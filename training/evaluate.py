# evaluate.py — AI MATE 80:20 훈련/테스트 분할 + 연구 검증
# 사용법: python evaluate.py
#
# 수행 내용:
#   1. DB에서 사전-사후 진단 데이터 로드
#   2. 80% 훈련셋(기술 통계) / 20% 테스트셋(예측 검증)
#   3. 대응표본 t-검정 (사전 vs 사후)
#   4. 요인별 향상도 분석
#   5. 롤모델 매칭 정확도
#   6. 결과를 CSV + 터미널 리포트로 출력

import os, sqlite3, json, csv, io
import random
from datetime import datetime

# ── 선택적 import (없으면 기본 통계로 대체) ──
try:
    import numpy as np
    from scipy import stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    print("⚠️  scipy 없음 → 기본 통계로 대체 (pip install scipy)")

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    HAS_PLT = True
except ImportError:
    HAS_PLT = False

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aiMate.db")
OUT_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eval_output")
os.makedirs(OUT_DIR, exist_ok=True)

random.seed(42)   # 재현 가능한 분할


# ══════════════════════════════════════════════════════════
# 1. 데이터 로드
# ══════════════════════════════════════════════════════════
def load_data():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # 사전 진단 (is_post=0, 가장 이른 것)
    pre_rows = conn.execute("""
        SELECT user_idx, behavior, natural_reward, constructive_thought, overall,
               role_model, issue
        FROM survey
        WHERE is_post = 0
        GROUP BY user_idx
        HAVING MIN(created_at)
        ORDER BY user_idx
    """).fetchall()

    # 사후 진단 (is_post=1, 가장 최근 것)
    post_rows = conn.execute("""
        SELECT user_idx, behavior, natural_reward, constructive_thought, overall,
               role_model
        FROM survey
        WHERE is_post = 1
        GROUP BY user_idx
        HAVING MAX(created_at)
        ORDER BY user_idx
    """).fetchall()

    conn.close()

    # user_idx 기준으로 매칭 (사전+사후 모두 있는 사용자)
    pre_dict  = {r["user_idx"]: dict(r) for r in pre_rows}
    post_dict = {r["user_idx"]: dict(r) for r in post_rows}
    paired_ids = sorted(set(pre_dict) & set(post_dict))

    paired = []
    for uid in paired_ids:
        p = pre_dict[uid]
        q = post_dict[uid]
        paired.append({
            "user_idx":        uid,
            "pre_behavior":    p["behavior"],
            "pre_natural":     p["natural_reward"],
            "pre_thought":     p["constructive_thought"],
            "pre_overall":     p["overall"],
            "post_behavior":   q["behavior"],
            "post_natural":    q["natural_reward"],
            "post_thought":    q["constructive_thought"],
            "post_overall":    q["overall"],
            "diff_overall":    round(q["overall"] - p["overall"], 2),
            "diff_behavior":   round(q["behavior"] - p["behavior"], 2),
            "diff_natural":    round(q["natural_reward"] - p["natural_reward"], 2),
            "diff_thought":    round(q["constructive_thought"] - p["constructive_thought"], 2),
            "role_model":      p["role_model"],
            "issue":           p["issue"],
        })

    return paired


# ══════════════════════════════════════════════════════════
# 2. 80:20 분할
# ══════════════════════════════════════════════════════════
def split_8020(data):
    shuffled = data.copy()
    random.shuffle(shuffled)
    cut = int(len(shuffled) * 0.8)
    return shuffled[:cut], shuffled[cut:]


# ══════════════════════════════════════════════════════════
# 3. 기술 통계
# ══════════════════════════════════════════════════════════
def mean(vals):
    return sum(vals) / len(vals) if vals else 0.0

def std(vals):
    if len(vals) < 2: return 0.0
    m = mean(vals)
    return (sum((x-m)**2 for x in vals) / (len(vals)-1)) ** 0.5

def describe(vals, label=""):
    n = len(vals); m = mean(vals); s = std(vals)
    mn = min(vals); mx = max(vals)
    return {"label":label, "n":n, "mean":round(m,3), "std":round(s,3),
            "min":round(mn,3), "max":round(mx,3)}


# ══════════════════════════════════════════════════════════
# 4. 대응표본 t-검정
# ══════════════════════════════════════════════════════════
def paired_t(pre_vals, post_vals, label=""):
    diffs = [p-q for p,q in zip(post_vals, pre_vals)]   # post - pre
    n  = len(diffs); m  = mean(diffs); s  = std(diffs)
    if s == 0:
        return {"label":label, "n":n, "mean_diff":round(m,3), "t":0.0, "p":1.0,
                "significant":False, "cohen_d":0.0}

    if HAS_SCIPY:
        import numpy as np
        t_val, p_val = stats.ttest_rel(post_vals, pre_vals)
        cohen_d = float(np.mean(diffs) / np.std(diffs, ddof=1))
    else:
        import math
        t_val = m / (s / math.sqrt(n))
        # 간이 p-value 추정 (df=n-1, 양측)
        df = n - 1
        # t > 2.0 → p < 0.05 근사
        p_val = 0.01 if abs(t_val) > 2.576 else (0.04 if abs(t_val) > 1.96 else 0.1)
        cohen_d = m / s

    return {"label":label, "n":n, "mean_diff":round(m,3), "t":round(float(t_val),3),
            "p":round(float(p_val),4), "significant": float(p_val) < 0.05,
            "cohen_d":round(float(cohen_d),3)}


# ══════════════════════════════════════════════════════════
# 5. 롤모델 매칭 '정확도' (취약 요인과 일치율)
# ══════════════════════════════════════════════════════════
ROLE_FACTOR_MAP = {
    "마리 퀴리":"behavior", "이순신":"behavior",
    "벤자민 프랭클린":"behavior", "김만덕":"behavior",
    "프리다 칼로":"natural", "윤동주":"natural",
    "리처드 파인만":"natural", "레이첼 카슨":"natural",
    "헬렌 켈러":"thought", "넬슨 만델라":"thought",
    "루스 베이더 긴즈버그":"thought", "플로렌스 나이팅게일":"thought",
}

def lowest_factor(row, prefix="pre_"):
    scores = {k: row[prefix+k] for k in ["behavior","natural","thought"]}
    return min(scores, key=scores.get)

def role_model_accuracy(data):
    correct = 0
    for row in data:
        rm = row["role_model"]
        expected_factor = lowest_factor(row, "pre_")
        actual_factor   = ROLE_FACTOR_MAP.get(rm, "unknown")
        if actual_factor == expected_factor:
            correct += 1
    return round(correct / len(data) * 100, 1) if data else 0.0


# ══════════════════════════════════════════════════════════
# 6. 향상 예측 정확도 (훈련셋 기준 임계값으로 테스트셋 예측)
# ══════════════════════════════════════════════════════════
def improvement_accuracy(train, test):
    """
    훈련셋: 사전 점수 → 사후 향상 여부(+) 학습 (평균 향상 임계값)
    테스트셋: 같은 임계값으로 예측 → 실제와 비교
    """
    # 훈련셋에서 임계값 계산 (평균 사전 점수 기준)
    train_pre = [r["pre_overall"] for r in train]
    threshold = mean(train_pre)

    # 테스트셋 예측: 사전 점수 < 임계값이면 향상 예측
    correct = 0
    for row in test:
        predicted_improve = row["pre_overall"] < threshold
        actual_improve    = row["diff_overall"] > 0
        if predicted_improve == actual_improve:
            correct += 1

    return round(correct / len(test) * 100, 1) if test else 0.0


# ══════════════════════════════════════════════════════════
# 7. 그래프 출력
# ══════════════════════════════════════════════════════════
def save_plots(train, test, all_data):
    if not HAS_PLT:
        print("  ⚠️  matplotlib 없음 → 그래프 스킵")
        return

    # 한글 폰트 설정
    try:
        font_candidates = [
            "NanumGothic", "AppleGothic", "Malgun Gothic",
            "NanumBarunGothic", "DejaVu Sans",
        ]
        available = [f.name for f in fm.fontManager.ttflist]
        chosen = next((f for f in font_candidates if f in available), None)
        if chosen:
            plt.rcParams["font.family"] = chosen
    except Exception:
        pass
    plt.rcParams["axes.unicode_minus"] = False

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    fig.suptitle("AI MATE 80:20 훈련/테스트 분석 리포트", fontsize=14, fontweight="bold", y=0.98)

    factors = ["behavior","natural","thought"]
    factor_labels = ["행동중심전략","자연적 보상전략","건설적 사고패턴전략"]
    colors = ["#2a6658","#b8870a","#c25a3d"]

    # ── 그래프 1: 훈련셋 사전-사후 평균 비교 ──
    ax = axes[0][0]
    pre_means  = [mean([r[f"pre_{f}"]  for r in train]) for f in factors]
    post_means = [mean([r[f"post_{f}"] for r in train]) for f in factors]
    x = range(len(factors))
    w = 0.35
    ax.bar([i-w/2 for i in x], pre_means,  w, label="사전", color=["#aed4cc","#e8c97a","#e8a090"])
    ax.bar([i+w/2 for i in x], post_means, w, label="사후", color=["#2a6658","#b8870a","#c25a3d"])
    ax.set_xticks(list(x)); ax.set_xticklabels(factor_labels, fontsize=8)
    ax.set_ylim(0, 5.5); ax.set_title("훈련셋 요인별 사전-사후 평균 (n={}명)".format(len(train)))
    ax.legend(fontsize=8); ax.set_ylabel("점수")

    # ── 그래프 2: 테스트셋 향상도 분포 ──
    ax2 = axes[0][1]
    diffs = [r["diff_overall"] for r in test]
    ax2.hist(diffs, bins=12, color="#5a3d8a", alpha=0.75, edgecolor="white")
    ax2.axvline(0, color="red", linestyle="--", linewidth=1.2, label="변화없음")
    ax2.axvline(mean(diffs), color="#2a6658", linestyle="-", linewidth=1.5,
                label=f"평균 +{mean(diffs):.2f}")
    ax2.set_title(f"테스트셋 전체 점수 향상도 분포 (n={len(test)}명)")
    ax2.set_xlabel("사후-사전 점수 차이"); ax2.set_ylabel("인원 수")
    ax2.legend(fontsize=8)

    # ── 그래프 3: 전체 사전 점수 분포 ──
    ax3 = axes[1][0]
    pre_all = [r["pre_overall"] for r in all_data]
    ax3.hist(pre_all, bins=10, color="#2a6658", alpha=0.7, edgecolor="white")
    ax3.axvline(mean(pre_all), color="#c25a3d", linestyle="--", linewidth=1.5,
                label=f"평균 {mean(pre_all):.2f}")
    ax3.set_title(f"전체 사전 진단 점수 분포 (n={len(all_data)}명)")
    ax3.set_xlabel("전체 점수"); ax3.set_ylabel("인원 수")
    ax3.legend(fontsize=8)

    # ── 그래프 4: 요인별 향상도 (전체) ──
    ax4 = axes[1][1]
    factor_diffs = [
        mean([r["diff_behavior"] for r in all_data]),
        mean([r["diff_natural"]  for r in all_data]),
        mean([r["diff_thought"]  for r in all_data]),
    ]
    bars = ax4.bar(factor_labels, factor_diffs, color=colors, alpha=0.85, edgecolor="white")
    ax4.axhline(0, color="black", linewidth=0.8)
    ax4.set_title("요인별 평균 향상도 (전체)")
    ax4.set_ylabel("사후-사전 차이")
    for bar, val in zip(bars, factor_diffs):
        ax4.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.02,
                 f"{val:+.2f}", ha="center", va="bottom", fontsize=9, fontweight="bold")

    plt.tight_layout()
    fig_path = os.path.join(OUT_DIR, "eval_report.png")
    plt.savefig(fig_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  📊 그래프 저장: {fig_path}")


# ══════════════════════════════════════════════════════════
# 8. CSV 저장
# ══════════════════════════════════════════════════════════
def save_csv(train, test, t_results):
    # 분할 결과
    split_path = os.path.join(OUT_DIR, "split_data.csv")
    fields = ["split","user_idx","pre_overall","post_overall","diff_overall",
              "diff_behavior","diff_natural","diff_thought","role_model","issue"]
    with open(split_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in train: w.writerow({"split":"train", **r})
        for r in test:  w.writerow({"split":"test",  **r})

    # t-검정 결과
    ttest_path = os.path.join(OUT_DIR, "ttest_results.csv")
    tfields = ["label","n","mean_diff","t","p","significant","cohen_d"]
    with open(ttest_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=tfields)
        w.writeheader()
        for r in t_results: w.writerow(r)

    print(f"  📄 데이터 CSV: {split_path}")
    print(f"  📄 t-검정 CSV: {ttest_path}")


# ══════════════════════════════════════════════════════════
# 메인
# ══════════════════════════════════════════════════════════
def main():
    print("\n" + "="*60)
    print("  AI MATE 80:20 훈련/테스트 분할 분석")
    print("="*60)

    if not os.path.exists(DB_PATH):
        print("❌ aiMate.db 파일 없음. 먼저 앱 실행 후 seed_data.py를 실행하세요.")
        return

    # ── 데이터 로드 ──
    all_data = load_data()
    n = len(all_data)
    print(f"\n📥 로드된 사전-사후 쌍 데이터: {n}명")
    if n < 10:
        print("❌ 분석에 필요한 최소 데이터(10명)가 부족합니다.")
        return

    # ── 80:20 분할 ──
    train, test = split_8020(all_data)
    print(f"\n🔀 80:20 분할 결과")
    print(f"   훈련셋 (Train): {len(train)}명  ({len(train)/n*100:.0f}%)")
    print(f"   테스트셋 (Test): {len(test)}명   ({len(test)/n*100:.0f}%)")

    # ── 기술 통계 ──
    print(f"\n{'─'*60}")
    print("📊 [훈련셋] 기술 통계")
    print(f"{'─'*60}")
    for label, key in [("전체 점수(사전)", "pre_overall"), ("전체 점수(사후)", "post_overall"),
                        ("향상도(사후-사전)", "diff_overall")]:
        d = describe([r[key] for r in train], label)
        sig = "⭐" if key=="diff_overall" and d["mean"]>0 else ""
        print(f"  {label:<18} 평균={d['mean']:.3f}  표준편차={d['std']:.3f}"
              f"  범위=[{d['min']:.1f}~{d['max']:.1f}] {sig}")

    print(f"\n📊 [테스트셋] 기술 통계")
    print(f"{'─'*60}")
    for label, key in [("전체 점수(사전)", "pre_overall"), ("전체 점수(사후)", "post_overall"),
                        ("향상도(사후-사전)", "diff_overall")]:
        d = describe([r[key] for r in test], label)
        print(f"  {label:<18} 평균={d['mean']:.3f}  표준편차={d['std']:.3f}"
              f"  범위=[{d['min']:.1f}~{d['max']:.1f}]")

    # ── t-검정 ──
    t_results = []
    print(f"\n{'─'*60}")
    print("📐 대응표본 t-검정 (사전 vs 사후)")
    print(f"{'─'*60}")
    for dataset_name, dataset in [("훈련셋", train), ("테스트셋", test), ("전체", all_data)]:
        for factor_key, factor_name in [
            ("overall", "전체 점수"),
            ("behavior", "행동중심전략"),
            ("natural",  "자연적 보상전략"),
            ("thought",  "건설적 사고패턴전략"),
        ]:
            pre_vals  = [r[f"pre_{factor_key}"]  for r in dataset]
            post_vals = [r[f"post_{factor_key}"] for r in dataset]
            result = paired_t(pre_vals, post_vals, f"{dataset_name}_{factor_name}")
            t_results.append(result)

            if dataset_name != "전체":
                sig_mark = "✅ 유의" if result["significant"] else "❌ 비유의"
                print(f"  [{dataset_name}] {factor_name:<14}  "
                      f"평균향상={result['mean_diff']:+.3f}  "
                      f"t={result['t']:.3f}  p={result['p']:.4f}  "
                      f"d={result['cohen_d']:.3f}  {sig_mark}")

    # ── 전체 요약 ──
    all_t = [r for r in t_results if r["label"].startswith("전체")]
    print(f"\n{'─'*60}")
    print("📋 전체 데이터 t-검정 요약")
    print(f"{'─'*60}")
    for r in all_t:
        lbl = r["label"].replace("전체_","")
        sig_mark = "✅ 유의 (p<0.05)" if r["significant"] else "❌ 비유의"
        eff = "큰 효과" if abs(r["cohen_d"])>=0.8 else "중간 효과" if abs(r["cohen_d"])>=0.5 else "작은 효과"
        print(f"  {lbl:<16}  향상 {r['mean_diff']:+.3f}점  "
              f"t({r['n']-1})={r['t']:.3f}  p={r['p']:.4f}  "
              f"Cohen's d={r['cohen_d']:.3f} ({eff})  {sig_mark}")

    # ── 롤모델 매칭 정확도 ──
    train_acc = role_model_accuracy(train)
    test_acc  = role_model_accuracy(test)
    print(f"\n{'─'*60}")
    print("🎯 롤모델 매칭 정확도 (취약 요인 일치율)")
    print(f"{'─'*60}")
    print(f"  훈련셋:  {train_acc}%")
    print(f"  테스트셋: {test_acc}%")

    # ── 향상 예측 정확도 ──
    pred_acc = improvement_accuracy(train, test)
    print(f"\n{'─'*60}")
    print("🔮 향상 예측 정확도 (훈련셋 임계값 → 테스트셋 예측)")
    print(f"{'─'*60}")
    print(f"  테스트셋 예측 정확도: {pred_acc}%")
    print(f"  (사전 점수가 훈련셋 평균 이하면 향상 예측)")

    # ── 그래프 & CSV 저장 ──
    print(f"\n{'─'*60}")
    print("💾 결과 파일 저장 중...")
    save_plots(train, test, all_data)
    save_csv(train, test, t_results)

    # ── 최종 결론 ──
    overall_result = next(r for r in t_results if r["label"] == "전체_전체 점수")
    print(f"\n{'='*60}")
    print("✅ 최종 결론 요약")
    print(f"{'='*60}")
    print(f"  전체 대상자: {n}명 → 훈련 {len(train)}명 / 테스트 {len(test)}명")
    print(f"  전체 평균 향상도: {overall_result['mean_diff']:+.3f}점")
    if overall_result["significant"]:
        d = abs(overall_result["cohen_d"])
        eff = "큰" if d>=0.8 else "중간" if d>=0.5 else "작은"
        print(f"  통계적 유의성: ✅ 유의미 (p={overall_result['p']:.4f})")
        print(f"  효과 크기: Cohen's d={overall_result['cohen_d']:.3f} ({eff} 효과)")
        print(f"  🎉 AI MATE 플랫폼이 셀프리더십 향상에 유의미한 효과가 있습니다!")
    else:
        print(f"  통계적 유의성: ❌ 비유의 (p={overall_result['p']:.4f})")
        print(f"  ※ 실제 연구에서는 표본 크기를 늘리거나 처치 기간을 연장하세요.")
    print(f"\n  출력 폴더: {OUT_DIR}/")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
