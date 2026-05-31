# ============================================================
#  logic.py — 비즈니스 로직
#  점수 계산 / 해석 / 롤모델 매칭 / AI 응답 / CSV 생성
# ============================================================

import os
import csv
import io
from datetime import datetime

from config   import FACTORS, QUESTIONS, ROLE_MODELS, TONE_OPTIONS, ISSUE_OPTIONS
from database import db_get_chat_count, db_get_journals


# ── 점수 계산 ─────────────────────────────────────────────
def calc_scores(answers: dict) -> dict:
    """
    9문항 응답 → 3요인 점수 + overall + lowest 반환
    """
    by_factor = {}
    for fk in FACTORS:
        ids  = [q[0] for q in QUESTIONS if q[1] == fk]
        vals = [answers.get(qid, 3) for qid in ids]
        by_factor[fk] = round(sum(vals) / len(vals), 1)
    overall = round(sum(by_factor.values()) / len(by_factor), 1)
    lowest  = min(by_factor, key=by_factor.get)
    return {**by_factor, "overall": overall, "lowest": lowest}


# ── 점수 해석 ─────────────────────────────────────────────
def interpretation(score: float) -> tuple:
    """점수 → (텍스트 라벨, CSS 클래스명)"""
    if score >= 4.1: return "강점 영역",     "interp-strong"
    if score >= 3.1: return "보통 이상",     "interp-ok"
    if score >= 2.1: return "성장 필요",     "interp-grow"
    return              "우선 개입 필요", "interp-need"


# ── 롤모델 매칭 ───────────────────────────────────────────
def choose_role_model(scores: dict, tone: str, issue: str) -> tuple:
    """
    취약 요인 풀(4인) 중
    (tone 인덱스 + issue 인덱스) % 4 번째 롤모델 선택
    """
    pool = ROLE_MODELS[scores["lowest"]]
    ti   = TONE_OPTIONS.index(tone)   if tone  in TONE_OPTIONS  else 0
    ii   = ISSUE_OPTIONS.index(issue) if issue in ISSUE_OPTIONS else 0
    return pool[(ti + ii) % len(pool)]


# ── AI 코칭 응답 ──────────────────────────────────────────
def get_ai_reply(chat_history: list, role_model: tuple,
                 scores: dict, issue: str, tone: str) -> str:
    """
    Anthropic Claude API 호출.
    API 키 없거나 오류 발생 시 요인별 fallback 응답 반환.
    """
    import streamlit as st

    name   = role_model[0]
    low    = scores["lowest"]
    factor = FACTORS[low]

    system = (
        f"당신은 {name}의 삶의 궤적과 가치철학을 깊이 연구하여 구성된 AI 코칭 롤모델입니다.\n"
        "실제 인물의 발언을 직접 인용하거나 사칭하지 않습니다.\n"
        f'사용자는 현재 "{factor["label"]}" 역량이 취약한 성인 여성으로, "{issue}" 분야의 고민이 있습니다.\n'
        f'코칭 스타일: "{tone}"\n'
        "코칭 흐름: 1)공감 → 2)사고 전환 → 3)오늘 실행 가능한 행동 1~2가지 제안.\n"
        "4~6문장 이내 한국어로 답하세요."
    )
    messages = [{"role": m["role"], "content": m["content"]} for m in chat_history[-20:]]

    try:
        from anthropic import Anthropic
        api_key = (st.secrets.get("anthropic", {}).get("api_key")
                   or os.environ.get("ANTHROPIC_API_KEY"))
        client   = Anthropic(api_key=api_key) if api_key else Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=600, system=system, messages=messages
        )
        return response.content[0].text
    except Exception:
        fallbacks = {
            "behavior": f"좋아요. 그 일을 '생각'이 아니라 '첫 행동'으로 바꿔봅시다. "
                        f"15분 안에 할 수 있는 가장 작은 조각을 찾아 오늘 바로 실행해보세요.\n\n"
                        f"오늘의 과제: {factor['action_task']}",
            "natural":  f"그 일 안에서 의미를 찾는 방향으로 다뤄볼게요. "
                        f"끝낸 뒤 어떤 배움이 남을지 한 줄로 먼저 적어보세요.\n\n"
                        f"오늘의 과제: {factor['action_task']}",
            "thought":  f"지금 필요한 건 억지 긍정보다 해석의 폭을 넓히는 일입니다. "
                        f"걱정을 하나 적고, 내가 선택할 수 있는 작은 행동을 골라보세요.\n\n"
                        f"오늘의 과제: {factor['action_task']}",
        }
        return fallbacks.get(low, "조금 더 구체적으로 말씀해 주시면 함께 방향을 찾아볼게요.")


# ── 익명 CSV 생성 ─────────────────────────────────────────
def build_csv(ss: dict) -> bytes:
    """
    세션 상태 dict → 익명 연구용 CSV (BOM UTF-8, Excel 호환)
    """
    scores   = ss.get("scores") or {}
    journals = db_get_journals()
    pre      = ss.get("pre_score")
    post     = ss.get("post_score")
    diff     = round(post - pre, 2) if (pre is not None and post is not None) else ""

    fields = [
        "created_at", "issue", "tone",
        "behavior_score", "natural_reward_score", "constructive_thought_score",
        "overall_score", "role_model",
        "user_chat_count", "journal_count",
        "pre_score", "post_score", "pre_post_diff",
    ]
    row = {
        "created_at":                  datetime.now().isoformat(timespec="seconds"),
        "issue":                        ss.get("issue", ""),
        "tone":                         ss.get("tone", ""),
        "behavior_score":               scores.get("behavior", ""),
        "natural_reward_score":         scores.get("natural", ""),
        "constructive_thought_score":   scores.get("thought", ""),
        "overall_score":                scores.get("overall", ""),
        "role_model":                   ss.get("role_model", [""])[0],
        "user_chat_count":              db_get_chat_count(),
        "journal_count":                len(journals),
        "pre_score":                    pre  if pre  is not None else "",
        "post_score":                   post if post is not None else "",
        "pre_post_diff":                diff,
    }
    buf = io.StringIO()
    w   = csv.DictWriter(buf, fieldnames=fields)
    w.writeheader()
    w.writerow(row)
    return ("\ufeff" + buf.getvalue()).encode("utf-8")
