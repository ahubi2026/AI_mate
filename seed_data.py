# seed_data.py — AI MATE 가상 데이터 생성기
# 사용법: python seed_data.py
# 결과: aiMate.db에 가상 사용자 100명 + 각 1~3회 진단 데이터 삽입

import sqlite3, os, hashlib, json, random
from datetime import datetime, timedelta

# ──────────────────────────────────────────────────────────
# DB 경로 설정 (이 파일과 같은 폴더의 aiMate.db)
# ──────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aiMate.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def _hash(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ──────────────────────────────────────────────────────────
# 가상 데이터 풀
# ──────────────────────────────────────────────────────────
FEMALE_NAMES = [
    "김지현","이수연","박민지","정유진","최서연","한소희","윤지은","임채원","오하은","서예린",
    "강다은","조현주","신지수","황민서","류하린","문소영","배나연","노지원","허수빈","양가연",
    "송미래","전지아","백서현","심유나","홍다인","추예지","마소율","변지혜","기나영","태하린",
    "도민경","가은솔","여지민","석소율","안채은","고나린","남지윤","진서아","우하영","석수아",
    "이나린","박채린","김소율","최나연","정다은","한지은","윤소희","임나현","오지은","서민지",
]
MALE_NAMES = [
    "김민준","이준혁","박서준","정도윤","최현우","한지호","윤성민","임재현","오승환","서동현",
    "강재원","조민혁","신준서","황성호","류지훈","문재인","배승우","노현준","허민준","양준혁",
    "송재훈","전민준","백준혁","심재원","홍성준","추민혁","마준서","변재현","기승민","태현준",
    "도재훈","가승호","여민준","석재현","안성민","고준혁","남재원","진민준","우재훈","석성호",
    "이준서","박민혁","김재원","최준혁","정성민","한재훈","윤민준","임준혁","오재현","서승호",
]
DOMAINS = ["gmail.com","naver.com","kakao.com","daum.net","hanmail.net","nate.com"]
ISSUES  = ["커리어","관계","학습","자기돌봄","전환기"]
TONES   = ["전략 코칭형","따뜻한 격려형","단호한 조언형","성찰 질문형"]
ROLES   = {
    "behavior": ["마리 퀴리","이순신","벤자민 프랭클린","김만덕"],
    "natural":  ["프리다 칼로","윤동주","리처드 파인만","레이첼 카슨"],
    "thought":  ["헬렌 켈러","넬슨 만델라","루스 베이더 긴즈버그","플로렌스 나이팅게일"],
}
QIDS = ["A1","A2","A3","B1","B2","B3","C1","C2","C3"]
FACTOR_MAP = {
    "A1":"behavior","A2":"behavior","A3":"behavior",
    "B1":"natural","B2":"natural","B3":"natural",
    "C1":"thought","C2":"thought","C3":"thought",
}

# 성별별 나이 분포 (한국 성인 여성 중심)
AGE_WEIGHTS = {
    (20,29): 25, (30,39): 30, (40,49): 25,
    (50,59): 12, (60,69): 5,  (15,19): 3,
}

REFLECTION_POOL = [
    "오늘 AI MATE와 대화하며 내가 미루던 일의 원인을 발견했다. 두려움이 아니라 습관의 문제였다.",
    "작은 실천 하나가 생각보다 큰 변화를 가져온다는 걸 느꼈다. 내일도 계속 해보겠다.",
    "자연적 보상 전략이 가장 약하다는 진단을 받았는데, 돌이켜보니 항상 결과만 보며 과정을 즐기지 못했던 것 같다.",
    "행동 중심 전략 점수가 낮게 나왔다. 목표를 세워도 실행하지 않는 패턴이 반복됐다. 오늘은 달랐다.",
    "성찰 일지를 쓰는 것 자체가 나에게 트리거가 됐다. 내 생각이 이렇게 구체화되는 경험은 처음이다.",
    "AI 코칭이 판단 없이 내 이야기를 들어준다는 느낌이 좋았다. 마음이 편안해졌다.",
    "넬슨 만델라 롤모델의 '긴 호흡으로 보기' 철학이 지금의 나에게 딱 필요한 메시지였다.",
    "마리 퀴리처럼 목표를 잘게 쪼개서 하루하루 검증해보기로 했다.",
    "프리다 칼로의 이야기에서 나의 경험이 에너지가 될 수 있다는 걸 새롭게 생각해봤다.",
    "오늘 실천과제: 내일 할 일 3가지 미리 적기. 생각보다 명확해져서 좋았다.",
    "스트레스를 배움의 기회로 재해석하는 연습을 했다. 처음엔 어색했지만 점점 자연스러워졌다.",
    "건설적 사고 패턴이 중요한 이유를 이제 체감했다. 머릿속 부정적 언어를 바꾸기만 해도 달라진다.",
    "2주 사용 후 사전보다 전체 점수가 0.8점 올랐다. 숫자보다 태도가 달라졌다는 게 더 크게 느껴진다.",
    "커리어 전환기에 이 플랫폼이 좋은 나침반이 됐다. 방향을 잡는 데 도움을 받았다.",
    "자기돌봄이 이기적인 게 아니라 지속가능한 성장의 기반이라는 걸 오늘 다시 확인했다.",
]
ACTIONS = [
    "내일 할 일 3가지 미리 적기",
    "10분 산책하며 오늘 하루 돌아보기",
    "미루던 이메일 1개 즉시 보내기",
    "지루한 업무에서 의미 한 가지 찾아 메모하기",
    "부정적 자기대화 하나를 긍정 문장으로 바꿔 쓰기",
    "내일 발표 전 5분 성공 시각화 연습",
    "오늘 잘한 일 2가지 일지에 기록하기",
    "업무 우선순위 리스트 작성하고 1개 완수",
    "스트레스 받은 상황 한 줄로 적고 재해석하기",
    "좋아하는 음악 들으며 10분 온전한 휴식",
]


def random_date(start_days_ago=90, end_days_ago=1):
    """최근 90일 이내 랜덤 날짜 생성"""
    delta = random.randint(end_days_ago, start_days_ago)
    return (datetime.now() - timedelta(days=delta)).strftime("%Y-%m-%d %H:%M:%S")


def pick_age():
    ranges = list(AGE_WEIGHTS.keys())
    weights = list(AGE_WEIGHTS.values())
    chosen = random.choices(ranges, weights=weights, k=1)[0]
    return random.randint(chosen[0], chosen[1])


def make_answers(profile="normal"):
    """
    profile: 'high' / 'normal' / 'low' / 'random'
    각 문항 1~5점 INTEGER 반환
    """
    base = {
        "high":   (3, 5),
        "normal": (2, 4),
        "low":    (1, 3),
        "random": (1, 5),
    }.get(profile, (2, 4))
    return {qid: random.randint(base[0], base[1]) for qid in QIDS}


def calc_scores_from_answers(answers):
    factors = {}
    for fk in ["behavior","natural","thought"]:
        ids  = [q for q,f in FACTOR_MAP.items() if f == fk]
        vals = [answers[q] for q in ids]
        factors[fk] = round(sum(vals)/len(vals), 1)
    overall = round(sum(factors.values())/3, 1)
    lowest  = min(factors, key=factors.get)
    return {**factors, "overall": overall, "lowest": lowest}


def make_phone():
    mid = random.randint(1000, 9999)
    end = random.randint(1000, 9999)
    return f"010-{mid}-{end}"


# ──────────────────────────────────────────────────────────
# 메인 생성 로직
# ──────────────────────────────────────────────────────────
def seed(n_users=100):
    conn = get_conn()
    cur  = conn.cursor()

    inserted_users   = 0
    inserted_surveys = 0
    inserted_journals = 0
    skipped = 0

    # 이름 풀 구성 (여성 70%, 남성 30%)
    all_female = FEMALE_NAMES * 3   # 150명분
    all_male   = MALE_NAMES   * 2   # 100명분
    random.shuffle(all_female)
    random.shuffle(all_male)

    used_emails = set()

    for i in range(n_users):
        # 성별 결정
        gender = "여" if random.random() < 0.70 else "남"
        name_pool = all_female if gender == "여" else all_male
        name = name_pool[i % len(name_pool)]

        # 이메일 생성 (중복 방지)
        domain = random.choice(DOMAINS)
        base_email = f"{name.lower().replace(' ','')}{random.randint(10,999)}@{domain}"
        if base_email in used_emails:
            base_email = f"user{i:04d}@{domain}"
        used_emails.add(base_email)

        age   = pick_age()
        phone = make_phone()

        # user 테이블 삽입
        try:
            reg_date = random_date(90, 20)
            cur.execute("""
                INSERT INTO user (id, pwd_hash, name, gender, age, phone, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (base_email, _hash("000000"), name, gender, age, phone, reg_date))
            user_idx = cur.lastrowid
            inserted_users += 1
        except sqlite3.IntegrityError:
            skipped += 1
            continue

        # 사용자 프로파일 결정 (나이·성별에 따라 다양화)
        if age < 25:
            profile_pre = random.choice(["low","normal","normal"])
        elif age < 40:
            profile_pre = random.choice(["normal","normal","high"])
        elif age < 55:
            profile_pre = random.choice(["normal","high","high"])
        else:
            profile_pre = random.choice(["low","normal","high"])

        issue = random.choice(ISSUES)
        tone  = random.choice(TONES)

        # ── 사전 진단 (is_post=0) ──
        pre_answers = make_answers(profile_pre)
        pre_scores  = calc_scores_from_answers(pre_answers)
        rm          = random.choice(ROLES[pre_scores["lowest"]])

        pre_date = random_date(60, 30)
        cur.execute("""
            INSERT INTO survey
            (user_idx, created_at, issue, tone, answers,
             behavior, natural_reward, constructive_thought, overall, role_model, is_post)
            VALUES (?,?,?,?,?,?,?,?,?,?,0)
        """, (user_idx, pre_date, issue, tone,
              json.dumps(pre_answers, ensure_ascii=False),
              pre_scores["behavior"], pre_scores["natural"],
              pre_scores["thought"], pre_scores["overall"], rm))
        inserted_surveys += 1

        # ── 중간 진단 (70% 확률) ──
        if random.random() < 0.70:
            mid_answers = make_answers("normal")
            mid_scores  = calc_scores_from_answers(mid_answers)
            mid_rm      = random.choice(ROLES[mid_scores["lowest"]])
            mid_date    = random_date(28, 15)
            cur.execute("""
                INSERT INTO survey
                (user_idx, created_at, issue, tone, answers,
                 behavior, natural_reward, constructive_thought, overall, role_model, is_post)
                VALUES (?,?,?,?,?,?,?,?,?,?,0)
            """, (user_idx, mid_date, issue, tone,
                  json.dumps(mid_answers, ensure_ascii=False),
                  mid_scores["behavior"], mid_scores["natural"],
                  mid_scores["thought"], mid_scores["overall"], mid_rm))
            inserted_surveys += 1

        # ── 사후 진단 (is_post=1, 80% 확률) ──
        if random.random() < 0.80:
            # 사후는 사전보다 0~1점 향상 경향
            post_answers = {
                qid: min(5, pre_answers[qid] + random.choices([0,0,1,1,2],weights=[10,20,35,25,10])[0])
                for qid in QIDS
            }
            post_scores = calc_scores_from_answers(post_answers)
            post_rm     = random.choice(ROLES[post_scores["lowest"]])
            post_date   = random_date(14, 1)
            cur.execute("""
                INSERT INTO survey
                (user_idx, created_at, issue, tone, answers,
                 behavior, natural_reward, constructive_thought, overall, role_model, is_post)
                VALUES (?,?,?,?,?,?,?,?,?,?,1)
            """, (user_idx, post_date, issue, tone,
                  json.dumps(post_answers, ensure_ascii=False),
                  post_scores["behavior"], post_scores["natural"],
                  post_scores["thought"], post_scores["overall"], post_rm))
            inserted_surveys += 1

        # ── 채팅 로그 (survey_id는 마지막 삽입 ID) ──
        last_survey_id = cur.lastrowid
        if random.random() < 0.75:
            n_turns = random.randint(2, 6)
            for t in range(n_turns):
                chat_date = post_date if inserted_surveys > 0 else pre_date
                cur.execute("""
                    INSERT INTO chats (survey_id, role, content, created_at)
                    VALUES (?,?,?,?)
                """, (last_survey_id,
                      "user" if t % 2 == 0 else "assistant",
                      random.choice([
                          "요즘 커리어 방향이 너무 막막해요.",
                          "목표는 세우는데 실행이 안 됩니다.",
                          "일이 지루하고 의미를 못 찾겠어요.",
                          "실패했을 때 너무 오래 자책하는 것 같아요.",
                          "네, 오늘의 과제를 실행해보겠습니다!",
                          "말씀처럼 작게 시작해보니 달라지는 것 같아요.",
                      ]),
                      chat_date))

        # ── 성찰 일지 (60% 확률, 2~5개) ──
        if random.random() < 0.60:
            n_journals = random.randint(2, 5)
            for _ in range(n_journals):
                j_date = random_date(25, 1)
                cur.execute("""
                    INSERT INTO journals (user_idx, action, reflection, created_at)
                    VALUES (?,?,?,?)
                """, (user_idx,
                      random.choice(ACTIONS),
                      random.choice(REFLECTION_POOL),
                      j_date))
                inserted_journals += 1

    conn.commit()
    conn.close()

    print("=" * 50)
    print("✅  AI MATE 가상 데이터 생성 완료")
    print("=" * 50)
    print(f"  사용자    : {inserted_users}명 (스킵: {skipped}명)")
    print(f"  진단 세션 : {inserted_surveys}건")
    print(f"  성찰 일지 : {inserted_journals}건")
    print(f"  DB 경로   : {DB_PATH}")
    print("=" * 50)
    print()
    print("📌 통계 미리보기:")
    conn2 = get_conn()
    genders = conn2.execute("SELECT gender, COUNT(*) as n FROM user GROUP BY gender").fetchall()
    for g in genders:
        print(f"  성별 {g['gender']}: {g['n']}명")
    ages = conn2.execute("SELECT AVG(age) as avg_age, MIN(age) as min_age, MAX(age) as max_age FROM user").fetchone()
    print(f"  나이 평균: {ages['avg_age']:.1f}세  (최소 {ages['min_age']}세 ~ 최대 {ages['max_age']}세)")
    avg_score = conn2.execute("SELECT AVG(overall) as avg FROM survey WHERE is_post=0").fetchone()
    post_score = conn2.execute("SELECT AVG(overall) as avg FROM survey WHERE is_post=1").fetchone()
    print(f"  사전 진단 평균: {avg_score['avg']:.2f}점")
    if post_score['avg']:
        print(f"  사후 진단 평균: {post_score['avg']:.2f}점")
        print(f"  평균 향상도   : +{post_score['avg'] - avg_score['avg']:.2f}점")
    conn2.close()
    print()
    print("▶  이제 streamlit run app.py 를 실행하면 관리자 대시보드에서 확인할 수 있습니다.")


if __name__ == "__main__":
    print(f"DB 경로: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("⚠️  aiMate.db 파일이 없습니다. 먼저 streamlit run app.py를 한 번 실행하여 DB를 초기화하세요.")
        exit(1)
    # 기존 가상 데이터가 있으면 초기화할지 선택
    conn = get_conn()
    existing = conn.execute("SELECT COUNT(*) FROM user").fetchone()[0]
    conn.close()
    if existing > 0:
        print(f"⚠️  이미 사용자 {existing}명이 등록되어 있습니다.")
        ans = input("기존 데이터를 유지하고 추가 생성하려면 Y, 취소하려면 N: ").strip().upper()
        if ans != "Y":
            print("취소되었습니다.")
            exit(0)
    seed(100)
