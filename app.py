# app.py — AI MATE v5 (모든 오류 수정)
import os, time, re
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

from config import (FACTORS, ROLE_MODELS, ISSUE_OPTIONS, TONE_OPTIONS, ADMIN_ID, ADMIN_PWD)
from database import (
    init_db, register_user, check_email_available, login_user,
    get_all_users, reset_user_pwd, get_user_count, get_age_distribution,
    get_questions, get_all_questions_admin, add_question, update_question, toggle_question,
    save_survey, get_user_surveys, get_all_surveys, get_survey_count,
    save_chat, get_chat_count, save_journal, get_journals
)
from logic import (calc_scores, interpretation, choose_role_model, get_ai_reply,
                    build_csv_all, build_user_csv, generate_pdf,
                    validate_email, validate_pwd, validate_name, format_phone)
from styles import inject_css
from components import (render_radar_chart, render_score_bars, render_mentor_card,
                         render_mission_box, render_journal_entry, render_dashboard_metrics)

# ══════════════════════════════════════════════════════════
# 앱 설정
# ══════════════════════════════════════════════════════════
st.set_page_config(page_title="AI MATE", page_icon="🌿", layout="wide",
                   initial_sidebar_state="collapsed")
inject_css()
st.markdown("""<style>
.auth-box{background:rgba(255,255,255,.85);border:1px solid rgba(0,0,0,.1);
  border-radius:12px;padding:16px 20px;backdrop-filter:blur(6px);}
.admin-card{background:#fff;border:1px solid rgba(0,0,0,.08);border-radius:12px;padding:20px;margin-bottom:14px;}
.admin-title{font-size:13px;font-weight:700;color:#5a3d8a;letter-spacing:.06em;text-transform:uppercase;margin-bottom:8px;}
.reg-section{background:linear-gradient(135deg,#e8f0e9 0%,#e0ece8 50%,#eaf0f6 100%);
  border-radius:16px;padding:30px;margin-bottom:20px;}
.reg-title{font-family:'DM Serif Display',serif;font-size:28px;color:#2a6658;margin-bottom:4px;}
.reg-sub{font-size:13px;color:#737373;}
.user-id-display{background:#2a6658;color:white;padding:6px 16px;border-radius:999px;
  font-size:13px;font-weight:600;display:inline-block;}
</style>""", unsafe_allow_html=True)

init_db()

# ── 브라우저 자동 열기 (환경변수로 1회만) ──
if not os.environ.get("AIMATE_OPENED"):
    os.environ["AIMATE_OPENED"] = "1"
    import threading, webbrowser
    def _ob():
        time.sleep(1.5)
        webbrowser.open("http://localhost:8501")
    threading.Thread(target=_ob, daemon=True).start()

# ── 세션 초기화 ──
defaults = {
    "answers": {q["qid"]: 3 for q in get_questions()},
    "issue": ISSUE_OPTIONS[0], "tone": TONE_OPTIONS[0],
    "scores": None, "role_model": None, "chat": [], "survey_id": None,
    "pre_score": None, "post_score": None,
    "view": "title", "diagnosed": False,
    "user": None, "admin_logged": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

user = st.session_state.user  # None 또는 dict


# ══════════════════════════════════════════════════════════
# 타이틀 페이지
# ══════════════════════════════════════════════════════════
if st.session_state.view == "title":
    _, rc = st.columns([2, 1])
    with rc:
        if user:
            st.markdown(f'<div class="user-id-display">👤 {user["name"]} ({user["id"]})</div>',
                        unsafe_allow_html=True)
            if st.button("로그아웃", key="logout_btn"):
                for k in list(st.session_state.keys()):
                    del st.session_state[k]
                st.rerun()
        else:
            with st.container():
                lid = st.text_input("이메일(ID)", key="login_id", placeholder="example@email.com")
                lpw = st.text_input("비밀번호", key="login_pw", type="password", placeholder="숫자 6자리")
                lc1, lc2 = st.columns(2)
                with lc1:
                    if st.button("로그인", key="login_btn", use_container_width=True, type="primary"):
                        u = login_user(lid.strip(), lpw.strip())
                        if u:
                            st.session_state.user = u
                            st.session_state.answers = {q["qid"]: 3 for q in get_questions()}
                            st.rerun()
                        else:
                            st.error("이메일 또는 비밀번호가 틀렸습니다.")
                with lc2:
                    if st.button("등록하기", key="reg_btn", use_container_width=True):
                        st.session_state.view = "register"
                        st.rerun()

    st.markdown("""
    <div class="title-page">
      <div class="title-deco"></div>
      <div class="title-badge">🌿 AI-Powered Self-Leadership Platform</div>
      <div class="title-main">셀프리더십 향상을 위한<br><em>AI MATE</em> 코칭 시스템</div>
      <div class="title-sub">ASLQ 기반 셀프리더십 진단부터 AI 롤모델 코칭,<br>
        성찰 일지, 사전–사후 비교까지 — 나를 이끄는 성장 여정</div>
      <div class="title-features">
        <div class="title-feat-item"><div class="feat-icon">🔍</div><div class="feat-text">ASLQ 진단</div></div>
        <div class="title-feat-item"><div class="feat-icon">🤝</div><div class="feat-text">AI 롤모델</div></div>
        <div class="title-feat-item"><div class="feat-icon">💬</div><div class="feat-text">1:1 코칭</div></div>
        <div class="title-feat-item"><div class="feat-icon">📖</div><div class="feat-text">3T 성찰</div></div>
        <div class="title-feat-item"><div class="feat-icon">📊</div><div class="feat-text">대시보드</div></div>
      </div>
    </div>
    <div class="title-author" style="text-align:center">Developed by <strong>Young</strong> · AI융합교육학과 박사과정</div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    _, cc, _ = st.columns([2, 1, 2])
    with cc:
        if user:
            if st.button("🌿  시작하기  →", type="primary", use_container_width=True, key="start"):
                st.session_state.view = "diagnosis"
                st.rerun()
        else:
            st.info("로그인 후 시작할 수 있습니다.")
    st.stop()


# ══════════════════════════════════════════════════════════
# 등록 화면
# ══════════════════════════════════════════════════════════
if st.session_state.view == "register":
    st.markdown('<div class="reg-section">', unsafe_allow_html=True)
    st.markdown('<div class="reg-title">회원 등록</div>', unsafe_allow_html=True)
    st.markdown('<div class="reg-sub">AI MATE를 이용하기 위해 간단한 정보를 등록해주세요.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    with st.form("reg_form"):
        r_email = st.text_input("이메일 (ID로 사용)", placeholder="example@email.com")
        r_pwd   = st.text_input("비밀번호 (숫자 6자리)", type="password", placeholder="123456")
        r_pwd2  = st.text_input("비밀번호 확인", type="password", placeholder="동일하게 입력")
        r_name  = st.text_input("이름 (한글 4자 / 영문 8자 이하)", placeholder="홍길동")
        r_gender = st.radio("성별", ["남", "여"], horizontal=True)
        r_age   = st.number_input("나이", min_value=10, max_value=99, value=25, step=1)
        r_phone = st.text_input("전화번호 (숫자만 입력)", placeholder="01012345678")
        submitted = st.form_submit_button("등록 완료", type="primary", use_container_width=True)

        if submitted:
            errors = []
            if not validate_email(r_email):
                errors.append("올바른 이메일 형식이 아닙니다.")
            elif not check_email_available(r_email):
                errors.append("이미 사용 중인 이메일입니다.")
            ok, msg = validate_pwd(r_pwd)
            if not ok:
                errors.append(msg)
            if r_pwd != r_pwd2:
                errors.append("비밀번호가 일치하지 않습니다.")
            if not validate_name(r_name):
                errors.append("이름: 한글 4자 또는 영문 8자 이하")
            phone = format_phone(r_phone)
            if len(re.sub(r'\D', '', r_phone)) not in (10, 11):
                errors.append("전화번호 형식 오류 (10~11자리)")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                ok, msg = register_user(r_email, r_pwd, r_name, r_gender, r_age, phone)
                if ok:
                    st.success("🎉 등록 완료! 로그인 화면으로 이동합니다.")
                    st.session_state.view = "title"
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(msg)

    if st.button("← 타이틀로 돌아가기"):
        st.session_state.view = "title"
        st.rerun()
    st.stop()


# re 모듈 import (등록 화면에서 사용)

# ══════════════════════════════════════════════════════════
# 사이드바
# ══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""<div class="brand-block"><div class="brand-icon">🌿</div>
      <div><div class="brand-title">AI MATE</div>
      <div class="brand-sub">Self-Leadership Platform</div></div></div>""", unsafe_allow_html=True)

    # 관리자 로그인
    st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)
    with st.expander("🔑 관리자 로그인", expanded=st.session_state.admin_logged):
        if st.session_state.admin_logged:
            st.success("관리자 모드 활성화")
            if st.button("관리자 로그아웃", key="admin_lo"):
                st.session_state.admin_logged = False
                st.session_state.view = "title"
                st.rerun()
        else:
            aid = st.text_input("관리자 ID", key="aid", placeholder="admin")
            apw = st.text_input("관리자 PW", type="password", key="apw", placeholder="비밀번호")
            if st.button("관리자 접속", key="admin_login"):
                if aid == ADMIN_ID and apw == ADMIN_PWD:
                    st.session_state.admin_logged = True
                    st.session_state.view = "admin"
                    st.rerun()
                else:
                    st.error("관리자 인증 실패")

    st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)

    if st.session_state.admin_logged:
        if st.button("📊 관리자 대시보드", key="nav_admin", use_container_width=True,
                     type="primary" if st.session_state.view == "admin" else "secondary"):
            st.session_state.view = "admin"
            st.rerun()

    if user:
        for vid, lbl in [("diagnosis", "◎  진단"), ("result", "◈  결과 리포트"),
                         ("mentor", "◉  멘토 코칭"), ("journal", "◇  성찰 일지"),
                         ("dashboard", "◆  성장 대시보드")]:
            active = st.session_state.view == vid
            if st.button(lbl, key=f"nav_{vid}", use_container_width=True,
                         type="primary" if active else "secondary"):
                st.session_state.view = vid
                st.rerun()
        st.markdown("---")
        if st.session_state.diagnosed:
            st.download_button("↓ CSV 내보내기", data=build_user_csv(st.session_state),
                               file_name=f"aiMate_{datetime.now():%Y%m%d}.csv",
                               mime="text/csv", use_container_width=True)

    st.markdown("---")
    if st.button("🏠 타이틀 페이지로", key="nav_title", use_container_width=True):
        st.session_state.view = "title"
        st.rerun()


# ══════════════════════════════════════════════════════════
# 관리자 화면
# ══════════════════════════════════════════════════════════
if st.session_state.view == "admin":
    if not st.session_state.admin_logged:
        st.warning("관리자 로그인이 필요합니다.")
        st.stop()

    st.markdown('<p class="eyebrow" style="color:#5a3d8a;">ADMIN DASHBOARD</p>', unsafe_allow_html=True)
    st.markdown("## 🛡️ AI MATE 관리자 대시보드")

    # 사용자수 + 나이별 통계
    m1, m2 = st.columns([1, 2])
    with m1:
        st.markdown(f'<div class="admin-card"><div class="admin-title">등록 사용자 수</div>'
                    f'<div style="font-size:48px;font-weight:700;color:#5a3d8a;">{get_user_count()}</div>'
                    f'<div style="font-size:12px;color:#9e9e9e;">명</div></div>', unsafe_allow_html=True)
    with m2:
        age_dist = get_age_distribution()
        fig_age = go.Figure(go.Bar(x=list(age_dist.keys()), y=list(age_dist.values()),
                                   marker_color="#7c5cbf"))
        fig_age.update_layout(height=250, margin=dict(l=20, r=20, t=10, b=30),
                              paper_bgcolor="white", plot_bgcolor="white",
                              xaxis_title="연령대", yaxis_title="인원수")
        st.plotly_chart(fig_age, use_container_width=True)

    st.markdown("---")

    # 사용자 관리
    st.markdown("### 👥 사용자 관리")
    users = get_all_users()
    if users:
        tab_list, tab_diag, tab_pwd = st.tabs(["사용자 목록", "개별 진단 조회", "비밀번호 초기화"])
        with tab_list:
            df = pd.DataFrame(users)[["idx", "id", "name", "gender", "age", "phone", "created_at"]]
            df.columns = ["No", "이메일", "이름", "성별", "나이", "전화번호", "등록일"]
            st.dataframe(df, use_container_width=True, hide_index=True)

        with tab_diag:
            sel = st.selectbox("사용자 선택",
                               [f"{u['name']} ({u['id']})" for u in users], key="diag_sel")
            idx = [f"{u['name']} ({u['id']})" for u in users].index(sel)
            uid = users[idx]["idx"]
            surveys = get_user_surveys(uid)
            if surveys:
                for s in surveys:
                    lb, _ = interpretation(s["overall"])
                    st.markdown(f"""<div class="admin-card">
                      <strong>{s['created_at']}</strong> | 전체 {s['overall']:.1f}점 ({lb})
                      | 행동 {s['behavior']:.1f} | 의미 {s['natural_reward']:.1f}
                      | 사고 {s['constructive_thought']:.1f}
                      | {'📌 사후' if s['is_post'] else '사전'}</div>""", unsafe_allow_html=True)
            else:
                st.info("진단 기록이 없습니다.")

        with tab_pwd:
            sel2 = st.selectbox("사용자 선택",
                                [f"{u['name']} ({u['id']})" for u in users], key="pwd_sel")
            idx2 = [f"{u['name']} ({u['id']})" for u in users].index(sel2)
            uid2 = users[idx2]["idx"]
            if st.button("비밀번호를 000000으로 초기화", key="pwd_reset"):
                reset_user_pwd(uid2, "000000")
                st.success(f"{users[idx2]['name']}의 비밀번호가 000000으로 초기화되었습니다.")
    else:
        st.info("등록된 사용자가 없습니다.")

    st.markdown("---")

    # 전체 진단 통계
    st.markdown("### 📈 전체 진단 결과 통계")
    all_surveys = get_all_surveys()
    if all_surveys:
        df_s = pd.DataFrame(all_surveys)
        fig_box = go.Figure()
        for col, nm, clr in [("behavior", "행동중심", "#2a6658"),
                              ("natural_reward", "자연적 보상", "#b8870a"),
                              ("constructive_thought", "건설적 사고", "#c25a3d")]:
            if col in df_s.columns:
                fig_box.add_trace(go.Box(y=df_s[col], name=nm, marker_color=clr))
        fig_box.update_layout(height=350, title="요인별 점수 분포 (Box Plot)",
                              margin=dict(l=40, r=20, t=50, b=30),
                              paper_bgcolor="white", plot_bgcolor="#fafafa")
        st.plotly_chart(fig_box, use_container_width=True)

        if "name" in df_s.columns:
            df_latest = df_s.sort_values("created_at").groupby("name").last().reset_index()
            fig_bar = go.Figure(go.Bar(x=df_latest["name"], y=df_latest["overall"],
                                       marker_color="#5a3d8a"))
            fig_bar.update_layout(height=300, title="사용자별 최근 전체 점수",
                                  xaxis_title="사용자", yaxis_title="점수", yaxis_range=[0, 5],
                                  margin=dict(l=40, r=20, t=50, b=50),
                                  paper_bgcolor="white", plot_bgcolor="#fafafa")
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("진단 데이터가 없습니다.")

    st.markdown("---")

    # 문항 관리
    st.markdown("### 📝 진단 문항 관리")
    qs = get_all_questions_admin()
    for q in qs:
        with st.expander(f"{'✅' if q['active'] else '❌'} [{q['qid']}] {q['text'][:40]}…"):
            nf = st.selectbox("요인", ["behavior", "natural", "thought"],
                              index=["behavior", "natural", "thought"].index(q["factor"]),
                              key=f"qf_{q['qid']}")
            nt = st.text_area("문항 내용", value=q["text"], key=f"qt_{q['qid']}")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("저장", key=f"qs_{q['qid']}"):
                    update_question(q["qid"], nf, nt)
                    st.success("수정 완료")
                    st.rerun()
            with c2:
                new_active = not q["active"]
                lbl = "활성화" if new_active else "비활성화"
                if st.button(lbl, key=f"qa_{q['qid']}"):
                    toggle_question(q["qid"], new_active)
                    st.rerun()

    st.markdown("##### ➕ 새 문항 추가")
    with st.form("add_q", clear_on_submit=True):
        nqid = st.text_input("문항 ID (예: D1)")
        nqfac = st.selectbox("요인", ["behavior", "natural", "thought"])
        nqtxt = st.text_area("문항 내용")
        if st.form_submit_button("추가"):
            if nqid and nqtxt:
                add_question(nqid, nqfac, nqtxt)
                st.success(f"{nqid} 추가 완료")
                st.rerun()

    st.markdown("---")
    csv_data = build_csv_all()
    if csv_data:
        st.download_button("📥 전체 진단 결과 CSV 다운로드", data=csv_data,
                           file_name=f"aiMate_all_{datetime.now():%Y%m%d}.csv",
                           mime="text/csv", use_container_width=True)
    st.stop()


# ══════════════════════════════════════════════════════════
# 로그인 필수
# ══════════════════════════════════════════════════════════
if not user:
    st.warning("로그인이 필요합니다.")
    if st.button("타이틀 페이지로"):
        st.session_state.view = "title"
        st.rerun()
    st.stop()


# ══════════════════════════════════════════════════════════
# 메인 헤더
# ══════════════════════════════════════════════════════════
ch1, ch2 = st.columns([3, 1])
with ch1:
    st.markdown('<p class="eyebrow">AI-powered Self-Leadership Growth Platform</p>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">나를 이끄는 AI MATE</h1>', unsafe_allow_html=True)
with ch2:
    if st.session_state.diagnosed and st.session_state.scores:
        sc = st.session_state.scores["overall"]
        st.markdown(f'<div class="score-hero"><div class="score-hero-label">전체 평균</div>'
                    f'<div class="score-hero-num">{sc:.1f}<span>/5.0</span></div></div>',
                    unsafe_allow_html=True)
st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)

view = st.session_state.view


# ══════════════════════════════════════════════════════════
# 진단
# ══════════════════════════════════════════════════════════
if view == "diagnosis":
    st.markdown('<p class="eyebrow-coral">Self-Leadership Diagnosis · ASLQ</p>', unsafe_allow_html=True)
    st.subheader("셀프리더십 진단")
    questions = get_questions()
    FC = {"behavior": ("#2a6658", "행동중심전략", "목표 설정·실행 조절"),
          "natural": ("#b8870a", "자연적 보상전략", "내적 동기·의미 발견"),
          "thought": ("#c25a3d", "건설적 사고패턴전략", "긍정 자기대화·이미지화")}
    pill_bg = {1: "#fce8e2", 2: "#fdf3d9", 3: "#f0f4f0", 4: "#e0f0ec", 5: "#c8e6c9"}
    pill_fg = {1: "#c25a3d", 2: "#b8870a", 3: "#5a7a5e", 4: "#2a6658", 5: "#1b5e20"}

    for fk, (color, fname, fdesc) in FC.items():
        qs = [q for q in questions if q["factor"] == fk]
        if not qs:
            continue
        st.markdown(f'<div class="factor-section-header" style="border-color:{color};">'
                    f'<span style="width:12px;height:12px;border-radius:50%;background:{color};'
                    f'display:inline-block;"></span>'
                    f'<span class="factor-section-title" style="color:{color};">{fname}</span>'
                    f'<span class="factor-section-desc">{fdesc}</span></div>', unsafe_allow_html=True)
        for q in qs:
            qid = q["qid"]
            text = q["text"]
            if qid not in st.session_state.answers:
                st.session_state.answers[qid] = 3
            c_card, c_sl = st.columns([3, 2])
            with c_card:
                st.markdown(f'<div class="q-row-card" style="border-left:4px solid {color};">'
                            f'<span class="q-row-num" style="float:right;">{qid}</span>'
                            f'<div class="q-row-text">{text}</div></div>', unsafe_allow_html=True)
            with c_sl:
                val = st.slider(f"{qid}번 문항", 1, 5, st.session_state.answers[qid],
                                key=f"sq_{qid}", label_visibility="collapsed")
                st.session_state.answers[qid] = val
                st.markdown(f'<div style="text-align:right;"><span style="display:inline-flex;'
                            f'align-items:center;justify-content:center;min-width:40px;height:40px;'
                            f'border-radius:10px;background:{pill_bg.get(val, "#f0f4f0")};'
                            f'color:{pill_fg.get(val, "#2a6658")};font-weight:800;font-size:16px;">'
                            f'{val}점</span></div>', unsafe_allow_html=True)

    st.markdown("---")
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        issue = st.selectbox("고민 분야", ISSUE_OPTIONS,
                             index=ISSUE_OPTIONS.index(st.session_state.issue))
        st.session_state.issue = issue
    with c2:
        tone = st.selectbox("코칭 스타일", TONE_OPTIONS,
                            index=TONE_OPTIONS.index(st.session_state.tone))
        st.session_state.tone = tone
    with c3:
        st.markdown('<div style="height:28px"></div>', unsafe_allow_html=True)
        if st.button("진단 결과 보기 →", type="primary", use_container_width=True):
            scores = calc_scores(st.session_state.answers)
            rm = choose_role_model(scores, st.session_state.tone, st.session_state.issue)
            st.session_state.scores = scores
            st.session_state.role_model = rm
            st.session_state.diagnosed = True
            if st.session_state.pre_score is None:
                st.session_state.pre_score = scores["overall"]
            sid = save_survey(user["idx"], st.session_state.issue, st.session_state.tone,
                              st.session_state.answers, scores, rm, 0)
            st.session_state.survey_id = sid
            st.session_state.chat = []
            st.session_state.view = "result"
            st.rerun()


# ══════════════════════════════════════════════════════════
# 결과 리포트
# ══════════════════════════════════════════════════════════
elif view == "result":
    st.markdown('<p class="eyebrow-coral">Result Report</p>', unsafe_allow_html=True)
    st.subheader("요인별 점수와 해석")
    if not st.session_state.diagnosed:
        st.info("먼저 진단을 완료해주세요.")
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
        low = scores["lowest"]
        fi = FACTORS[low]
        ci1, ci2, ci3 = st.columns(3)
        for col, icon, title, body in [
            (ci1, "🎯", "취약 요인", f"{fi['label']} ({scores[low]:.1f}점)"),
            (ci2, "✨", fi["insight_title"], fi["insight_desc"]),
            (ci3, "📋", "실천과제", fi["action_task"]),
        ]:
            with col:
                st.markdown(f'<div class="insight-card"><div class="i-icon">{icon}</div>'
                            f'<div class="i-title">{title}</div>'
                            f'<div class="i-body">{body}</div></div>', unsafe_allow_html=True)

        st.markdown("---")
        bc1, bc2 = st.columns(2)
        with bc1:
            if st.button("📥 사후진단으로 저장", use_container_width=True):
                st.session_state.post_score = scores["overall"]
                save_survey(user["idx"], st.session_state.issue, st.session_state.tone,
                            st.session_state.answers, scores, st.session_state.role_model, 1)
                st.success(f"사후진단 점수({scores['overall']:.1f}점) 저장!")
        with bc2:
            try:
                pdf_bytes = generate_pdf(user, scores)
                fname = f"{user['name']}({user['id']}).pdf"
                st.download_button("📄 진단결과 PDF 다운로드", data=pdf_bytes,
                                   file_name=fname, mime="application/pdf",
                                   use_container_width=True)
            except Exception as e:
                st.warning(f"PDF 생성 오류: {e}\n`pip install fpdf2` 실행 후 재시도하세요.")


# ══════════════════════════════════════════════════════════
# 멘토 코칭
# ══════════════════════════════════════════════════════════
elif view == "mentor":
    st.markdown('<p class="eyebrow-coral">AI Coaching Room</p>', unsafe_allow_html=True)
    st.subheader("AI 롤모델 매칭")
    if not st.session_state.diagnosed:
        st.info("먼저 진단을 완료해주세요.")
    else:
        scores = st.session_state.scores
        rm = st.session_state.role_model
        low = scores["lowest"]
        cp, cc = st.columns([1, 2])
        with cp:
            render_mentor_card(rm, low, st.session_state)
            render_mission_box(FACTORS[low]["action_task"])
        with cc:
            if len(st.session_state.chat) == 0:
                opening = (f"**{rm[0]}** 의 가치에서 영감을 받은 AI 코칭 롤모델입니다.\n\n"
                           f"진단 결과, **{FACTORS[low]['label']}** 점수({scores[low]:.1f}점)가 "
                           f"낮게 나타났어요. 가장 마음에 걸리는 일을 알려주세요. 🌱")
                st.session_state.chat.append({"role": "assistant", "content": opening})
                save_chat(st.session_state.survey_id, "assistant", opening)
            chat_box = st.container(height=420)
            with chat_box:
                for msg in st.session_state.chat:
                    with st.chat_message(msg["role"],
                                         avatar="🌿" if msg["role"] == "assistant" else "🙋"):
                        st.markdown(msg["content"])
            ui = st.chat_input("고민을 적어보세요…")
            if ui:
                st.session_state.chat.append({"role": "user", "content": ui})
                save_chat(st.session_state.survey_id, "user", ui)
                with st.spinner("응답 작성 중..."):
                    reply = get_ai_reply(st.session_state.chat, rm, scores,
                                         st.session_state.issue, st.session_state.tone)
                st.session_state.chat.append({"role": "assistant", "content": reply})
                save_chat(st.session_state.survey_id, "assistant", reply)
                st.rerun()


# ══════════════════════════════════════════════════════════
# 성찰 일지
# ══════════════════════════════════════════════════════════
elif view == "journal":
    st.markdown('<p class="eyebrow-coral">Reflection Journal · 3T Model</p>', unsafe_allow_html=True)
    st.subheader("오늘의 실천과 성찰")
    cf, cl = st.columns([1, 1])
    with cf:
        st.markdown("""<div class="three-t-box">
          <div class="t-row"><span class="t-tag">Task</span><span class="t-desc">어떤 과제를 수행했나요?</span></div>
          <div class="t-row"><span class="t-tag">Trigger</span><span class="t-desc">내면의 변화나 깨달음은?</span></div>
          <div class="t-row"><span class="t-tag">Transform</span><span class="t-desc">내일의 다짐은 무엇인가요?</span></div>
        </div>""", unsafe_allow_html=True)
        with st.form("journal_form", clear_on_submit=True):
            action = st.text_input("오늘 실행한 작은 행동", placeholder="예: 내일 할 일 1개 정하기")
            refl = st.text_area("성찰 기록", placeholder="Task→Trigger→Transform 순서로 작성", height=180)
            if st.form_submit_button("성찰 저장 ✓", type="primary", use_container_width=True):
                if action.strip() and refl.strip():
                    save_journal(user["idx"], action.strip(), refl.strip())
                    st.success("저장 완료! 🌱")
                    st.rerun()
                else:
                    st.warning("모두 입력해주세요.")
    with cl:
        st.markdown("#### 📖 성찰 기록")
        journals = get_journals(user["idx"])
        if not journals:
            st.markdown('<div class="empty-state">아직 기록이 없습니다.</div>', unsafe_allow_html=True)
        else:
            for j in journals:
                render_journal_entry(j)


# ══════════════════════════════════════════════════════════
# 성장 대시보드
# ══════════════════════════════════════════════════════════
elif view == "dashboard":
    st.markdown('<p class="eyebrow-coral">My Growth Dashboard</p>', unsafe_allow_html=True)
    st.subheader("성장 변화와 연구 로그")
    if not st.session_state.diagnosed:
        st.info("먼저 진단을 완료해주세요.")
    else:
        scores = st.session_state.scores
        journals = get_journals(user["idx"])
        render_dashboard_metrics(scores, journals, get_chat_count(),
                                  st.session_state.pre_score, st.session_state.post_score)
        st.markdown("---")
        dc, dt = st.columns([1, 1])
        with dc:
            st.markdown("#### 📊 요인별 점수")
            for key, info in FACTORS.items():
                s = scores[key]
                pct = int(s / 5 * 100)
                color = info["color"]
                st.markdown(f'<div class="fbar-row"><div class="fbar-label">{info["short"]}</div>'
                            f'<div class="fbar-track"><div class="fbar-fill" style="width:{pct}%;'
                            f'background:{color};"></div></div>'
                            f'<div class="fbar-val">{s:.1f}</div></div>', unsafe_allow_html=True)
        with dt:
            st.markdown("#### 🗂 나의 진단 이력")
            my_surveys = get_user_surveys(user["idx"])
            for s in my_surveys[:10]:
                lb, _ = interpretation(s["overall"])
                st.markdown(f'<div class="tl-item"><div class="tl-label">'
                            f'{"📌사후" if s["is_post"] else "사전"}</div>'
                            f'<div class="tl-body">{s["created_at"][:16]} | '
                            f'{s["overall"]:.1f}점 ({lb})</div></div>', unsafe_allow_html=True)
