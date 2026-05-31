# ============================================================
#  app.py — AI MATE 메인 진입점
#  역할: 앱 설정 · 세션 초기화 · 사이드바 · 페이지 라우팅
#
#  파일 구조
#  ├── app.py          ← 여기 (진입점·라우터)
#  ├── config.py       ← FACTORS / QUESTIONS / ROLE_MODELS
#  ├── database.py     ← SQLite CRUD
#  ├── logic.py        ← 점수 계산 · AI 응답 · CSV
#  ├── styles.py       ← 전체 CSS
#  ├── components.py   ← 재사용 UI 컴포넌트
#  ├── requirements.txt
#  └── .streamlit/config.toml
# ============================================================

import threading
import webbrowser
import time
import streamlit as st
from datetime import datetime

# ── 내부 모듈 ────────────────────────────────────────────
from config     import FACTORS, QUESTIONS, ROLE_MODELS, ISSUE_OPTIONS, TONE_OPTIONS
from database   import (init_db, db_save_session, db_save_chat, db_save_journal,
                         db_get_journals, db_get_chat_count, db_get_session_count)
from logic      import calc_scores, choose_role_model, get_ai_reply, build_csv
from styles     import inject_css
from components import (render_radar_chart, render_score_bars, render_mentor_card,
                         render_mission_box, render_journal_entry, render_dashboard_metrics)


# ══════════════════════════════════════════════════════════
# 1. 앱 기본 설정
# ══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AI MATE — 셀프리더십 성장 플랫폼",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",   # 타이틀 화면에서는 숨김
)
inject_css()
init_db()

# ── 브라우저 자동 열기 ────────────────────────────────────
# Streamlit은 매번 전체 스크립트를 재실행하므로,
# 환경변수로 '이미 열었음'을 기록해 최초 1회만 실행합니다.
import os
#if not os.environ.get("AImate_BROWSER_OPENED"):
#    os.environ["AIMATE_BROWSER_OPENED"] = "1"
#    def _open_browser():
#        time.sleep(1.5)          # 서버가 완전히 뜰 때까지 잠깐 대기
#        webbrowser.open("http://localhost:8501")
#    threading.Thread(target=_open_browser, daemon=True).start()

# ── ① 세션 상태 초기화 ────────────────────────────────────
for k, v in {
    "answers":    {q[0]: 3 for q in QUESTIONS},
    "issue":      ISSUE_OPTIONS[0],
    "tone":       TONE_OPTIONS[0],
    "scores":     None,
    "role_model": None,
    "chat":       [],
    "session_id": None,
    "pre_score":  None,
    "post_score": None,
    "view":       "title",
    "diagnosed":  False,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════
# 2. 타이틀 페이지
# ══════════════════════════════════════════════════════════
if st.session_state.view == "title":
    st.markdown("""
    <div class="title-page">
      <div class="title-deco"></div>
      <div class="title-badge">🌿 AI-Powered Self-Leadership Platform</div>
      <div class="title-main">
        셀프리더십 향상을 위한<br>
        <em>AI MATE</em> 코칭 시스템
      </div>
      <div class="title-sub">
        ASLQ 기반 셀프리더십 진단부터 AI 롤모델 코칭,<br>
        성찰 일지, 사전–사후 비교까지 — 나를 이끄는 성장 여정
      </div>
      <div class="title-features">
        <div class="title-feat-item"><div class="feat-icon">🔍</div><div class="feat-text">9문항 ASLQ 진단</div></div>
        <div class="title-feat-item"><div class="feat-icon">🤝</div><div class="feat-text">AI 롤모델 매칭</div></div>
        <div class="title-feat-item"><div class="feat-icon">💬</div><div class="feat-text">1:1 코칭 대화</div></div>
        <div class="title-feat-item"><div class="feat-icon">📖</div><div class="feat-text">3T 성찰 일지</div></div>
        <div class="title-feat-item"><div class="feat-icon">📊</div><div class="feat-text">성장 대시보드</div></div>
      </div>
    </div>
    <div class="title-author" style="text-align:center;">
      Developed by <strong>Young</strong> · AI융합교육학과 박사과정
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    _, col_c, _ = st.columns([2, 1, 2])
    with col_c:
        if st.button("🌿  시작하기  →", type="primary", use_container_width=True):
            st.session_state.view = "diagnosis"
            st.rerun()
    st.stop()


# ══════════════════════════════════════════════════════════
# 3. 사이드바 (메인 앱 진입 후)
# ══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="brand-block">
      <div class="brand-icon">🌿</div>
      <div>
        <div class="brand-title">AI MATE</div>
        <div class="brand-sub">Self-Leadership Platform</div>
      </div>
    </div>""", unsafe_allow_html=True)
    st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)

    # 메인 네비게이션
    for view_id, label in [
        ("diagnosis", "◎  진단"),
        ("result",    "◈  결과 리포트"),
        ("mentor",    "◉  멘토 코칭"),
        ("journal",   "◇  성찰 일지"),
        ("dashboard", "◆  성장 대시보드"),
    ]:
        is_active = (st.session_state.view == view_id)
        if st.button(label, key=f"nav_{view_id}", use_container_width=True,
                     type="primary" if is_active else "secondary"):
            st.session_state.view = view_id
            st.rerun()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="research-badge">
      <div class="badge-label">📋 Research Tool</div>
      <div class="badge-body">ASLQ 기반 9문항<br>사전–사후 비교 설계</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")

    # CSV 내보내기
    if st.session_state.diagnosed:
        st.download_button(
            "↓ 익명 CSV 내보내기",
            data=build_csv(st.session_state),
            file_name=f"aiMate_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.caption("진단 완료 후 CSV 내보내기가 활성화됩니다.")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── ③ 타이틀 페이지로 돌아가기 버튼 ─────────────────
    st.markdown("---")
    if st.button("🏠  타이틀 페이지로", key="nav_title",
                 use_container_width=True, type="secondary"):
        st.session_state.view = "title"
        st.rerun()


# ══════════════════════════════════════════════════════════
# 4. 메인 헤더
# ══════════════════════════════════════════════════════════
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<p class="eyebrow">AI-powered Self-Leadership Growth Platform</p>',
                unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">나를 이끄는 AI MATE</h1>',
                unsafe_allow_html=True)
with col_h2:
    if st.session_state.diagnosed and st.session_state.scores:
        sc = st.session_state.scores["overall"]
        st.markdown(f"""
        <div class="score-hero">
          <div class="score-hero-label">전체 평균</div>
          <div class="score-hero-num">{sc:.1f}<span>/5.0</span></div>
        </div>""", unsafe_allow_html=True)
st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# 5. 뷰 라우터
# ══════════════════════════════════════════════════════════
view = st.session_state.view

# ─────────────────────────────────────────────────────────
# VIEW: 진단
# ─────────────────────────────────────────────────────────
if view == "diagnosis":
    st.markdown('<p class="eyebrow-coral">Self-Leadership Diagnosis · ASLQ</p>',
                unsafe_allow_html=True)
    st.subheader("9문항 셀프리더십 진단")
    st.caption("각 문항을 읽고 현재 자신의 모습과 얼마나 일치하는지 1~5점으로 응답해 주세요.")

    FC = {
        "behavior": ("#2a6658", "행동중심전략",       "목표 설정·실행 조절"),
        "natural":  ("#b8870a", "자연적 보상전략",     "내적 동기·의미 발견"),
        "thought":  ("#c25a3d", "건설적 사고패턴전략", "긍정 자기대화·이미지화"),
    }
    pill_bg = {1:"#fce8e2",2:"#fdf3d9",3:"#f0f4f0",4:"#e0f0ec",5:"#c8e6c9"}
    pill_fg = {1:"#c25a3d",2:"#b8870a",3:"#5a7a5e",4:"#2a6658",5:"#1b5e20"}

    for factor_key, (color, fname, fdesc) in FC.items():
        qs = [q for q in QUESTIONS if q[1] == factor_key]
        st.markdown(f"""
        <div class="factor-section-header" style="border-color:{color};">
          <span style="width:12px;height:12px;border-radius:50%;background:{color};
                       display:inline-block;flex-shrink:0;"></span>
          <span class="factor-section-title" style="color:{color};">{fname}</span>
          <span class="factor-section-desc">{fdesc}</span>
        </div>""", unsafe_allow_html=True)

        for qid, _, text in qs:
            cur_val = st.session_state.answers[qid]
            col_card, col_slider = st.columns([3, 2])
            with col_card:
                st.markdown(f"""
                <div class="q-row-card" style="border-left:4px solid {color};">
                  <span class="q-row-num" style="float:right;">{qid}</span>
                  <span class="q-row-dot" style="background:{color};display:inline-block;
                        width:10px;height:10px;border-radius:50%;margin-right:8px;"></span>
                  <div class="q-row-text">{text}</div>
                </div>""", unsafe_allow_html=True)
            with col_slider:
                st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
                st.markdown('<span style="font-size:11px;color:#9e9e9e;">← 전혀 아님 &nbsp;&nbsp; 매우 그러함 →</span>',
                            unsafe_allow_html=True)
                val = st.slider(f"{qid}번 문항 점수 (1~5점)", 1, 5, cur_val,
                                key=f"sq_{qid}", label_visibility="collapsed")
                st.session_state.answers[qid] = val
                st.markdown(f"""
                <div style="text-align:right;margin-top:4px;">
                  <span style="display:inline-flex;align-items:center;justify-content:center;
                    min-width:42px;height:42px;border-radius:10px;
                    background:{pill_bg.get(val,'#f0f4f0')};
                    color:{pill_fg.get(val,'#2a6658')};
                    font-weight:800;font-size:16px;">{val}점</span>
                </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    st.markdown("---")
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        issue = st.selectbox("현재 고민 분야", ISSUE_OPTIONS,
                             index=ISSUE_OPTIONS.index(st.session_state.issue))
        st.session_state.issue = issue
    with c2:
        tone = st.selectbox("원하는 코칭 스타일", TONE_OPTIONS,
                            index=TONE_OPTIONS.index(st.session_state.tone))
        st.session_state.tone = tone
    with c3:
        st.markdown('<div style="height:28px"></div>', unsafe_allow_html=True)
        if st.button("진단 결과 보기 →", type="primary", use_container_width=True):
            scores = calc_scores(st.session_state.answers)
            rm     = choose_role_model(scores, st.session_state.tone, st.session_state.issue)
            st.session_state.scores     = scores
            st.session_state.role_model = rm
            st.session_state.diagnosed  = True
            if st.session_state.pre_score is None:
                st.session_state.pre_score = scores["overall"]
            sid = db_save_session(st.session_state.issue, st.session_state.tone, scores, rm, 0)
            st.session_state.session_id = sid
            st.session_state.chat       = []
            st.session_state.view       = "result"
            st.rerun()


# ─────────────────────────────────────────────────────────
# VIEW: 결과 리포트
# ─────────────────────────────────────────────────────────
elif view == "result":
    st.markdown('<p class="eyebrow-coral">Result Report</p>', unsafe_allow_html=True)
    st.subheader("요인별 점수와 해석")
    if not st.session_state.diagnosed:
        st.info("먼저 진단을 완료해주세요.")
        if st.button("진단 화면으로 →"):
            st.session_state.view = "diagnosis"; st.rerun()
    else:
        scores = st.session_state.scores
        cc, cs = st.columns([1, 1])
        with cc:
            st.caption("셀프리더십 프로파일")
            st.plotly_chart(render_radar_chart(scores), use_container_width=True,
                            config={"displayModeBar": False})
        with cs:
            render_score_bars(scores)

        st.markdown("---")
        low = scores["lowest"]; fi = FACTORS[low]
        ci1, ci2, ci3 = st.columns(3)
        for col, icon, title, body in [
            (ci1, "🎯", "취약 요인 집중 개발",
             f"{fi['label']} 점수({scores[low]:.1f}점)가 가장 낮습니다. 이 영역에 집중한 AI 롤모델이 매칭됩니다."),
            (ci2, "✨", fi["insight_title"], fi["insight_desc"]),
            (ci3, "📋", "오늘의 실천과제",   fi["action_task"]),
        ]:
            with col:
                st.markdown(f"""
                <div class="insight-card">
                  <div class="i-icon">{icon}</div>
                  <div class="i-title">{title}</div>
                  <div class="i-body">{body}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("---")

        # ── 사전-사후 비교 섹션 ──────────────────────────────
        pre  = st.session_state.pre_score
        post = st.session_state.post_score

        st.markdown('<p class="eyebrow-coral">Pre-Post Comparison · 연구 설계</p>',
                    unsafe_allow_html=True)
        st.markdown("#### 📊 사전-사후 셀프리더십 비교")

        col_pre, col_post, col_diff = st.columns(3)

        with col_pre:
            pre_val  = f"{pre:.1f}" if pre is not None else "—"
            pre_sub  = "첫 번째 진단 결과" if pre is not None else "아직 사전 진단 없음"
            st.markdown(f"""
            <div class="metric-wrap">
              <div class="metric-label">🔵 사전 진단 점수</div>
              <div class="metric-num">{pre_val}</div>
              <div class="metric-sub">{pre_sub}</div>
            </div>""", unsafe_allow_html=True)

        with col_post:
            post_val = f"{post:.1f}" if post is not None else "—"
            post_sub = "사후 저장된 점수" if post is not None else "아직 사후 진단 없음"
            st.markdown(f"""
            <div class="metric-wrap">
              <div class="metric-label">🟢 사후 진단 점수</div>
              <div class="metric-num">{post_val}</div>
              <div class="metric-sub">{post_sub}</div>
            </div>""", unsafe_allow_html=True)

        with col_diff:
            if pre is not None and post is not None:
                diff     = post - pre
                sign     = "+" if diff >= 0 else ""
                color    = "#2a6658" if diff >= 0 else "#c25a3d"
                arrow    = "▲" if diff > 0 else ("▼" if diff < 0 else "━")
                diff_str = f"{sign}{diff:.1f}"
                diff_sub = "향상" if diff > 0 else ("유지" if diff == 0 else "하락")
            else:
                diff_str = "—"
                color    = "#9e9e9e"
                arrow    = ""
                diff_sub = "사전·사후 모두 저장 후 표시"

            st.markdown(f"""
            <div class="metric-wrap">
              <div class="metric-label">📈 변화량 (사후 - 사전)</div>
              <div class="metric-num" style="color:{color};">{arrow} {diff_str}</div>
              <div class="metric-sub">{diff_sub}</div>
            </div>""", unsafe_allow_html=True)

        # 요인별 사전-사후 막대 비교
        if pre is not None and post is not None:
            st.markdown("---")
            st.markdown("##### 요인별 변화 비교")

            # DB에서 가장 최근 사전 세션 불러오기
            from database import get_conn
            conn = get_conn()
            pre_row  = conn.execute(
                "SELECT behavior, natural_reward, constructive_thought FROM sessions "
                "WHERE is_post=0 ORDER BY created_at LIMIT 1"
            ).fetchone()
            post_row = conn.execute(
                "SELECT behavior, natural_reward, constructive_thought FROM sessions "
                "WHERE is_post=1 ORDER BY created_at DESC LIMIT 1"
            ).fetchone()
            conn.close()

            if pre_row and post_row:
                factor_labels = {
                    "behavior": ("행동중심전략", "#2a6658"),
                    "natural":  ("자연적 보상전략", "#b8870a"),
                    "thought":  ("건설적 사고패턴전략", "#c25a3d"),
                }
                factor_keys  = ["behavior", "natural", "thought"]
                pre_vals  = [pre_row[0],  pre_row[1],  pre_row[2]]
                post_vals = [post_row[0], post_row[1], post_row[2]]

                for i, key in enumerate(factor_keys):
                    fname, fcolor = factor_labels[key]
                    pv  = pre_vals[i]  or 0
                    pov = post_vals[i] or 0
                    diff_f = pov - pv
                    sign   = "+" if diff_f >= 0 else ""
                    st.markdown(f"""
                    <div style="margin-bottom:14px;">
                      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                        <span style="font-size:13px;font-weight:600;color:{fcolor};">{fname}</span>
                        <span style="font-size:12px;color:#737373;">사전 {pv:.1f} → 사후 {pov:.1f}
                          <strong style="color:{'#2a6658' if diff_f>=0 else '#c25a3d'};">
                            ({sign}{diff_f:.1f})
                          </strong>
                        </span>
                      </div>
                      <div style="height:8px;background:rgba(0,0,0,.08);border-radius:4px;overflow:hidden;position:relative;">
                        <div style="height:100%;width:{int(pv/5*100)}%;background:{fcolor};opacity:.35;border-radius:4px;position:absolute;left:0;top:0;"></div>
                        <div style="height:100%;width:{int(pov/5*100)}%;background:{fcolor};border-radius:4px;position:absolute;left:0;top:0;"></div>
                      </div>
                      <div style="display:flex;justify-content:space-between;font-size:10px;color:#9e9e9e;margin-top:2px;">
                        <span>0</span><span>5</span>
                      </div>
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("요인별 비교는 사전·사후 진단이 각 1회 이상 저장되어야 표시됩니다.")

        st.markdown("---")
        # 사후진단 저장 버튼
        save_col, info_col = st.columns([1, 2])
        with save_col:
            if st.button("📥  현재 결과를 사후진단으로 저장", type="secondary",
                         use_container_width=True):
                st.session_state.post_score = scores["overall"]
                db_save_session(st.session_state.issue, st.session_state.tone,
                                scores, st.session_state.role_model, 1)
                st.success(f"사후진단 점수({scores['overall']:.1f}점)가 저장되었습니다! "
                           f"위 비교표가 업데이트됩니다.")
                st.rerun()
        with info_col:
            st.markdown("""
            <div style="background:#fdf3d9;border-radius:8px;padding:12px 16px;
                        border:1px solid rgba(184,135,10,.2);font-size:12.5px;color:#7a5c00;">
              <strong>📌 사후진단 저장이란?</strong><br>
              2주간 AI MATE를 사용한 <em>후</em>, 진단을 다시 받고 이 버튼을 누르면
              처음(사전) 점수와 현재(사후) 점수를 비교하여 셀프리더십 향상 여부를
              수치로 확인할 수 있습니다. 연구 데이터(CSV)에도 두 점수가 함께 기록됩니다.
            </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# VIEW: 멘토 코칭
# ─────────────────────────────────────────────────────────
elif view == "mentor":
    st.markdown('<p class="eyebrow-coral">AI Coaching Room</p>', unsafe_allow_html=True)
    st.subheader("진단 기반 AI 롤모델 매칭")
    if not st.session_state.diagnosed:
        st.info("먼저 진단을 완료해주세요.")
        if st.button("진단 화면으로 →"):
            st.session_state.view = "diagnosis"; st.rerun()
    else:
        scores = st.session_state.scores
        rm     = st.session_state.role_model
        low    = scores["lowest"]
        cp, cc = st.columns([1, 2])
        with cp:
            render_mentor_card(rm, low, st.session_state)
            render_mission_box(FACTORS[low]["action_task"])
        with cc:
            st.markdown('<div class="chat-header" style="font-size:14px;font-weight:700;margin-bottom:10px;">💬 AI 코칭 대화</div>',
                        unsafe_allow_html=True)
            if len(st.session_state.chat) == 0:
                opening = (
                    f"**{rm[0]}** 의 가치에서 영감을 받은 AI 코칭 롤모델입니다.\n\n"
                    f"진단 결과, **{FACTORS[low]['label']}** 점수({scores[low]:.1f}점)가 "
                    f"상대적으로 낮게 나타났어요. "
                    f"지금 가장 미루고 있거나 마음에 걸리는 일을 하나만 알려주세요. 🌱"
                )
                st.session_state.chat.append({"role": "assistant", "content": opening})
                db_save_chat(st.session_state.session_id, "assistant", opening)

            chat_box = st.container(height=420)
            with chat_box:
                for msg in st.session_state.chat:
                    with st.chat_message(msg["role"],
                                         avatar="🌿" if msg["role"] == "assistant" else "🙋"):
                        st.markdown(msg["content"])

            user_input = st.chat_input("지금 가장 다루고 싶은 고민을 적어보세요…")
            if user_input:
                st.session_state.chat.append({"role": "user", "content": user_input})
                db_save_chat(st.session_state.session_id, "user", user_input)
                with st.spinner("AI 롤모델이 응답을 작성하고 있습니다..."):
                    reply = get_ai_reply(st.session_state.chat, rm, scores,
                                         st.session_state.issue, st.session_state.tone)
                st.session_state.chat.append({"role": "assistant", "content": reply})
                db_save_chat(st.session_state.session_id, "assistant", reply)
                st.rerun()


# ─────────────────────────────────────────────────────────
# VIEW: 성찰 일지
# ─────────────────────────────────────────────────────────
elif view == "journal":
    st.markdown('<p class="eyebrow-coral">Reflection Journal · 3T Model</p>',
                unsafe_allow_html=True)
    st.subheader("오늘의 실천과 성찰")
    cf, cl = st.columns([1, 1])
    with cf:
        st.markdown("""
        <div class="three-t-box">
          <div class="t-row"><span class="t-tag">Task</span>
            <span class="t-desc">어떤 과제를 수행했나요?</span></div>
          <div class="t-row"><span class="t-tag">Trigger</span>
            <span class="t-desc">내면의 변화나 깨달음은?</span></div>
          <div class="t-row"><span class="t-tag">Transform</span>
            <span class="t-desc">내일의 다짐은 무엇인가요?</span></div>
        </div>""", unsafe_allow_html=True)
        with st.form("journal_form", clear_on_submit=True):
            action     = st.text_input("오늘 실행한 작은 행동",
                                        placeholder="예: 내일 할 일 1개 정하기")
            reflection = st.text_area("성찰 기록 (3T 가이드 참고)",
                                       placeholder="Task → Trigger → Transform 순서로 자유롭게 작성해보세요.",
                                       height=180)
            if st.form_submit_button("성찰 저장하기 ✓", type="primary",
                                      use_container_width=True):
                if action.strip() and reflection.strip():
                    db_save_journal(action.strip(), reflection.strip())
                    st.success("성찰 일지가 저장되었습니다! 🌱"); st.rerun()
                else:
                    st.warning("실행 행동과 성찰 내용을 모두 입력해주세요.")
    with cl:
        st.markdown("#### 📖 성찰 기록 목록")
        journals = db_get_journals()
        if not journals:
            st.markdown('<div class="empty-state">아직 저장된 성찰 기록이 없습니다.<br>'
                        '<small>오늘의 실천과제를 수행한 후 기록을 남겨보세요.</small></div>',
                        unsafe_allow_html=True)
        else:
            for j in journals:
                render_journal_entry(j)


# ─────────────────────────────────────────────────────────
# VIEW: 성장 대시보드
# ─────────────────────────────────────────────────────────
elif view == "dashboard":
    st.markdown('<p class="eyebrow-coral">My Growth Dashboard</p>',
                unsafe_allow_html=True)
    st.subheader("성장 변화와 연구 로그")
    if not st.session_state.diagnosed:
        st.info("먼저 진단을 완료해주세요.")
    else:
        scores   = st.session_state.scores
        journals = db_get_journals()
        render_dashboard_metrics(scores, journals, db_get_chat_count(),
                                  st.session_state.pre_score, st.session_state.post_score)
        st.markdown("---")
        dc, dt = st.columns([1, 1])
        with dc:
            st.markdown("#### 📊 요인별 점수")
            for key, info in FACTORS.items():
                s = scores[key]; pct = int(s / 5 * 100); color = info["color"]
                st.markdown(f"""
                <div class="fbar-row">
                  <div class="fbar-label">{info['short']}</div>
                  <div class="fbar-track">
                    <div class="fbar-fill" style="width:{pct}%;background:{color};"></div>
                  </div>
                  <div class="fbar-val">{s:.1f}</div>
                </div>""", unsafe_allow_html=True)
        with dt:
            st.markdown("#### 🗂 연구 로그 타임라인")
            rm_name = st.session_state.role_model[0] if st.session_state.role_model else "—"
            tl_items = [
                ("사전진단",
                 f"{st.session_state.pre_score:.1f}점 저장됨"
                 if st.session_state.pre_score else "첫 진단 결과가 기록됩니다."),
                ("롤모델 매칭",
                 f"{rm_name} · {FACTORS[scores['lowest']]['label']}"),
                ("성찰 일지",  f"{len(journals)}건 기록"),
                ("진단 세션",  f"총 {db_get_session_count()}회"),
                ("사후진단",
                 f"{st.session_state.post_score:.1f}점 저장됨"
                 if st.session_state.post_score else "사후진단 미완료"),
            ]
            for lbl, body in tl_items:
                st.markdown(f"""
                <div class="tl-item">
                  <div class="tl-label">{lbl}</div>
                  <div class="tl-body">{body}</div>
                </div>""", unsafe_allow_html=True)
