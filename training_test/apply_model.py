# apply_model.py — AI MATE 훈련셋/테스트셋 실제 적용
# =============================================================
#
#  방법 1. 점수 예측 모델 (선형 회귀)
#          훈련셋으로 "사전 점수 → 사후 점수" 예측 수식 학습
#          테스트셋으로 예측 정확도 검증
#
#  방법 2. 롤모델 최적 추천 모델 (분류)
#          훈련셋으로 "어떤 요인이 약할 때 어떤 롤모델이 효과적?"
#          학습 → 테스트셋에서 예측
#
#  방법 3. 시스템 프롬프트 자동 최적화
#          훈련셋 패턴 분석 → Claude API 시스템 프롬프트 개선
#          테스트셋으로 프롬프트 품질 비교
#
#  사용법: python apply_model.py
# =============================================================

import os, sqlite3, json, csv, random, math
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aiMate.db")
OUT_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apply_output")
os.makedirs(OUT_DIR, exist_ok=True)

random.seed(42)

# ─────────────────────────────────────────────────
# 유틸 함수
# ─────────────────────────────────────────────────
def mean(vals):
    return sum(vals)/len(vals) if vals else 0.0

def std(vals):
    if len(vals) < 2: return 0.0
    m = mean(vals)
    return (sum((x-m)**2 for x in vals)/(len(vals)-1))**0.5

def rmse(actual, predicted):
    return math.sqrt(mean([(a-p)**2 for a,p in zip(actual,predicted)]))

def mae(actual, predicted):
    return mean([abs(a-p) for a,p in zip(actual,predicted)])

def accuracy(actual, predicted):
    correct = sum(1 for a,p in zip(actual,predicted) if a==p)
    return round(correct/len(actual)*100, 1)


# ─────────────────────────────────────────────────
# 데이터 로드 (사전-사후 쌍)
# ─────────────────────────────────────────────────
def load_data():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row

    pre_rows = conn.execute("""
        SELECT user_idx, behavior, natural_reward, constructive_thought,
               overall, role_model, issue
        FROM survey WHERE is_post=0
        GROUP BY user_idx HAVING MIN(created_at)
    """).fetchall()

    post_rows = conn.execute("""
        SELECT user_idx, behavior, natural_reward, constructive_thought,
               overall, role_model
        FROM survey WHERE is_post=1
        GROUP BY user_idx HAVING MAX(created_at)
    """).fetchall()

    conn.close()

    pre  = {r["user_idx"]: dict(r) for r in pre_rows}
    post = {r["user_idx"]: dict(r) for r in post_rows}
    paired = []
    for uid in sorted(set(pre) & set(post)):
        p, q = pre[uid], post[uid]
        paired.append({
            "user_idx":     uid,
            "pre_behavior": p["behavior"],
            "pre_natural":  p["natural_reward"],
            "pre_thought":  p["constructive_thought"],
            "pre_overall":  p["overall"],
            "post_behavior":q["behavior"],
            "post_natural": q["natural_reward"],
            "post_thought": q["constructive_thought"],
            "post_overall": q["overall"],
            "diff":         round(q["overall"]-p["overall"], 2),
            "role_model":   p["role_model"],
            "issue":        p["issue"],
            # 취약 요인 레이블
            "lowest":       min(
                {"behavior":p["behavior"],
                 "natural":p["natural_reward"],
                 "thought":p["constructive_thought"]},
                key=lambda k: {"behavior":p["behavior"],
                               "natural":p["natural_reward"],
                               "thought":p["constructive_thought"]}[k]
            ),
        })
    return paired


def split(data, ratio=0.8):
    s = data.copy(); random.shuffle(s)
    cut = int(len(s)*ratio)
    return s[:cut], s[cut:]


# ═══════════════════════════════════════════════════
# 방법 1. 선형 회귀 — 사전 점수로 사후 점수 예측
# ═══════════════════════════════════════════════════
class LinearRegression:
    """
    y = w0 + w1*x1 + w2*x2 + w3*x3
    (bias 포함 최소제곱법)
    """
    def __init__(self):
        self.weights = None   # [w0, w1, w2, w3]

    def fit(self, X, y):
        """X: [[x1,x2,x3], ...], y: [y1, y2, ...]"""
        # 바이어스 열 추가
        Xb = [[1.0]+row for row in X]
        n, m = len(Xb), len(Xb[0])

        # 정규 방정식: w = (X^T X)^{-1} X^T y
        XtX = [[sum(Xb[k][i]*Xb[k][j] for k in range(n))
                for j in range(m)] for i in range(m)]
        Xty = [sum(Xb[k][i]*y[k] for k in range(n)) for i in range(m)]
        self.weights = _solve(XtX, Xty)

    def predict(self, X):
        return [sum(self.weights[j]*(1.0 if j==0 else row[j-1])
                    for j in range(len(self.weights)))
                for row in X]


def _solve(A, b):
    """가우스 소거법 (단순 선형 연립방정식 풀기)"""
    n = len(b)
    M = [A[i][:]+[b[i]] for i in range(n)]  # 증강 행렬

    for col in range(n):
        # 피벗 찾기
        pivot = max(range(col, n), key=lambda r: abs(M[r][col]))
        M[col], M[pivot] = M[pivot], M[col]
        if abs(M[col][col]) < 1e-12: continue
        for row in range(n):
            if row != col:
                factor = M[row][col] / M[col][col]
                M[row] = [M[row][j] - factor*M[col][j] for j in range(n+1)]

    return [M[i][n]/M[i][i] for i in range(n)]


def run_regression(train, test):
    print("\n" + "="*60)
    print("  방법 1. 선형 회귀 — 사전 점수 → 사후 점수 예측")
    print("="*60)

    # 훈련
    X_tr = [[r["pre_behavior"], r["pre_natural"], r["pre_thought"]] for r in train]
    y_tr = [r["post_overall"] for r in train]
    model = LinearRegression()
    model.fit(X_tr, y_tr)
    w = model.weights
    print(f"\n[학습된 수식]")
    print(f"  사후점수 = {w[0]:.3f}")
    print(f"           + {w[1]:.3f} × 행동중심전략(사전)")
    print(f"           + {w[2]:.3f} × 자연적보상전략(사전)")
    print(f"           + {w[3]:.3f} × 건설적사고패턴(사전)")
    print(f"\n  해석: 행동중심전략 1점 향상 → 사후 전체점수 {w[1]:.3f}점 기여")

    # 훈련셋 성능
    y_tr_pred = model.predict(X_tr)
    print(f"\n[훈련셋 성능] (n={len(train)}명)")
    print(f"  RMSE = {rmse(y_tr, y_tr_pred):.4f}  (낮을수록 좋음)")
    print(f"  MAE  = {mae(y_tr, y_tr_pred):.4f}  (평균 오차)")

    # 테스트셋 성능
    X_te = [[r["pre_behavior"], r["pre_natural"], r["pre_thought"]] for r in test]
    y_te = [r["post_overall"] for r in test]
    y_te_pred = model.predict(X_te)
    print(f"\n[테스트셋 성능] (n={len(test)}명) ← 핵심: 새 데이터 예측력")
    print(f"  RMSE = {rmse(y_te, y_te_pred):.4f}")
    print(f"  MAE  = {mae(y_te, y_te_pred):.4f}")

    # 개별 예측 결과
    print(f"\n[테스트셋 개별 예측 결과]")
    print(f"  {'사용자':<8} {'실제 사후':<10} {'예측 사후':<10} {'오차':<8}")
    print(f"  {'-'*36}")
    for i, (r, pred) in enumerate(zip(test, y_te_pred)):
        diff = r["post_overall"] - pred
        print(f"  {r['user_idx']:<8} {r['post_overall']:<10.2f} {pred:<10.2f} {diff:+.2f}")

    # CSV 저장
    csv_path = os.path.join(OUT_DIR, "regression_predictions.csv")
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        w2 = csv.writer(f)
        w2.writerow(["split","user_idx","actual_post","predicted_post",
                     "error","pre_behavior","pre_natural","pre_thought"])
        for r, pred in zip(train, model.predict(X_tr)):
            w2.writerow(["train", r["user_idx"], r["post_overall"],
                         round(pred,3), round(r["post_overall"]-pred,3),
                         r["pre_behavior"], r["pre_natural"], r["pre_thought"]])
        for r, pred in zip(test, y_te_pred):
            w2.writerow(["test", r["user_idx"], r["post_overall"],
                         round(pred,3), round(r["post_overall"]-pred,3),
                         r["pre_behavior"], r["pre_natural"], r["pre_thought"]])
    print(f"\n  📄 저장: {csv_path}")
    return model, w


# ═══════════════════════════════════════════════════
# 방법 2. k-최근접 이웃(kNN) — 최적 롤모델 추천
# ═══════════════════════════════════════════════════
ROLE_FACTOR = {
    "마리 퀴리":"behavior",      "이순신":"behavior",
    "벤자민 프랭클린":"behavior", "김만덕":"behavior",
    "프리다 칼로":"natural",     "윤동주":"natural",
    "리처드 파인만":"natural",    "레이첼 카슨":"natural",
    "헬렌 켈러":"thought",       "넬슨 만델라":"thought",
    "루스 베이더 긴즈버그":"thought","플로렌스 나이팅게일":"thought",
}
FACTOR_LABELS = {"behavior":"행동중심","natural":"자연적보상","thought":"건설적사고"}


class KNN:
    """
    k-최근접 이웃 분류기
    입력: 사전 3요인 점수
    출력: 향상에 가장 효과적인 요인 (취약 요인 기반)
    """
    def __init__(self, k=5):
        self.k = k
        self.X_train = []
        self.y_train = []

    def fit(self, X, y):
        self.X_train = X; self.y_train = y

    def predict_one(self, x):
        dists = []
        for i, xt in enumerate(self.X_train):
            d = math.sqrt(sum((a-b)**2 for a,b in zip(x,xt)))
            dists.append((d, self.y_train[i]))
        dists.sort(key=lambda t: t[0])
        k_labels = [t[1] for t in dists[:self.k]]
        return max(set(k_labels), key=k_labels.count)

    def predict(self, X):
        return [self.predict_one(x) for x in X]


def run_knn(train, test):
    print("\n" + "="*60)
    print("  방법 2. kNN — 취약 요인 예측 → 최적 롤모델 추천")
    print("="*60)

    # 훈련: 사전 3요인 점수 → 실제 취약 요인
    X_tr = [[r["pre_behavior"], r["pre_natural"], r["pre_thought"]] for r in train]
    y_tr = [r["lowest"] for r in train]
    knn = KNN(k=5)
    knn.fit(X_tr, y_tr)

    # 훈련셋 정확도
    y_tr_pred = knn.predict(X_tr)
    tr_acc = accuracy(y_tr, y_tr_pred)
    print(f"\n[훈련셋 취약 요인 예측 정확도] (n={len(train)}명): {tr_acc}%")

    # 테스트셋 정확도
    X_te = [[r["pre_behavior"], r["pre_natural"], r["pre_thought"]] for r in test]
    y_te = [r["lowest"] for r in test]
    y_te_pred = knn.predict(X_te)
    te_acc = accuracy(y_te, y_te_pred)
    print(f"[테스트셋 취약 요인 예측 정확도] (n={len(test)}명): {te_acc}%")

    # 롤모델 추천 예시
    print(f"\n[테스트셋 롤모델 추천 결과]")
    RECOMMENDED = {
        "behavior": "마리 퀴리 또는 이순신",
        "natural":  "프리다 칼로 또는 윤동주",
        "thought":  "헬렌 켈러 또는 넬슨 만델라",
    }
    print(f"  {'사용자':<8} {'예측 취약요인':<16} {'실제 취약요인':<16} {'추천 롤모델':<24} {'일치'}")
    print(f"  {'-'*72}")
    for r, pred in zip(test, y_te_pred):
        match = "✅" if pred==r["lowest"] else "❌"
        print(f"  {r['user_idx']:<8} {FACTOR_LABELS[pred]:<16} "
              f"{FACTOR_LABELS[r['lowest']]:<16} "
              f"{RECOMMENDED[pred]:<24} {match}")

    # 혼동 행렬
    print(f"\n[혼동 행렬 (테스트셋)]")
    labels = ["behavior","natural","thought"]
    print(f"  {'':14}", end="")
    for l in labels: print(f"{FACTOR_LABELS[l]:<14}", end="")
    print("← 예측")
    for true in labels:
        print(f"  {FACTOR_LABELS[true]:<14}", end="")
        for pred in labels:
            cnt = sum(1 for a,p in zip(y_te,y_te_pred) if a==true and p==pred)
            print(f"{cnt:<14}", end="")
        print()
    print("↑ 실제")

    # CSV 저장
    csv_path = os.path.join(OUT_DIR, "knn_recommendations.csv")
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["split","user_idx","pre_behavior","pre_natural","pre_thought",
                    "actual_lowest","predicted_lowest","matched","recommended_rolemodel"])
        for r, pred in zip(train, y_tr_pred):
            w.writerow(["train",r["user_idx"],r["pre_behavior"],r["pre_natural"],
                        r["pre_thought"],r["lowest"],pred,r["lowest"]==pred,
                        RECOMMENDED[pred]])
        for r, pred in zip(test, y_te_pred):
            w.writerow(["test",r["user_idx"],r["pre_behavior"],r["pre_natural"],
                        r["pre_thought"],r["lowest"],pred,r["lowest"]==pred,
                        RECOMMENDED[pred]])
    print(f"\n  📄 저장: {csv_path}")
    return knn


# ═══════════════════════════════════════════════════
# 방법 3. 프롬프트 최적화 — 훈련셋 패턴 → 시스템 프롬프트 생성
# ═══════════════════════════════════════════════════
def run_prompt_optimization(train, test):
    print("\n" + "="*60)
    print("  방법 3. 프롬프트 최적화 — 훈련셋 패턴 기반")
    print("="*60)

    # 훈련셋에서 패턴 추출
    by_factor = {"behavior":[], "natural":[], "thought":[]}
    for r in train:
        by_factor[r["lowest"]].append(r["diff"])

    print(f"\n[훈련셋에서 학습한 요인별 향상 패턴]")
    factor_insights = {}
    for fk, diffs in by_factor.items():
        if not diffs: continue
        avg = mean(diffs); sd = std(diffs)
        hi = [r for r in train if r["lowest"]==fk and r["diff"] >= avg+0.3]
        factor_insights[fk] = {
            "avg_improvement": avg,
            "std": sd,
            "high_improvers": len(hi),
            "total": len(diffs)
        }
        print(f"  {FACTOR_LABELS[fk]:<14} 평균향상 +{avg:.3f}점  표준편차 {sd:.3f}  "
              f"고향상자 {len(hi)}/{len(diffs)}명")

    # 고향상자 공통 패턴 분석
    print(f"\n[고향상자 공통 특성 분석] (평균 대비 +0.3점 이상)")
    for fk in ["behavior","natural","thought"]:
        hi_group = [r for r in train if r["lowest"]==fk and r["diff"] >= factor_insights.get(fk,{}).get("avg_improvement",0)+0.3]
        lo_group = [r for r in train if r["lowest"]==fk and r["diff"] < factor_insights.get(fk,{}).get("avg_improvement",0)]
        if hi_group and lo_group:
            hi_pre = mean([r["pre_overall"] for r in hi_group])
            lo_pre = mean([r["pre_overall"] for r in lo_group])
            print(f"\n  [{FACTOR_LABELS[fk]}]")
            print(f"    고향상자 사전 평균: {hi_pre:.2f}점  |  저향상자 사전 평균: {lo_pre:.2f}점")
            if hi_pre < lo_pre:
                print(f"    → 사전 점수가 낮을수록 향상폭이 크다 (바닥 효과)")
            else:
                print(f"    → 사전 점수가 높아도 추가 향상 가능")

    # 최적화된 시스템 프롬프트 생성
    print(f"\n[생성된 최적화 시스템 프롬프트]")
    prompts = {}
    for fk in ["behavior","natural","thought"]:
        insight = factor_insights.get(fk, {})
        avg = insight.get("avg_improvement", 0.5)
        hi_rate = insight.get("high_improvers",0) / max(insight.get("total",1),1) * 100
        factor_name = FACTOR_LABELS[fk]
        if fk == "behavior":
            coaching_tip = "오늘 당장 15분 안에 실행할 수 있는 가장 작은 행동 1가지를 구체적으로 제안하세요."
        elif fk == "natural":
            coaching_tip = "현재 과업에서 의미와 흥미를 찾는 질문을 3가지 던지고, 사용자가 스스로 답하게 유도하세요."
        else:
            coaching_tip = "현재 상황을 '배움의 기회'로 재해석하는 긍정적 언어로 사용자의 자기대화를 전환시켜 주세요."

        prompt = f"""
당신은 [{factor_name}] 향상 전문 AI 코칭 롤모델입니다.

[훈련 데이터 기반 인사이트]
- 이 요인이 취약한 사용자의 평균 향상도: +{avg:.2f}점
- 고향상자 비율: {hi_rate:.0f}%

[최적 코칭 전략]
1. 공감: 사용자의 현재 어려움을 2문장 이내로 반영
2. 전환: {coaching_tip}
3. 실행: 오늘 밤 잠들기 전 완수 가능한 과제 1가지 제시

[제약]
- 응답은 4~6문장 이내
- 판단이나 평가 없이 질문으로 사고 유도
- 한국어로 답변
""".strip()
        prompts[fk] = prompt
        print(f"\n  ─── {factor_name} ───")
        for line in prompt.split("\n")[:8]:
            print(f"  {line}")
        print(f"  ...")

    # 프롬프트 파일 저장
    prompt_path = os.path.join(OUT_DIR, "optimized_prompts.json")
    with open(prompt_path, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "train_size": len(train),
            "test_size": len(test),
            "factor_insights": factor_insights,
            "prompts": prompts
        }, f, ensure_ascii=False, indent=2)
    print(f"\n  📄 저장: {prompt_path}")
    return prompts


# ═══════════════════════════════════════════════════
# 방법 3-b. 최적화 프롬프트 실제 적용 함수 (app.py 연동용)
# ═══════════════════════════════════════════════════
def get_optimized_prompt(factor_key: str, prompt_file: str = None) -> str:
    """
    app.py의 get_ai_reply() 에서 호출하여 최적화된 프롬프트 사용.
    예시:
        from apply_model import get_optimized_prompt
        system = get_optimized_prompt(scores["lowest"])
    """
    if prompt_file is None:
        prompt_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "apply_output", "optimized_prompts.json"
        )
    if not os.path.exists(prompt_file):
        return ""   # 파일 없으면 빈 문자열 반환 (기존 프롬프트 사용)
    with open(prompt_file, encoding="utf-8") as f:
        data = json.load(f)
    return data["prompts"].get(factor_key, "")


# ═══════════════════════════════════════════════════
# 방법 4. 예측 결과를 DB에 기록 (실시간 활용)
# ═══════════════════════════════════════════════════
def save_predictions_to_db(test, reg_model, knn_model):
    """
    테스트셋 예측 결과를 predictions 테이블에 저장
    → 관리자 화면에서 예측 vs 실제 비교 가능
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_idx INTEGER,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            predicted_post_overall REAL,
            predicted_lowest_factor TEXT,
            actual_post_overall REAL,
            error REAL
        )
    """)
    X_te = [[r["pre_behavior"], r["pre_natural"], r["pre_thought"]] for r in test]
    reg_preds = reg_model.predict(X_te)
    knn_preds = knn_model.predict(X_te)

    for r, reg_p, knn_p in zip(test, reg_preds, knn_preds):
        conn.execute("""
            INSERT INTO predictions
            (user_idx, predicted_post_overall, predicted_lowest_factor,
             actual_post_overall, error)
            VALUES (?,?,?,?,?)
        """, (r["user_idx"], round(reg_p, 3), knn_p,
              r["post_overall"], round(r["post_overall"]-reg_p, 3)))
    conn.commit(); conn.close()
    print(f"\n  💾 DB predictions 테이블에 {len(test)}건 저장 완료")


# ═══════════════════════════════════════════════════
# 메인
# ═══════════════════════════════════════════════════
def main():
    print("\n" + "="*60)
    print("  AI MATE 훈련셋/테스트셋 실제 적용")
    print("="*60)

    if not os.path.exists(DB_PATH):
        print("❌ aiMate.db 없음. seed_data.py 먼저 실행하세요.")
        return

    data = load_data()
    print(f"\n📥 사전-사후 쌍 데이터: {len(data)}명")

    train, test = split(data, 0.8)
    print(f"   훈련셋: {len(train)}명 | 테스트셋: {len(test)}명")

    # 방법 1: 선형 회귀
    reg_model, weights = run_regression(train, test)

    # 방법 2: kNN 롤모델 추천
    knn_model = run_knn(train, test)

    # 방법 3: 프롬프트 최적화
    prompts = run_prompt_optimization(train, test)

    # 방법 4: DB 저장
    print("\n" + "="*60)
    print("  방법 4. 예측 결과 DB 저장 (관리자 화면 연동)")
    print("="*60)
    save_predictions_to_db(test, reg_model, knn_model)

    # ── 최종 요약 ──
    print("\n" + "="*60)
    print("  ✅ 전체 요약 및 실제 활용 방법")
    print("="*60)
    print("""
  ┌─────────────────────────────────────────────────────┐
  │  모델          활용 위치          효과                 │
  ├─────────────────────────────────────────────────────┤
  │  선형 회귀     진단 결과 화면     "예상 향상점수 표시"    │
  │  kNN          롤모델 매칭        "최적 롤모델 추천"     │
  │  프롬프트최적화 AI 코칭 대화      "더 효과적인 코칭"     │
  │  predictions  관리자 대시보드    "예측 vs 실제 비교"    │
  └─────────────────────────────────────────────────────┘

  app.py에서 최적화 프롬프트 사용하는 방법:
  ─────────────────────────────────────────
  # logic.py의 get_ai_reply() 함수 안에 추가:

  from apply_model import get_optimized_prompt
  extra = get_optimized_prompt(scores["lowest"])
  if extra:
      system = extra + "\\n\\n" + system   # 최적화 프롬프트 앞에 추가
    """)
    print(f"  📁 출력 폴더: {OUT_DIR}/")
    print("="*60)


if __name__ == "__main__":
    main()
