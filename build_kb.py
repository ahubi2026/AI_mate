# build_kb.py — AI MATE 코칭 지식베이스 구축
# ============================================================
# 사용법: python build_kb.py
# 결과:   ./chroma_db/ 폴더에 벡터DB 생성
# 1회만 실행하면 됩니다. 이후에는 자동으로 로드됩니다.
# ============================================================

import os
import chromadb
from chromadb.utils import embedding_functions

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db")

# ──────────────────────────────────────────────────────────
# 임베딩 함수 설정
# 인터넷 연결 시: "all-MiniLM-L6-v2" (영문 빠름)
# 한국어 최적:   "jhgan/ko-sroberta-multitask" (느리지만 정확)
# 기본(오프라인): chromadb 내장 함수 사용
# ──────────────────────────────────────────────────────────
def get_embedding_fn():
    try:
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="jhgan/ko-sroberta-multitask"
        )
        # 테스트
        ef(["테스트"])
        print("✅ 한국어 임베딩 모델 로드 완료 (ko-sroberta)")
        return ef
    except Exception:
        try:
            ef = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="paraphrase-multilingual-MiniLM-L12-v2"
            )
            ef(["테스트"])
            print("✅ 다국어 임베딩 모델 로드 완료 (multilingual-MiniLM)")
            return ef
        except Exception:
            print("⚠️  sentence-transformers 없음 → ChromaDB 기본 임베딩 사용")
            return embedding_functions.DefaultEmbeddingFunction()


# ──────────────────────────────────────────────────────────
# 코칭 지식베이스 데이터
# ──────────────────────────────────────────────────────────
KNOWLEDGE = [

    # ════════════════════════════════════════════════════
    # 1. ASLQ 요인별 코칭 원칙
    # ════════════════════════════════════════════════════
    {
        "id": "behavior_001",
        "factor": "behavior",
        "category": "coaching_principle",
        "text": "행동중심전략이 낮은 사람은 목표를 세워도 실행으로 이어지지 않는 패턴을 보입니다. 핵심 코칭 원칙은 '완벽한 계획'보다 '불완전한 실행'을 먼저 장려하는 것입니다. 오늘 15분 안에 할 수 있는 가장 작은 행동 하나를 찾아 즉시 시작하도록 유도하세요.",
    },
    {
        "id": "behavior_002",
        "factor": "behavior",
        "category": "research",
        "text": "셀프리더십 연구(Houghton et al., 2012)에 따르면 행동중심전략은 자기목표 설정, 자기관찰, 자기보상의 세 요소로 구성됩니다. 목표를 구체적이고 측정 가능하게 설정할수록 실행률이 67% 향상됩니다. 추상적 목표를 행동 단위로 쪼개는 것이 핵심입니다.",
    },
    {
        "id": "behavior_003",
        "factor": "behavior",
        "category": "coaching_technique",
        "text": "미루기(procrastination)의 근본 원인은 게으름이 아닌 완벽주의와 실패 두려움입니다. '2분 규칙'을 적용하세요. 2분 안에 할 수 있는 일은 지금 당장 하고, 그보다 큰 일은 첫 2분만 시작하는 것을 목표로 삼으면 실행력이 크게 향상됩니다.",
    },
    {
        "id": "behavior_004",
        "factor": "behavior",
        "category": "coaching_technique",
        "text": "목표 달성을 위한 실행 계획 수립 시 '언제, 어디서, 어떻게'를 구체적으로 정하는 실행 의도(implementation intention) 기법이 효과적입니다. '나는 내일 오전 9시에 책상에서 보고서 첫 단락을 작성하겠다'처럼 구체적으로 설정하면 실행 가능성이 2~3배 높아집니다.",
    },
    {
        "id": "behavior_005",
        "factor": "behavior",
        "category": "women_context",
        "text": "성인 여성의 행동중심전략이 낮은 주요 원인은 다중 역할 부담입니다. 직장, 가정, 자기계발을 동시에 수행하며 우선순위 설정에 어려움을 겪습니다. 이때 '중요하지만 급하지 않은 일'에 하루 30분을 확보하는 것만으로도 셀프리더십 점수가 유의미하게 향상됩니다.",
    },

    # ════════════════════════════════════════════════════
    # 2. 자연적 보상전략
    # ════════════════════════════════════════════════════
    {
        "id": "natural_001",
        "factor": "natural",
        "category": "coaching_principle",
        "text": "자연적 보상전략이 낮은 사람은 일을 의무로만 인식하며 내적 동기가 소진된 상태입니다. 외부 보상(칭찬, 급여)에 의존하기보다 과업 자체에서 의미, 흥미, 역량 발휘의 즐거움을 찾도록 돕는 것이 핵심입니다. '이 일에서 내가 배우는 것은 무엇인가?'라는 질문이 효과적입니다.",
    },
    {
        "id": "natural_002",
        "factor": "natural",
        "category": "research",
        "text": "자기결정이론(Deci & Ryan, 2000)에 따르면 내적 동기는 자율성, 유능감, 관계성의 세 가지 기본 심리 욕구가 충족될 때 발생합니다. 반복적인 업무에서도 '내가 선택한다'는 자율성 인식만 높여도 내적 동기가 40% 이상 향상됩니다.",
    },
    {
        "id": "natural_003",
        "factor": "natural",
        "category": "coaching_technique",
        "text": "번아웃 예방을 위한 '마이크로 보상' 기법입니다. 목표를 달성했을 때 즉각적이고 작은 보상을 스스로에게 제공하세요. 커피 한 잔, 좋아하는 음악 10분 듣기, 짧은 산책처럼 감각적인 보상이 도파민 회로를 활성화하여 다음 과업의 동기를 높입니다.",
    },
    {
        "id": "natural_004",
        "factor": "natural",
        "category": "coaching_technique",
        "text": "지루한 일을 즐겁게 만드는 '잡 크래프팅(Job Crafting)' 기법입니다. 업무 방식을 조금씩 수정하거나, 동료와 협력하거나, 일의 의미를 재해석함으로써 같은 업무도 다르게 경험할 수 있습니다. 프리다 칼로가 고통을 예술로 승화시킨 것처럼, 어떤 경험도 의미 있는 이야기로 재구성할 수 있습니다.",
    },
    {
        "id": "natural_005",
        "factor": "natural",
        "category": "women_context",
        "text": "성인 여성의 자연적 보상전략 저하는 주로 번아웃과 역할 과부하에서 비롯됩니다. '나를 위한 시간'을 이기적이라고 느끼는 인식을 전환하는 것이 중요합니다. 자기돌봄은 지속 가능한 성장의 기반이며, 산소마스크 원칙처럼 나를 먼저 채워야 타인도 도울 수 있습니다.",
    },

    # ════════════════════════════════════════════════════
    # 3. 건설적 사고패턴전략
    # ════════════════════════════════════════════════════
    {
        "id": "thought_001",
        "factor": "thought",
        "category": "coaching_principle",
        "text": "건설적 사고패턴전략이 낮은 사람은 부정적 자기대화와 실패에 대한 과도한 자기비판 패턴을 보입니다. 핵심 코칭은 '생각을 바꾸라'가 아니라 '같은 상황을 다른 관점으로 볼 수 있다'는 인지적 유연성을 키우는 것입니다. 재해석(reframing) 연습이 가장 효과적입니다.",
    },
    {
        "id": "thought_002",
        "factor": "thought",
        "category": "research",
        "text": "긍정심리학 연구(Seligman, 2011)에서 성공 시각화(mental imagery)는 실제 수행 능력을 10~20% 향상시키는 것으로 밝혀졌습니다. 중요한 일을 앞두고 5분간 성공적으로 완수하는 자신의 모습을 구체적으로 상상하면 자기효능감이 유의미하게 증가합니다.",
    },
    {
        "id": "thought_003",
        "factor": "thought",
        "category": "coaching_technique",
        "text": "인지 재구성(cognitive reframing) 4단계 기법입니다. 1단계: 부정적 상황을 한 문장으로 적기. 2단계: '이 상황에서 내가 배울 수 있는 것은?' 질문하기. 3단계: 통제 가능한 요소 찾기. 4단계: 배움의 언어로 다시 쓰기. 매일 1개 상황에 적용하면 2주 후 인지 유연성이 눈에 띄게 향상됩니다.",
    },
    {
        "id": "thought_004",
        "factor": "thought",
        "category": "coaching_technique",
        "text": "자기대화(self-talk) 점검 기법입니다. 하루에 한 번, 자신에게 했던 말을 친한 친구에게도 할 수 있는지 물어보세요. '넌 왜 이것도 못해'라는 말을 친구에게 하겠습니까? 자기 자신에게도 같은 친절함을 적용하는 자기연민(self-compassion) 훈련이 건설적 사고의 출발점입니다.",
    },
    {
        "id": "thought_005",
        "factor": "thought",
        "category": "women_context",
        "text": "여성 리더십 연구에 따르면 여성은 남성보다 자신의 능력을 과소평가하는 경향이 있습니다(임포스터 증후군). '내가 정말 이 자리에 있을 자격이 있을까?'라는 생각이 자주 든다면, 지금까지 성취한 것들의 목록을 만들어보세요. 근거 있는 자기확신이 건설적 사고의 핵심입니다.",
    },

    # ════════════════════════════════════════════════════
    # 4. 롤모델 철학 (행동중심)
    # ════════════════════════════════════════════════════
    {
        "id": "rolemodel_curie",
        "factor": "behavior",
        "category": "role_model",
        "text": "마리 퀴리의 핵심 철학: 목표를 반복적으로 검증하고 작은 실험을 쌓아가는 과학적 실행력입니다. 그녀는 수천 번의 실패 속에서도 '이번 실험에서 무엇을 배웠는가'를 기록했습니다. 오늘 할 수 있는 가장 작은 검증을 시작하세요. 큰 성취는 작은 실행의 누적입니다.",
    },
    {
        "id": "rolemodel_iss",
        "factor": "behavior",
        "category": "role_model",
        "text": "이순신 장군의 핵심 철학: 극도의 압박 상황에서도 오늘 할 일을 명확히 정하고 기록하는 습관입니다. 난중일기는 전쟁 중에도 매일 상황을 정리하고 다음 행동을 계획한 기록입니다. 어떤 혼란 속에서도 오늘의 우선순위 하나를 정하는 것이 셀프리더십의 출발점입니다.",
    },
    {
        "id": "rolemodel_franklin",
        "factor": "behavior",
        "category": "role_model",
        "text": "벤자민 프랭클린의 핵심 철학: 13개의 덕목을 정하고 매주 하나씩 집중적으로 실천하는 자기점검 시스템입니다. 그는 매일 저녁 '오늘 무엇을 했는가'를 기록했습니다. 완벽한 하루가 아니라 점검하는 하루가 성장을 만듭니다.",
    },

    # ════════════════════════════════════════════════════
    # 5. 롤모델 철학 (자연적 보상)
    # ════════════════════════════════════════════════════
    {
        "id": "rolemodel_kahlo",
        "factor": "natural",
        "category": "role_model",
        "text": "프리다 칼로의 핵심 철학: 극심한 고통과 제약 속에서도 자신의 경험을 예술로 승화시켰습니다. 어떤 상황도 나만의 의미로 재창조할 수 있다는 믿음이 그녀의 내적 동기였습니다. 지금 하는 일에서 나만의 이야기를 찾아보세요. 그것이 지속 가능한 에너지의 원천입니다.",
    },
    {
        "id": "rolemodel_yoon",
        "factor": "natural",
        "category": "role_model",
        "text": "윤동주 시인의 핵심 철학: 절망적인 식민지 현실 속에서도 내면의 가치와 진정성을 지켰습니다. '죽는 날까지 하늘을 우러러 한 점 부끄럼이 없기를'처럼, 외부 평가가 아닌 자신의 가치 기준으로 살아가는 것이 진정한 내적 동기입니다.",
    },
    {
        "id": "rolemodel_feynman",
        "factor": "natural",
        "category": "role_model",
        "text": "리처드 파인만의 핵심 철학: 물리학을 '재미있는 놀이'로 접근했습니다. 그는 '내가 이것을 즐기지 못하면 왜 하는가'라고 항상 물었습니다. 어떤 과업에도 호기심과 유희의 감각을 더하면 의무가 흥미로 바뀝니다. 오늘의 업무에서 흥미로운 질문 하나를 찾아보세요.",
    },

    # ════════════════════════════════════════════════════
    # 6. 롤모델 철학 (건설적 사고)
    # ════════════════════════════════════════════════════
    {
        "id": "rolemodel_keller",
        "factor": "thought",
        "category": "role_model",
        "text": "헬렌 켈러의 핵심 철학: 보지도 듣지도 못하는 상황을 '불가능'이 아닌 '다른 방식으로 가능'으로 재정의했습니다. '한 문이 닫히면 다른 문이 열린다'는 그녀의 믿음처럼, 막힌 상황에서 아직 열려있는 선택지를 찾는 것이 건설적 사고의 본질입니다.",
    },
    {
        "id": "rolemodel_mandela",
        "factor": "thought",
        "category": "role_model",
        "text": "넬슨 만델라의 핵심 철학: 27년의 감옥 생활을 원망이 아닌 준비의 시간으로 재해석했습니다. '나는 지는 것을 모른다. 이기거나 배우거나'라는 그의 철학처럼, 모든 실패와 역경은 성장의 데이터입니다. 지금 겪는 어려움에서 10년 후 가르쳐줄 수 있는 교훈을 찾아보세요.",
    },
    {
        "id": "rolemodel_ginsburg",
        "factor": "thought",
        "category": "role_model",
        "text": "루스 베이더 긴즈버그의 핵심 철학: 여성이라는 이유로 수십 번 거절당했지만 감정에 치우치지 않고 논리적 근거로 자신의 자리를 만들었습니다. '분노는 에너지를 낭비한다. 그 에너지를 행동에 쓰라'는 그녀의 철학처럼, 근거 있는 자기확신이 어떤 편견도 넘어설 수 있습니다.",
    },

    # ════════════════════════════════════════════════════
    # 7. 성인 여성 리더십 연구 근거
    # ════════════════════════════════════════════════════
    {
        "id": "research_women_001",
        "factor": "behavior",
        "category": "research",
        "text": "최고은(2020) 연구에서 성인의 셀프리더십은 자기효능감을 완전 매개로 직무만족도에 유의미한 영향을 미칩니다. 특히 행동중심전략의 향상이 자기효능감 증가에 가장 직접적인 영향을 주었습니다. 작은 성공 경험의 축적이 자기효능감을 높이는 핵심 메커니즘입니다.",
    },
    {
        "id": "research_women_002",
        "factor": "thought",
        "category": "research",
        "text": "임희정(2018) 여성 리더십 연구에 따르면 한국 여성 관리자는 자신의 리더십 능력을 과소평가하는 경향이 있으며, 이는 조직 내 유리천장보다 내면의 심리적 장벽에서 더 많이 기인합니다. 긍정적 자기대화 훈련이 이 장벽을 낮추는 데 효과적입니다.",
    },
    {
        "id": "research_women_003",
        "factor": "natural",
        "category": "research",
        "text": "문세연(2025) ASLQ 연구에서 자연적 보상전략이 회복탄력성을 43.2% 설명하는 핵심 변인으로 확인되었습니다. 일 속에서 의미를 발견하는 능력이 스트레스와 번아웃에 대한 심리적 면역력을 높입니다.",
    },
    {
        "id": "research_rolemodel_001",
        "factor": "thought",
        "category": "research",
        "text": "Joo(2025) 여성 롤모델 연구에서 여성 대학생들은 여성 롤모델을 통해 도전, 회복탄력성, 감성적 공감의 리더십 가치를 내면화하는 것으로 나타났습니다. 롤모델의 삶을 서사적으로 성찰하는 것 자체가 자기효능감 향상에 기여합니다.",
    },

    # ════════════════════════════════════════════════════
    # 8. 3T 성찰 모델 가이드
    # ════════════════════════════════════════════════════
    {
        "id": "reflection_3t_001",
        "factor": "behavior",
        "category": "reflection_guide",
        "text": "3T 성찰 모델의 Task 단계: 오늘 수행한 실천과제를 구체적으로 기술합니다. '무엇을 언제 어떻게 했는가'를 사실 중심으로 기록하세요. 모호한 기록보다 구체적 행동 기술이 다음 실천의 동기를 높입니다.",
    },
    {
        "id": "reflection_3t_002",
        "factor": "natural",
        "category": "reflection_guide",
        "text": "3T 성찰 모델의 Trigger 단계: 과제 수행 중 내면에서 일어난 변화, 깨달음, 감정의 변화를 기록합니다. '처음에는 X라고 생각했는데, 해보니 Y라는 것을 알았다'는 형식이 효과적입니다. 이 단계가 진짜 학습이 일어나는 지점입니다.",
    },
    {
        "id": "reflection_3t_003",
        "factor": "thought",
        "category": "reflection_guide",
        "text": "3T 성찰 모델의 Transform 단계: 이 경험을 바탕으로 내일의 행동과 마음가짐이 어떻게 달라질지 구체적으로 작성합니다. 다짐은 추상적일수록 실행되지 않습니다. '내일 아침 9시에 X를 한다'처럼 실행 의도로 마무리하세요.",
    },
]


# ──────────────────────────────────────────────────────────
# 지식베이스 구축 메인 함수
# ──────────────────────────────────────────────────────────
def build():
    print("\n" + "="*55)
    print("  AI MATE 코칭 지식베이스 구축 시작")
    print("="*55)

    # ChromaDB 클라이언트 (로컬 파일 저장)
    client = chromadb.PersistentClient(path=DB_DIR)

    # 기존 컬렉션 삭제 후 재생성 (재실행 시 중복 방지)
    try:
        client.delete_collection("coaching_kb")
        print("  기존 컬렉션 초기화 완료")
    except Exception:
        pass

    ef = get_embedding_fn()

    collection = client.create_collection(
        name="coaching_kb",
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"}
    )

    # 데이터 삽입
    documents = [k["text"] for k in KNOWLEDGE]
    ids       = [k["id"]   for k in KNOWLEDGE]
    metadatas = [{"factor": k["factor"], "category": k["category"]}
                 for k in KNOWLEDGE]

    collection.add(documents=documents, ids=ids, metadatas=metadatas)

    print(f"\n  ✅ {len(KNOWLEDGE)}개 지식 문서 삽입 완료")
    print(f"  📁 저장 위치: {DB_DIR}")

    # 검색 테스트
    print("\n" + "-"*55)
    print("  🔍 검색 테스트")
    print("-"*55)

    test_queries = [
        ("목표를 세워도 실행이 안돼요", "behavior"),
        ("일이 너무 지루하고 의미가 없어요", "natural"),
        ("실패하면 자책이 심해요", "thought"),
    ]

    for query, expected_factor in test_queries:
        results = collection.query(
            query_texts=[query],
            n_results=2,
            where={"factor": expected_factor}
        )
        print(f"\n  질문: '{query}'")
        for i, doc in enumerate(results["documents"][0]):
            print(f"  결과 {i+1}: {doc[:60]}…")

    print("\n" + "="*55)
    print("  ✅ 지식베이스 구축 완료!")
    print("  이제 streamlit run app.py 를 실행하면")
    print("  RAG가 자동으로 활성화됩니다.")
    print("="*55 + "\n")


if __name__ == "__main__":
    build()
