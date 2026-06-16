# build_kb.py — AI MATE 코칭 지식베이스 구축 (100개 버전)
# 사용법: python build_kb.py
# 결과: ./chroma_db/ 폴더에 100개 코칭 지식 벡터DB 생성

import os
import chromadb
from chromadb.utils import embedding_functions

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db")

def get_embedding_fn():
    try:
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="jhgan/ko-sroberta-multitask")
        ef(["테스트"]); print("✅ 한국어 임베딩 (ko-sroberta)"); return ef
    except Exception:
        try:
            ef = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="paraphrase-multilingual-MiniLM-L12-v2")
            ef(["테스트"]); print("✅ 다국어 임베딩 (multilingual-MiniLM)"); return ef
        except Exception:
            print("⚠️  ChromaDB 기본 임베딩 사용")
            return embedding_functions.DefaultEmbeddingFunction()


KNOWLEDGE = [
# ══════════════════════════════════════════════════════════
# 행동중심전략 (behavior) — 33개
# ══════════════════════════════════════════════════════════
# ── 코칭 원칙 (4) ──
{"id":"beh_pr_01","factor":"behavior","category":"coaching_principle",
 "text":"행동중심전략이 낮은 사람은 목표를 세워도 실행으로 이어지지 않는다. 핵심 코칭 원칙은 완벽한 계획보다 불완전한 실행을 먼저 장려하는 것이다. 오늘 15분 안에 할 수 있는 가장 작은 행동 하나를 찾아 즉시 시작하도록 유도한다."},
{"id":"beh_pr_02","factor":"behavior","category":"coaching_principle",
 "text":"행동 변화의 첫걸음은 목표의 가시화이다. 추상적 다짐을 눈에 보이는 형태(체크리스트, 일정표, 진행 막대)로 바꾸면 실행 가능성이 높아진다. 코치는 학습자가 목표를 시각적으로 표현하도록 돕는다."},
{"id":"beh_pr_03","factor":"behavior","category":"coaching_principle",
 "text":"자기관찰(self-observation)은 행동중심전략의 핵심이다. 자신의 행동을 기록하는 것만으로도 바람직한 행동이 증가하는 반응성 효과가 나타난다. 코치는 학습자가 하루 단위로 행동을 점검하도록 안내한다."},
{"id":"beh_pr_04","factor":"behavior","category":"coaching_principle",
 "text":"자기보상(self-reward)은 지속적 실행의 동력이다. 목표 달성 시 스스로에게 작은 보상을 주는 습관은 행동을 강화한다. 코치는 학습자가 자신만의 보상 체계를 설계하도록 돕는다."},
# ── 연구 근거 (5) ──
{"id":"beh_rs_01","factor":"behavior","category":"research",
 "text":"셀프리더십 연구(Houghton et al., 2012)에 따르면 행동중심전략은 자기목표 설정, 자기관찰, 자기보상의 세 요소로 구성된다. 목표를 구체적이고 측정 가능하게 설정할수록 실행률이 향상된다."},
{"id":"beh_rs_02","factor":"behavior","category":"research",
 "text":"실행 의도(implementation intention) 연구(Gollwitzer, 1999)는 언제·어디서·어떻게를 구체적으로 정하면 목표 달성률이 2~3배 높아짐을 보였다. 막연한 결심보다 상황과 연결된 계획이 행동을 촉발한다."},
{"id":"beh_rs_03","factor":"behavior","category":"research",
 "text":"최고은(2020)은 성인의 셀프리더십이 자기효능감을 매개로 직무만족에 영향을 미치며, 특히 행동중심전략의 향상이 자기효능감 증가에 가장 직접적임을 확인하였다. 작은 성공 경험의 축적이 핵심 메커니즘이다."},
{"id":"beh_rs_04","factor":"behavior","category":"research",
 "text":"목표설정이론(Locke & Latham, 2002)에 따르면 구체적이고 도전적인 목표가 모호한 목표보다 높은 성과를 낳는다. '최선을 다하자'보다 '이번 주 3회 실행'이 효과적이다."},
{"id":"beh_rs_05","factor":"behavior","category":"research",
 "text":"습관 형성 연구(Lally et al., 2010)는 새로운 행동이 자동화되기까지 평균 66일이 걸림을 밝혔다. 행동중심전략 코칭에서 단기 성과보다 지속의 중요성을 강조하는 근거이다."},
# ── 코칭 기법 (8) ──
{"id":"beh_tc_01","factor":"behavior","category":"technique",
 "text":"2분 규칙: 2분 안에 할 수 있는 일은 지금 즉시 하고, 큰 일은 첫 2분만 시작하는 것을 목표로 삼는다. 시작의 장벽을 낮춰 미루기를 극복하는 기법이다."},
{"id":"beh_tc_02","factor":"behavior","category":"technique",
 "text":"목표 쪼개기(chunking): 큰 목표를 3단계 이하의 작은 단위로 분해한다. '보고서 작성'을 '자료 수집→개요 작성→초안 작성'으로 나누면 실행 가능성이 높아진다."},
{"id":"beh_tc_03","factor":"behavior","category":"technique",
 "text":"실행 의도 문장: '나는 [언제] [어디서] [무엇을] 하겠다' 형식으로 계획을 작성한다. '내일 오전 9시에 책상에서 보고서 첫 단락을 쓰겠다'처럼 구체화한다."},
{"id":"beh_tc_04","factor":"behavior","category":"technique",
 "text":"하루 1개 우선순위: 매일 아침 '오늘 반드시 끝낼 단 하나'를 정한다. 여러 일에 분산되는 에너지를 한 곳에 집중시켜 완수 경험을 만든다."},
{"id":"beh_tc_05","factor":"behavior","category":"technique",
 "text":"진행 기록표: 행동을 달력이나 표에 매일 체크한다. 연속된 체크 표시가 끊기지 않게 하려는 심리(돈 브레이크 더 체인)가 지속을 돕는다."},
{"id":"beh_tc_06","factor":"behavior","category":"technique",
 "text":"환경 설계: 원하는 행동은 쉽게, 원치 않는 행동은 어렵게 환경을 바꾼다. 운동복을 미리 꺼내두면 운동 실행이 쉬워지는 원리이다."},
{"id":"beh_tc_07","factor":"behavior","category":"technique",
 "text":"5초 규칙: 행동을 미루고 싶을 때 5초를 세고 즉시 움직인다. 망설임이 행동을 막기 전에 몸을 먼저 움직이게 하는 기법이다."},
{"id":"beh_tc_08","factor":"behavior","category":"technique",
 "text":"주간 회고: 매주 끝에 '무엇을 했고, 무엇이 막혔는가'를 점검한다. 계획-실행-점검의 순환을 돌려 다음 주 계획을 수정한다."},
# ── 성인여성 맥락 (4) ──
{"id":"beh_wm_01","factor":"behavior","category":"women_context",
 "text":"성인 여성의 행동중심전략 저하는 다중 역할 부담에서 기인한다. 직장·가정·자기계발을 동시에 수행하며 우선순위 설정에 어려움을 겪는다. '중요하지만 급하지 않은 일'에 하루 30분 확보가 효과적이다."},
{"id":"beh_wm_02","factor":"behavior","category":"women_context",
 "text":"여성은 타인의 필요를 우선하느라 자기 목표를 뒤로 미루는 경향이 있다. 자기 목표를 일정에 먼저 배치하는 것(나를 위한 시간 블록)이 행동중심전략 강화의 출발점이다."},
{"id":"beh_wm_03","factor":"behavior","category":"women_context",
 "text":"경력 단절을 경험한 여성은 재시작의 첫 행동에 큰 심리적 장벽을 느낀다. 거창한 복귀 계획보다 '오늘 이력서 한 줄 수정'처럼 미세한 첫걸음이 실행을 촉발한다."},
{"id":"beh_wm_04","factor":"behavior","category":"women_context",
 "text":"여성의 완벽주의는 시작을 지연시키는 요인이 된다. '완벽하게 준비된 다음'이 아니라 '지금 가능한 만큼'으로 기준을 낮추면 행동이 시작된다."},
# ── 롤모델 철학 (4) ──
{"id":"beh_rm_01","factor":"behavior","category":"role_model",
 "text":"마리 퀴리의 핵심 철학: 목표를 반복적으로 검증하고 작은 실험을 쌓아가는 과학적 실행력이다. 수천 번의 실패 속에서도 이번 실험에서 무엇을 배웠는가를 기록했다. 큰 성취는 작은 실행의 누적이다."},
{"id":"beh_rm_02","factor":"behavior","category":"role_model",
 "text":"이순신의 핵심 철학: 극도의 압박 속에서도 오늘 할 일을 명확히 정하고 기록하는 습관이다. 난중일기는 전쟁 중에도 매일 상황을 정리하고 다음 행동을 계획한 기록이다."},
{"id":"beh_rm_03","factor":"behavior","category":"role_model",
 "text":"벤자민 프랭클린의 핵심 철학: 13개 덕목을 정하고 매주 하나씩 집중 실천하는 자기점검 시스템이다. 완벽한 하루가 아니라 점검하는 하루가 성장을 만든다."},
{"id":"beh_rm_04","factor":"behavior","category":"role_model",
 "text":"김만덕의 핵심 철학: 주변 조건을 살피며 실질적인 첫 행동을 찾는 현실 감각이다. 거창한 이상보다 지금 할 수 있는 구체적 실천으로 변화를 만들었다."},
# ── 실천 사례 (5) ──
{"id":"beh_ex_01","factor":"behavior","category":"example",
 "text":"실천 사례: 매일 아침 '오늘의 1순위'를 포스트잇에 적어 모니터에 붙인다. 그 한 가지를 끝내면 나머지는 보너스로 여긴다. 작은 완수가 자신감을 만든다."},
{"id":"beh_ex_02","factor":"behavior","category":"example",
 "text":"실천 사례: 미루던 이메일은 '제목만 먼저 쓰기'로 시작한다. 시작의 장벽을 넘으면 본문은 자연스럽게 이어진다."},
{"id":"beh_ex_03","factor":"behavior","category":"example",
 "text":"실천 사례: 운동 목표를 '30분 운동'이 아니라 '운동화 신고 현관 나서기'로 잡는다. 첫 행동을 최소화하면 그 다음은 따라온다."},
{"id":"beh_ex_04","factor":"behavior","category":"example",
 "text":"실천 사례: 큰 프로젝트를 시작할 때 '25분 집중-5분 휴식'의 뽀모도로를 단 1회만 해본다. 한 번의 집중이 흐름을 만든다."},
{"id":"beh_ex_05","factor":"behavior","category":"example",
 "text":"실천 사례: 하루를 마치며 완수한 일에 줄을 긋는다. 지워지는 항목을 눈으로 확인하는 것이 다음 날의 실행 동기가 된다."},
# ── 3T 가이드 (3) ──
{"id":"beh_3t_01","factor":"behavior","category":"reflection_guide",
 "text":"3T 성찰의 Task 단계(행동중심): 오늘 실행한 행동을 '무엇을 언제 어떻게 했는가' 사실 중심으로 구체적으로 기록한다. 모호한 기록보다 구체적 행동 기술이 다음 실천 동기를 높인다."},
{"id":"beh_3t_02","factor":"behavior","category":"reflection_guide",
 "text":"3T 성찰의 Trigger 단계(행동중심): 실행을 막거나 도운 계기를 찾는다. '무엇 때문에 시작했는가, 무엇이 방해했는가'를 적으면 다음 행동 설계의 단서가 된다."},
{"id":"beh_3t_03","factor":"behavior","category":"reflection_guide",
 "text":"3T 성찰의 Transform 단계(행동중심): 내일의 첫 행동을 실행 의도 문장으로 작성한다. '내일 [언제] [무엇을] 하겠다'로 마무리하면 성찰이 행동으로 연결된다."},

# ══════════════════════════════════════════════════════════
# 자연적 보상전략 (natural) — 33개
# ══════════════════════════════════════════════════════════
# ── 코칭 원칙 (4) ──
{"id":"nat_pr_01","factor":"natural","category":"coaching_principle",
 "text":"자연적 보상전략이 낮은 사람은 일을 의무로만 인식하며 내적 동기가 소진된 상태다. 과업 자체에서 의미·흥미·역량 발휘의 즐거움을 찾도록 돕는 것이 핵심이다. '이 일에서 내가 배우는 것은 무엇인가' 질문이 효과적이다."},
{"id":"nat_pr_02","factor":"natural","category":"coaching_principle",
 "text":"내적 동기는 강요로 만들어지지 않는다. 코치는 정답을 주기보다 학습자가 스스로 의미를 발견하도록 질문을 던진다. 발견된 의미만이 지속적 동기가 된다."},
{"id":"nat_pr_03","factor":"natural","category":"coaching_principle",
 "text":"자율성의 인식이 내적 동기의 핵심이다. 같은 일도 '시켜서 한다'가 아니라 '내가 선택했다'고 느낄 때 동기가 살아난다. 코치는 학습자의 선택권을 부각시킨다."},
{"id":"nat_pr_04","factor":"natural","category":"coaching_principle",
 "text":"작은 즐거움의 발견이 큰 의미로 이어진다. 일 전체가 즐겁지 않아도 그 안의 한 부분에서 흥미를 찾으면 동기의 실마리가 된다."},
# ── 연구 근거 (5) ──
{"id":"nat_rs_01","factor":"natural","category":"research",
 "text":"자기결정이론(Deci & Ryan, 2000)에 따르면 내적 동기는 자율성·유능감·관계성의 세 욕구가 충족될 때 발생한다. 반복 업무에서도 '내가 선택한다'는 인식만 높여도 내적 동기가 향상된다."},
{"id":"nat_rs_02","factor":"natural","category":"research",
 "text":"문세연(2025)의 ASLQ 연구에서 자연적 보상전략은 회복탄력성을 43.2% 설명하는 핵심 변인으로 확인되었다. 일에서 의미를 발견하는 능력이 스트레스에 대한 심리적 면역력을 높인다."},
{"id":"nat_rs_03","factor":"natural","category":"research",
 "text":"몰입(flow) 연구(Csikszentmihalyi, 1990)는 과제 난이도와 역량이 균형을 이룰 때 깊은 몰입과 즐거움이 발생함을 보였다. 너무 쉽지도 어렵지도 않은 적정 도전이 내적 보상을 만든다."},
{"id":"nat_rs_04","factor":"natural","category":"research",
 "text":"잡 크래프팅 연구(Wrzesniewski & Dutton, 2001)는 업무 방식·관계·의미를 스스로 재구성하면 같은 일도 다르게 경험됨을 밝혔다. 의미는 주어지는 것이 아니라 만들어가는 것이다."},
{"id":"nat_rs_05","factor":"natural","category":"research",
 "text":"의미 중심 동기 연구는 일의 목적을 더 큰 가치와 연결할 때 지속 동기가 강화됨을 보인다. '내 일이 누구에게 어떤 도움이 되는가'를 인식하면 동기가 회복된다."},
# ── 코칭 기법 (8) ──
{"id":"nat_tc_01","factor":"natural","category":"technique",
 "text":"잡 크래프팅: 업무 방식을 조금씩 수정하거나, 동료와 협력하거나, 일의 의미를 재해석하여 같은 업무를 다르게 경험한다. 통제 가능한 작은 변화부터 시작한다."},
{"id":"nat_tc_02","factor":"natural","category":"technique",
 "text":"마이크로 보상: 목표 달성 시 즉각적이고 작은 보상(커피 한 잔, 음악 10분, 짧은 산책)을 준다. 감각적 보상이 다음 과업의 동기를 높인다."},
{"id":"nat_tc_03","factor":"natural","category":"technique",
 "text":"의미 한 줄 쓰기: 과업을 시작하기 전 '이 일을 끝내면 무엇을 얻는가'를 한 줄로 적는다. 의미를 미리 명시하면 지루함이 줄어든다."},
{"id":"nat_tc_04","factor":"natural","category":"technique",
 "text":"흥미 요소 추가: 지루한 일에 게임 요소(시간 기록, 점수, 도전)를 더한다. 같은 일도 놀이로 재구성하면 몰입이 생긴다."},
{"id":"nat_tc_05","factor":"natural","category":"technique",
 "text":"강점 활용: 자신의 강점을 발휘할 수 있는 방식으로 일을 재배치한다. 강점이 쓰이는 순간 유능감과 즐거움이 동시에 일어난다."},
{"id":"nat_tc_06","factor":"natural","category":"technique",
 "text":"감사 일기: 하루에 잘된 일 3가지를 기록한다. 긍정 경험에 주의를 돌리면 일상에서 의미를 발견하는 감각이 길러진다."},
{"id":"nat_tc_07","factor":"natural","category":"technique",
 "text":"목적 연결: 지금 하는 일을 자신의 더 큰 가치나 목표와 연결한다. '이 보고서는 내 전문성을 쌓는 과정'처럼 의미를 부여한다."},
{"id":"nat_tc_08","factor":"natural","category":"technique",
 "text":"호기심 질문: 일하면서 '왜 이럴까, 더 나은 방법은 없을까'를 묻는다. 호기심은 의무를 탐구로 바꾸는 가장 강력한 내적 동기이다."},
# ── 성인여성 맥락 (4) ──
{"id":"nat_wm_01","factor":"natural","category":"women_context",
 "text":"성인 여성의 자연적 보상 저하는 번아웃과 역할 과부하에서 비롯된다. '나를 위한 시간'을 이기적이라 느끼는 인식을 전환하는 것이 중요하다. 자기돌봄은 지속 가능한 성장의 기반이다."},
{"id":"nat_wm_02","factor":"natural","category":"women_context",
 "text":"돌봄 노동에 지친 여성은 자신의 흥미와 즐거움을 잊기 쉽다. '예전에 무엇을 할 때 시간 가는 줄 몰랐는가'를 되묻는 것이 잃어버린 내적 동기를 회복하는 단서가 된다."},
{"id":"nat_wm_03","factor":"natural","category":"women_context",
 "text":"여성은 성취를 당연시하고 즐기지 못하는 경향이 있다. 작은 성취를 의식적으로 축하하고 음미하는 연습이 자연적 보상 감각을 키운다."},
{"id":"nat_wm_04","factor":"natural","category":"women_context",
 "text":"산소마스크 원칙: 비행기에서 자신의 산소마스크를 먼저 써야 타인을 돕듯, 자신을 먼저 채워야 지속적으로 베풀 수 있다. 자기돌봄은 의무 수행의 전제이다."},
# ── 롤모델 철학 (4) ──
{"id":"nat_rm_01","factor":"natural","category":"role_model",
 "text":"프리다 칼로의 핵심 철학: 극심한 고통과 제약 속에서도 자신의 경험을 예술로 승화시켰다. 어떤 상황도 나만의 의미로 재창조할 수 있다는 믿음이 내적 동기였다."},
{"id":"nat_rm_02","factor":"natural","category":"role_model",
 "text":"윤동주의 핵심 철학: 절망적 현실 속에서도 내면의 가치와 진정성을 지켰다. 외부 평가가 아닌 자신의 가치 기준으로 살아가는 것이 진정한 내적 동기이다."},
{"id":"nat_rm_03","factor":"natural","category":"role_model",
 "text":"리처드 파인만의 핵심 철학: 물리학을 재미있는 놀이로 접근했다. '내가 이것을 즐기지 못하면 왜 하는가'를 물었다. 호기심과 유희의 감각이 의무를 흥미로 바꾼다."},
{"id":"nat_rm_04","factor":"natural","category":"role_model",
 "text":"레이첼 카슨의 핵심 철학: 작은 일이 더 큰 책임과 연결되는 지점을 보았다. 자신의 일을 자연과 미래 세대에 대한 사명으로 의미화하여 깊은 동기를 얻었다."},
# ── 실천 사례 (5) ──
{"id":"nat_ex_01","factor":"natural","category":"example",
 "text":"실천 사례: 반복적인 집안일에 좋아하는 팟캐스트를 함께 듣는다. 지루한 일에 즐거운 요소를 결합하면 경험이 달라진다."},
{"id":"nat_ex_02","factor":"natural","category":"example",
 "text":"실천 사례: 업무 보고서를 쓸 때 '이 일로 내가 배우는 기술 한 가지'를 메모해둔다. 성장의 관점이 의무를 의미로 바꾼다."},
{"id":"nat_ex_03","factor":"natural","category":"example",
 "text":"실천 사례: 하루를 마치며 '오늘 가장 몰입했던 순간'을 떠올린다. 그 순간을 늘려가는 것이 내적 동기를 키우는 길이다."},
{"id":"nat_ex_04","factor":"natural","category":"example",
 "text":"실천 사례: 단조로운 업무를 '시간 안에 끝내기' 도전으로 바꾼다. 스스로 만든 작은 게임이 몰입을 만든다."},
{"id":"nat_ex_05","factor":"natural","category":"example",
 "text":"실천 사례: 주말에 의무가 아닌 순수한 즐거움을 위한 30분을 확보한다. 그 시간이 한 주의 내적 에너지를 충전한다."},
# ── 3T 가이드 (3) ──
{"id":"nat_3t_01","factor":"natural","category":"reflection_guide",
 "text":"3T 성찰의 Task 단계(자연적 보상): 오늘 한 일 중 조금이라도 의미나 흥미를 느낀 순간을 기록한다. 작은 즐거움의 발견이 내적 동기의 씨앗이 된다."},
{"id":"nat_3t_02","factor":"natural","category":"reflection_guide",
 "text":"3T 성찰의 Trigger 단계(자연적 보상): '무엇이 그 순간을 의미 있게 했는가'를 적는다. 자신을 움직이는 내적 동기의 원천을 발견하는 단계이다."},
{"id":"nat_3t_03","factor":"natural","category":"reflection_guide",
 "text":"3T 성찰의 Transform 단계(자연적 보상): 내일 일에서 의미를 더할 한 가지 방법을 정한다. '내일은 이 일에 이런 의미를 부여하겠다'로 마무리한다."},

# ══════════════════════════════════════════════════════════
# 건설적 사고패턴전략 (thought) — 34개
# ══════════════════════════════════════════════════════════
# ── 코칭 원칙 (4) ──
{"id":"tho_pr_01","factor":"thought","category":"coaching_principle",
 "text":"건설적 사고패턴이 낮은 사람은 부정적 자기대화와 과도한 자기비판 패턴을 보인다. 핵심은 생각을 바꾸라가 아니라 같은 상황을 다른 관점으로 볼 수 있다는 인지적 유연성을 키우는 것이다."},
{"id":"tho_pr_02","factor":"thought","category":"coaching_principle",
 "text":"억지 긍정은 효과가 없다. 코치는 무조건 긍정하라 대신, 상황을 정확히 보고 통제 가능한 부분을 찾도록 돕는다. 현실적 낙관이 건설적 사고의 핵심이다."},
{"id":"tho_pr_03","factor":"thought","category":"coaching_principle",
 "text":"자기연민(self-compassion)이 자기비판보다 성장에 효과적이다. 실패한 자신을 친구 대하듯 친절하게 대하는 태도가 회복과 재도전을 가능하게 한다."},
{"id":"tho_pr_04","factor":"thought","category":"coaching_principle",
 "text":"생각은 사실이 아니라 해석이다. '나는 부족하다'는 생각을 사실이 아닌 하나의 해석으로 거리를 두고 바라보면, 다른 해석의 여지가 열린다."},
# ── 연구 근거 (5) ──
{"id":"tho_rs_01","factor":"thought","category":"research",
 "text":"긍정심리학 연구(Seligman, 2011)에서 성공 시각화(mental imagery)는 실제 수행 능력을 향상시킨다. 중요한 일을 앞두고 성공하는 자신을 구체적으로 상상하면 자기효능감이 증가한다."},
{"id":"tho_rs_02","factor":"thought","category":"research",
 "text":"인지행동치료(CBT) 연구는 자동적 부정 사고를 식별하고 재구성하면 정서와 행동이 변화함을 보인다. 생각-감정-행동의 연결고리에서 생각을 바꾸는 것이 출발점이다."},
{"id":"tho_rs_03","factor":"thought","category":"research",
 "text":"임희정(2018)의 여성 리더십 연구에 따르면 한국 여성 관리자는 자신의 능력을 과소평가하는 경향이 있으며, 이는 유리천장보다 내면의 심리적 장벽에서 더 기인한다. 긍정적 자기대화 훈련이 효과적이다."},
{"id":"tho_rs_04","factor":"thought","category":"research",
 "text":"성장 마인드셋 연구(Dweck, 2006)는 능력이 노력으로 발전한다는 믿음이 도전과 회복을 촉진함을 보였다. 실패를 끝이 아닌 학습 과정으로 보는 관점이 건설적 사고이다."},
{"id":"tho_rs_05","factor":"thought","category":"research",
 "text":"자기연민 연구(Neff, 2003)는 자기비판보다 자기연민이 회복탄력성과 동기를 높임을 밝혔다. 실패 후 자신을 비난하는 사람보다 위로하는 사람이 더 빨리 재도전한다."},
# ── 코칭 기법 (8) ──
{"id":"tho_tc_01","factor":"thought","category":"technique",
 "text":"인지 재구성 4단계: 1)부정 상황을 한 문장으로 적기 2)이 상황에서 배울 점 질문하기 3)통제 가능한 요소 찾기 4)배움의 언어로 다시 쓰기. 매일 1개 상황에 적용한다."},
{"id":"tho_tc_02","factor":"thought","category":"technique",
 "text":"자기대화 점검: 자신에게 한 말을 친한 친구에게도 할 수 있는지 묻는다. 친구에게 하지 않을 가혹한 말이라면 자신에게도 하지 않는다."},
{"id":"tho_tc_03","factor":"thought","category":"technique",
 "text":"성공 시각화: 중요한 일을 앞두고 5분간 성공적으로 완수하는 자신의 모습을 구체적으로 상상한다. 감각적으로 생생할수록 효과가 크다."},
{"id":"tho_tc_04","factor":"thought","category":"technique",
 "text":"증거 찾기: '나는 못한다'는 생각이 들 때, 그 반대 증거(과거의 성취)를 3가지 찾는다. 근거 있는 자기확신이 부정적 사고를 누른다."},
{"id":"tho_tc_05","factor":"thought","category":"technique",
 "text":"걱정-통제 분리: 걱정거리를 적고, 내가 통제할 수 있는 것과 없는 것을 나눈다. 통제 가능한 것에만 에너지를 집중한다."},
{"id":"tho_tc_06","factor":"thought","category":"technique",
 "text":"재해석 연습: 부정적 사건을 '나에게 무엇을 가르치려는가'의 관점으로 다시 본다. 모든 역경을 성장의 데이터로 재해석한다."},
{"id":"tho_tc_07","factor":"thought","category":"technique",
 "text":"감정 라벨링: 부정적 감정에 정확한 이름을 붙인다(불안, 좌절, 실망). 감정을 명명하는 것만으로 그 강도가 줄어든다."},
{"id":"tho_tc_08","factor":"thought","category":"technique",
 "text":"3인칭 거리두기: 고민을 '내가'가 아닌 '그가/그녀가'로 바꿔 본다. 자신의 문제를 제3자처럼 보면 더 객관적이고 차분해진다."},
# ── 성인여성 맥락 (4) ──
{"id":"tho_wm_01","factor":"thought","category":"women_context",
 "text":"여성 리더십 연구에 따르면 여성은 자신의 능력을 과소평가하는 임포스터 증후군을 자주 겪는다. '내가 이 자리에 있을 자격이 있을까'라는 생각이 들면 지금까지의 성취 목록을 만들어본다."},
{"id":"tho_wm_02","factor":"thought","category":"women_context",
 "text":"여성은 칭찬을 운으로, 실패를 능력 부족으로 귀인하는 경향이 있다. 성공을 자신의 노력과 능력으로 정당하게 인정하는 연습이 필요하다."},
{"id":"tho_wm_03","factor":"thought","category":"women_context",
 "text":"완벽주의에 시달리는 여성은 작은 실수에도 자기비판이 강하다. '완벽이 아니라 충분히 좋음(good enough)'을 새로운 기준으로 삼으면 자기대화가 부드러워진다."},
{"id":"tho_wm_04","factor":"thought","category":"women_context",
 "text":"여성은 타인의 평가에 민감하게 반응하는 경향이 있다. 외부 시선보다 자신의 기준을 우선하는 연습이 건설적 사고의 자율성을 키운다."},
# ── 롤모델 철학 (4) ──
{"id":"tho_rm_01","factor":"thought","category":"role_model",
 "text":"헬렌 켈러의 핵심 철학: 보지도 듣지도 못하는 상황을 불가능이 아닌 다른 방식으로 가능으로 재정의했다. 한 문이 닫히면 다른 문이 열린다는 믿음이 건설적 사고의 본질이다."},
{"id":"tho_rm_02","factor":"thought","category":"role_model",
 "text":"넬슨 만델라의 핵심 철학: 27년의 감옥 생활을 원망이 아닌 준비의 시간으로 재해석했다. '나는 지는 것을 모른다, 이기거나 배우거나'라는 철학처럼 모든 실패는 성장의 데이터이다."},
{"id":"tho_rm_03","factor":"thought","category":"role_model",
 "text":"루스 베이더 긴즈버그의 핵심 철학: 수십 번 거절당했지만 감정에 치우치지 않고 논리적 근거로 자신의 자리를 만들었다. '분노는 에너지를 낭비한다, 그 에너지를 행동에 쓰라.'"},
{"id":"tho_rm_04","factor":"thought","category":"role_model",
 "text":"플로렌스 나이팅게일의 핵심 철학: 상황을 사실과 데이터로 정리해 해결 실마리를 찾았다. 감정적 절망 대신 객관적 분석으로 문제를 돌파하는 건설적 사고의 전형이다."},
# ── 실천 사례 (5) ──
{"id":"tho_ex_01","factor":"thought","category":"example",
 "text":"실천 사례: 실수했을 때 '나는 왜 이럴까' 대신 '이번에 무엇을 배웠나'로 질문을 바꾼다. 질문이 바뀌면 감정과 다음 행동이 달라진다."},
{"id":"tho_ex_02","factor":"thought","category":"example",
 "text":"실천 사례: 발표 전 화장실 거울 앞에서 '나는 준비됐다, 잘 해낼 수 있다'를 소리내어 말한다. 긍정적 자기대화가 자신감을 만든다."},
{"id":"tho_ex_03","factor":"thought","category":"example",
 "text":"실천 사례: 잠들기 전 오늘 잘한 일 2가지를 떠올린다. 부정 편향에 기운 뇌를 긍정 경험으로 균형 잡는다."},
{"id":"tho_ex_04","factor":"thought","category":"example",
 "text":"실천 사례: 걱정이 쌓일 때 종이에 모두 적고, 통제 가능한 것 옆에만 동그라미를 친다. 동그라미 친 것만 행동으로 옮긴다."},
{"id":"tho_ex_05","factor":"thought","category":"example",
 "text":"실천 사례: 부정적 생각이 들 때 '이게 사실일까, 다른 해석은 없을까'를 스스로 묻는다. 생각과 거리를 두는 습관이 유연성을 키운다."},
# ── 3T 가이드 (3) ──
{"id":"tho_3t_01","factor":"thought","category":"reflection_guide",
 "text":"3T 성찰의 Task 단계(건설적 사고): 오늘 부정적 생각이 들었던 상황을 사실 그대로 기록한다. 감정과 사실을 분리해 적는 것이 출발점이다."},
{"id":"tho_3t_02","factor":"thought","category":"reflection_guide",
 "text":"3T 성찰의 Trigger 단계(건설적 사고): 그 상황을 다르게 해석할 여지를 찾는다. '이 경험이 나에게 가르치는 것은 무엇인가'를 적으며 관점을 넓힌다."},
{"id":"tho_3t_03","factor":"thought","category":"reflection_guide",
 "text":"3T 성찰의 Transform 단계(건설적 사고): 내일 같은 상황에서 쓸 긍정적 자기대화 문장을 미리 준비한다. '다음엔 이렇게 말하겠다'로 마무리한다."},
{"id":"tho_pr_05","factor":"thought","category":"coaching_principle",
 "text":"건설적 사고의 최종 목표는 자기 신뢰의 회복이다. 부정적 사고를 통제하는 것을 넘어, 어떤 상황에서도 나는 해결 방법을 찾을 수 있다는 근본적 자기 신뢰를 세우는 것이 코칭의 지향점이다."},
]


def build():
    print("\n" + "="*55)
    print("  AI MATE 코칭 지식베이스 구축 (100개)")
    print("="*55)
    client = chromadb.PersistentClient(path=DB_DIR)
    try:
        client.delete_collection("coaching_kb")
        print("  기존 컬렉션 초기화")
    except Exception:
        pass
    ef = get_embedding_fn()
    collection = client.create_collection(
        name="coaching_kb", embedding_function=ef,
        metadata={"hnsw:space": "cosine"})

    documents = [k["text"] for k in KNOWLEDGE]
    ids       = [k["id"]   for k in KNOWLEDGE]
    metadatas = [{"factor": k["factor"], "category": k["category"]} for k in KNOWLEDGE]
    collection.add(documents=documents, ids=ids, metadatas=metadatas)

    print(f"\n  ✅ {len(KNOWLEDGE)}개 지식 문서 삽입 완료")
    print(f"  📁 저장 위치: {DB_DIR}")

    from collections import Counter
    fc = Counter(k["factor"] for k in KNOWLEDGE)
    print(f"\n  요인별 분포:")
    labels = {"behavior":"행동중심", "natural":"자연적보상", "thought":"건설적사고"}
    for f, n in fc.items():
        print(f"    {labels.get(f,f)}: {n}개")

    print("\n" + "-"*55)
    print("  🔍 검색 테스트")
    print("-"*55)
    tests = [
        ("목표를 세워도 실행이 안돼요", "behavior"),
        ("일이 지루하고 의미가 없어요", "natural"),
        ("실패하면 자책이 심해요", "thought"),
    ]
    for query, factor in tests:
        r = collection.query(query_texts=[query], n_results=2, where={"factor": factor})
        print(f"\n  질문: '{query}'")
        for i, doc in enumerate(r["documents"][0]):
            print(f"  결과 {i+1}: {doc[:55]}…")

    print("\n" + "="*55)
    print("  ✅ 100개 지식베이스 구축 완료!")
    print("="*55 + "\n")


if __name__ == "__main__":
    build()
