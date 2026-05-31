# ============================================================
#  styles.py — 전체 커스텀 CSS 주입
# ============================================================

import streamlit as st


def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap');

/* ── 전역 ── */
*,*::before,*::after{box-sizing:border-box;}
html,body,[class*="css"]{font-family:'Noto Sans KR',-apple-system,sans-serif;color:#1a1a1a;}
.block-container{padding-top:1.2rem!important;max-width:1200px!important;}
section[data-testid="stSidebar"]>div{padding-top:1rem!important;}

/* ── 사이드바 ── */
section[data-testid="stSidebar"]{background:#1c2623!important;}
section[data-testid="stSidebar"] *{color:rgba(255,255,255,0.85)!important;}
section[data-testid="stSidebar"] button{background:transparent!important;border:none!important;
  text-align:left!important;border-radius:8px!important;padding:10px 14px!important;
  font-size:13.5px!important;transition:background .15s!important;color:rgba(255,255,255,.6)!important;}
section[data-testid="stSidebar"] button[kind="primary"]{background:rgba(90,122,94,.3)!important;
  color:#a8c9ac!important;font-weight:600!important;}
section[data-testid="stSidebar"] button:hover{background:rgba(255,255,255,.08)!important;color:white!important;}
.nav-divider{border-top:1px solid rgba(255,255,255,.1);margin:8px 0;}

/* ── 브랜드 ── */
.brand-block{display:flex;align-items:center;gap:12px;padding:8px 0 16px;}
.brand-icon{width:42px;height:42px;border-radius:10px;background:#2a6658;
  display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0;}
.brand-title{font-size:16px;font-weight:700;color:white;}
.brand-sub{font-size:11px;color:rgba(255,255,255,.5);margin-top:2px;}

/* ── 연구 배지 ── */
.research-badge{padding:12px;border-radius:8px;background:rgba(255,255,255,.06);
  border:1px solid rgba(255,255,255,.12);margin-bottom:12px;}
.badge-label{font-size:11px!important;font-weight:700!important;color:#8fac93!important;margin-bottom:4px;}
.badge-body{font-size:12px!important;color:rgba(255,255,255,.5)!important;line-height:1.5;}

/* ── 헤더 ── */
.eyebrow{font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#2a6658;margin-bottom:4px;}
.eyebrow-coral{font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#c25a3d;margin-bottom:4px;}
.main-title{font-family:'DM Serif Display','Noto Serif KR',serif!important;
  font-size:clamp(26px,4vw,40px)!important;font-weight:400!important;line-height:1.1!important;
  color:#1a1a1a!important;margin:0!important;}
.section-divider{border:none;border-top:1px solid rgba(0,0,0,.08);margin:12px 0 20px;}

/* ── 점수 히어로 ── */
.score-hero{text-align:right;padding:12px 0;}
.score-hero-label{font-size:11px;font-weight:700;color:#737373;letter-spacing:.06em;text-transform:uppercase;}
.score-hero-num{font-family:'DM Serif Display',serif;font-size:42px;font-weight:400;color:#2a6658;line-height:1;}
.score-hero-num span{font-size:16px;color:#9e9e9e;margin-left:2px;}

/* ── 인사이트 카드 ── */
.insight-card{background:#fff;border:1px solid rgba(0,0,0,.08);border-radius:12px;padding:20px;height:100%;}
.i-icon{font-size:22px;margin-bottom:8px;}
.i-title{font-size:14px;font-weight:700;color:#1a1a1a;margin-bottom:6px;}
.i-body{font-size:13px;color:#737373;line-height:1.6;}

/* ── 점수 행 ── */
.score-row-wrap{background:#fff;border:1px solid rgba(0,0,0,.08);border-radius:10px;padding:16px;margin-bottom:10px;}
.score-row-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;}
.score-row-name{font-size:14px;font-weight:700;}
.score-num-lg{font-family:'DM Serif Display',serif;font-size:22px;color:#2a6658;}
.interp-pill{display:inline-block;font-size:11px;font-weight:700;padding:3px 10px;border-radius:999px;margin-left:6px;}
.interp-strong{background:#e0f0ec;color:#2a6658;}
.interp-ok{background:#e8f0e9;color:#5a7a5e;}
.interp-grow{background:#fdf3d9;color:#b8870a;}
.interp-need{background:#fce8e2;color:#c25a3d;}

/* ── 롤모델 카드 ── */
.mentor-card-wrap{background:#fff;border:1px solid rgba(0,0,0,.08);border-radius:14px;padding:22px;margin-bottom:14px;}
.mentor-avatar{width:68px;height:68px;border-radius:10px;background:#e8f0e9;
  display:flex;align-items:center;justify-content:center;
  font-family:'DM Serif Display',serif;font-size:26px;color:#2a6658;float:left;margin-right:14px;}
.mentor-name{font-family:'DM Serif Display',serif;font-size:22px;font-weight:400;color:#1a1a1a;}
.mentor-role{font-size:12px;color:#737373;margin-top:3px;}
.mentor-tag{display:inline-block;font-size:11px;font-weight:700;padding:4px 10px;
  border-radius:999px;background:#e8f0e9;color:#5a7a5e;margin:3px 3px 0 0;}
.mentor-desc{font-size:13px;color:#737373;line-height:1.6;clear:both;margin-top:12px;}

/* ── 미션 박스 ── */
.mission-box{background:#fdf3d9;border:1px solid rgba(184,135,10,.2);border-radius:10px;padding:14px;}
.mission-label{font-size:10.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#b8870a;margin-bottom:6px;}
.mission-body{font-size:13px;color:#7a5c00;line-height:1.6;}

/* ── 3T 가이드 ── */
.three-t-box{border:1px solid rgba(0,0,0,.08);border-radius:10px;overflow:hidden;margin-bottom:18px;}
.t-row{display:flex;align-items:flex-start;gap:12px;padding:11px 14px;border-bottom:1px solid rgba(0,0,0,.06);}
.t-row:last-child{border-bottom:none;}
.t-tag{font-size:10.5px;font-weight:700;padding:3px 8px;border-radius:4px;
  background:#2a6658;color:white;white-space:nowrap;margin-top:1px;}
.t-desc{font-size:12.5px;color:#737373;}

/* ── 성찰 일지 ── */
.journal-entry-wrap{background:#fff;border:1px solid rgba(0,0,0,.08);border-radius:10px;padding:15px 18px;margin-bottom:10px;}
.je-time{font-size:11px;font-weight:700;color:#c25a3d;}
.je-action{font-size:14px;font-weight:600;color:#1a1a1a;margin:6px 0;}
.je-body{font-size:13px;color:#737373;line-height:1.6;}

/* ── 대시보드 메트릭 ── */
.metric-wrap{background:#fff;border:1px solid rgba(0,0,0,.08);border-radius:12px;padding:18px;text-align:center;}
.metric-label{font-size:12px;font-weight:600;color:#737373;letter-spacing:.03em;margin-bottom:6px;}
.metric-num{font-family:'DM Serif Display',serif;font-size:40px;font-weight:400;color:#2a6658;line-height:1;}
.metric-num.change{color:#c25a3d;}
.metric-sub{font-size:12px;color:#9e9e9e;margin-top:4px;}

/* ── 요인 막대 ── */
.fbar-row{display:flex;align-items:center;gap:12px;margin-bottom:14px;}
.fbar-label{font-size:12.5px;font-weight:600;color:#3d3d3d;width:40px;flex-shrink:0;}
.fbar-track{flex:1;height:8px;background:rgba(0,0,0,.08);border-radius:4px;overflow:hidden;}
.fbar-fill{height:100%;border-radius:4px;}
.fbar-val{font-size:13px;font-weight:700;color:#2a6658;width:28px;text-align:right;flex-shrink:0;}

/* ── 타임라인 ── */
.tl-item{display:flex;gap:14px;padding:10px 0;border-bottom:1px solid rgba(0,0,0,.06);}
.tl-item:last-child{border-bottom:none;}
.tl-label{font-size:12px;font-weight:700;color:#9e9e9e;width:80px;flex-shrink:0;}
.tl-body{font-size:12.5px;color:#3d3d3d;line-height:1.5;}

/* ── 빈 상태 ── */
.empty-state{padding:28px;text-align:center;color:#9e9e9e;font-size:13.5px;
  border:1px dashed rgba(0,0,0,.12);border-radius:10px;line-height:1.7;}

/* ── 타이틀 페이지 ── */
.title-page{min-height:88vh;background:linear-gradient(135deg,#e8f5e9 0%,#e0f2f1 30%,#e8eaf6 60%,#f3e5f5 100%);
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  text-align:center;padding:60px 20px;position:relative;overflow:hidden;}
.title-deco{position:absolute;top:0;left:0;right:0;bottom:0;
  background:radial-gradient(circle at 20% 20%,rgba(129,199,132,.25) 0%,transparent 50%),
             radial-gradient(circle at 80% 80%,rgba(149,117,205,.2)  0%,transparent 50%),
             radial-gradient(circle at 60% 10%,rgba(77,182,172,.18)  0%,transparent 40%);
  pointer-events:none;}
.title-badge{display:inline-block;background:rgba(42,102,88,.12);border:1px solid rgba(42,102,88,.3);
  color:#2a6658;font-size:12px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;
  padding:7px 20px;border-radius:999px;margin-bottom:28px;}
.title-main{font-family:'DM Serif Display','Noto Serif KR',serif;
  font-size:clamp(28px,5vw,52px);font-weight:400;line-height:1.25;
  color:#1a2e2a;margin-bottom:20px;letter-spacing:-.01em;}
.title-main em{font-style:normal;color:#2a6658;}
.title-sub{font-size:clamp(14px,2vw,17px);color:#5a7a6a;line-height:1.7;
  margin-bottom:48px;max-width:540px;}
.title-features{display:flex;gap:16px;flex-wrap:wrap;justify-content:center;margin-bottom:52px;}
.title-feat-item{background:rgba(255,255,255,.7);border:1px solid rgba(42,102,88,.15);
  border-radius:12px;padding:14px 20px;font-size:13px;color:#2a4a3a;
  backdrop-filter:blur(4px);min-width:140px;}
.title-feat-item .feat-icon{font-size:20px;margin-bottom:6px;}
.title-feat-item .feat-text{font-weight:600;}
.title-author{font-size:13px;color:#8aaa9a;letter-spacing:.06em;margin-top:12px;}
.title-author strong{color:#5a7a6a;}

/* ── 진단 섹션 헤더 ── */
.factor-section-header{display:flex;align-items:center;gap:12px;
  padding:14px 0 8px;margin-top:8px;border-bottom:2px solid;margin-bottom:16px;}
.factor-section-title{font-size:15px;font-weight:700;}
.factor-section-desc{font-size:12.5px;color:#737373;margin-left:auto;}

/* ── 진단 문항 카드 ── */
.q-row-card{background:#fff;border:1px solid rgba(0,0,0,.07);border-radius:14px;
  padding:20px 24px;margin-bottom:12px;transition:box-shadow .15s;}
.q-row-card:hover{box-shadow:0 4px 16px rgba(0,0,0,.08);}
.q-row-num{font-size:11px;font-weight:800;color:#9e9e9e;letter-spacing:.06em;}
.q-row-dot{width:10px;height:10px;border-radius:50%;}
.q-row-text{font-size:15px;line-height:1.65;color:#1a1a1a;font-weight:500;margin-bottom:8px;}

/* ── Streamlit 기본 버튼 재정의 ── */
div[data-testid="stButton"]>button[kind="primary"]{background:#2a6658!important;
  border:none!important;border-radius:8px!important;font-weight:600!important;padding:10px 20px!important;}
div[data-testid="stButton"]>button[kind="primary"]:hover{background:#5a7a5e!important;}
</style>
""", unsafe_allow_html=True)
