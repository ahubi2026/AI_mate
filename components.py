# ============================================================
#  components.py — 재사용 UI 컴포넌트
#  레이더 차트 / 점수 막대 / 롤모델 카드 / 일지 항목 / 대시보드 메트릭
# ============================================================

import streamlit as st
import plotly.graph_objects as go

from config import FACTORS
from logic  import interpretation


# ── 레이더 차트 ───────────────────────────────────────────
def render_radar_chart(scores: dict) -> go.Figure:
    keys   = list(FACTORS.keys())
    labels = [FACTORS[k]["label"] for k in keys]
    vals   = [scores[k] for k in keys]
    vals   += [vals[0]];  labels += [labels[0]]   # 닫기

    fig = go.Figure()
    # 격자 배경
    fig.add_trace(go.Scatterpolar(
        r=[5,5,5,5], theta=labels[:-1], fill="toself",
        fillcolor="rgba(0,0,0,0.02)",
        line=dict(color="rgba(0,0,0,0.1)", width=1),
        showlegend=False, hoverinfo="skip"
    ))
    # 데이터
    fig.add_trace(go.Scatterpolar(
        r=vals, theta=labels, fill="toself",
        fillcolor="rgba(42,102,88,0.18)",
        line=dict(color="#2a6658", width=2.5),
        marker=dict(size=7, color="#2a6658"),
        showlegend=False,
        hovertemplate="%{theta}<br>%{r:.1f}점<extra></extra>"
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, range=[0,5],
                tickfont=dict(size=10, color="#9e9e9e"),
                gridcolor="rgba(0,0,0,0.07)",
                tickvals=[1,2,3,4,5]
            ),
            angularaxis=dict(tickfont=dict(size=12, color="#2a6658", family="Noto Sans KR")),
            bgcolor="white"
        ),
        paper_bgcolor="white",
        margin=dict(l=50, r=50, t=30, b=30),
        height=320
    )
    return fig


# ── 요인별 점수 막대 ──────────────────────────────────────
def render_score_bars(scores: dict):
    color_map = {"behavior":"#2a6658","natural":"#b8870a","thought":"#c25a3d"}
    for key, info in FACTORS.items():
        s = scores[key]; pct = int(s / 5 * 100)
        label, cls = interpretation(s); color = color_map[key]
        st.markdown(f"""
        <div class="score-row-wrap">
          <div class="score-row-header">
            <span class="score-row-name">{info['label']}</span>
            <span>
              <span class="score-num-lg">{s:.1f}</span>
              <span class="interp-pill {cls}">{label}</span>
            </span>
          </div>
          <p style="font-size:12.5px;color:#737373;margin:4px 0 8px;line-height:1.5;">{info['description']}</p>
          <div style="height:6px;background:rgba(0,0,0,.08);border-radius:3px;overflow:hidden;">
            <div style="height:100%;width:{pct}%;background:{color};border-radius:3px;"></div>
          </div>
        </div>""", unsafe_allow_html=True)


# ── 롤모델 프로필 카드 ────────────────────────────────────
def render_mentor_card(role_model: tuple, low: str, ss: dict):
    name, role, summary, era, tags = role_model
    low_label  = FACTORS[low]["label"]
    issue      = ss.get("issue", "")
    tone       = ss.get("tone", "")
    tags_html  = "".join(f'<span class="mentor-tag">{t}</span>' for t in tags[:3])
    extra_tags = (f'<span class="mentor-tag">{low_label}</span>'
                  f'<span class="mentor-tag">{issue}</span>'
                  f'<span class="mentor-tag">{tone}</span>')
    st.markdown(f"""
    <div class="mentor-card-wrap">
      <div class="mentor-avatar">{name[0]}</div>
      <div>
        <div class="mentor-name">{name}</div>
        <div class="mentor-role">{role} · {era}</div>
      </div>
      <div style="clear:both;margin-top:12px;">{extra_tags}</div>
      <p class="mentor-desc">
        {name}의 삶의 궤적과 가치에서 영감을 받은 AI 코칭 롤모델입니다.<br>
        실제 인물의 발언을 사칭하지 않으며, 진단 결과에 맞춘 코칭 관점만 제공합니다.
      </p>
      <p class="mentor-desc"><strong style="color:#1a1a1a;">매칭 이유</strong><br>{summary}</p>
      <div style="margin-top:6px;">{tags_html}</div>
    </div>""", unsafe_allow_html=True)


def render_mission_box(action_task: str):
    st.markdown(f"""
    <div class="mission-box">
      <div class="mission-label">📋 오늘의 실천과제</div>
      <p class="mission-body">{action_task}</p>
    </div>""", unsafe_allow_html=True)


# ── 성찰 일지 항목 ────────────────────────────────────────
def render_journal_entry(entry: dict):
    st.markdown(f"""
    <div class="journal-entry-wrap">
      <div class="je-time">{entry.get('created_at','')}</div>
      <div class="je-action">{entry.get('action','')}</div>
      <div class="je-body">{entry.get('reflection','')}</div>
    </div>""", unsafe_allow_html=True)


# ── 대시보드 메트릭 카드 ──────────────────────────────────
def render_dashboard_metrics(scores: dict, journals: list,
                              chat_count: int,
                              pre_score, post_score):
    overall = scores["overall"]
    if pre_score is not None and post_score is not None:
        diff        = post_score - pre_score
        change_str  = f"{'+' if diff >= 0 else ''}{diff:.1f}"
        change_cls  = "change"
    else:
        change_str = "대기"; change_cls = ""

    col1, col2, col3, col4 = st.columns(4)
    for col, lbl, num, sub, cls in [
        (col1, "전체 평균 점수",  f"{overall:.1f}", "/5.0",   ""),
        (col2, "성찰 기록 수",    str(len(journals)), "건",   ""),
        (col3, "멘토 대화 수",    str(chat_count),    "회",   ""),
        (col4, "사전→사후 변화",  change_str,       "점 변화", change_cls),
    ]:
        with col:
            st.markdown(f"""
            <div class="metric-wrap">
              <div class="metric-label">{lbl}</div>
              <div class="metric-num {cls}">{num}</div>
              <div class="metric-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)
