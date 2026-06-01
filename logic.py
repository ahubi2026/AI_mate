# logic.py — 점수 계산 / 해석 / 롤모델 매칭 / AI 응답 / CSV / PDF
import os, csv, io, re, json
from datetime import datetime
from config import FACTORS, ROLE_MODELS, TONE_OPTIONS, ISSUE_OPTIONS
from database import get_chat_count, get_journals, get_questions

def calc_scores(answers):
    questions = get_questions()
    by_factor = {}
    for fk in FACTORS:
        ids  = [q["qid"] for q in questions if q["factor"] == fk]
        vals = [answers.get(qid, 3) for qid in ids]
        by_factor[fk] = round(sum(vals)/len(vals), 1) if vals else 3.0
    overall = round(sum(by_factor.values())/len(by_factor), 1)
    lowest  = min(by_factor, key=by_factor.get)
    return {**by_factor, "overall": overall, "lowest": lowest}

def interpretation(score):
    if score >= 4.1: return "강점 영역","interp-strong"
    if score >= 3.1: return "보통 이상","interp-ok"
    if score >= 2.1: return "성장 필요","interp-grow"
    return "우선 개입 필요","interp-need"

def choose_role_model(scores, tone, issue):
    pool = ROLE_MODELS[scores["lowest"]]
    ti = TONE_OPTIONS.index(tone) if tone in TONE_OPTIONS else 0
    ii = ISSUE_OPTIONS.index(issue) if issue in ISSUE_OPTIONS else 0
    return pool[(ti+ii)%len(pool)]

def get_ai_reply(chat_history, role_model, scores, issue, tone):
    import streamlit as st
    name = role_model[0]; low = scores["lowest"]; factor = FACTORS[low]
    system = (f"당신은 {name}의 삶의 궤적과 가치철학을 깊이 연구하여 구성된 AI 코칭 롤모델입니다.\n"
              "실제 인물의 발언을 직접 인용하거나 사칭하지 않습니다.\n"
              f'사용자는 현재 "{factor["label"]}" 역량이 취약한 성인으로, "{issue}" 분야의 고민이 있습니다.\n'
              f'코칭 스타일: "{tone}"\n코칭 흐름: 1)공감 → 2)사고 전환 → 3)오늘 실행 가능한 행동 제안.\n'
              "4~6문장 이내 한국어로 답하세요.")
    messages = [{"role":m["role"],"content":m["content"]} for m in chat_history[-20:]]
    try:
        from anthropic import Anthropic
        api_key = (st.secrets.get("anthropic",{}).get("api_key") or os.environ.get("ANTHROPIC_API_KEY"))
        client = Anthropic(api_key=api_key) if api_key else Anthropic()
        resp = client.messages.create(model="claude-sonnet-4-20250514",max_tokens=600,system=system,messages=messages)
        return resp.content[0].text
    except Exception:
        fb = {"behavior":f"그 일을 '첫 행동'으로 바꿔봅시다.\n\n오늘의 과제: {factor['action_task']}",
              "natural":f"의미를 찾는 방향으로 다뤄볼게요.\n\n오늘의 과제: {factor['action_task']}",
              "thought":f"해석의 폭을 넓혀봅시다.\n\n오늘의 과제: {factor['action_task']}"}
        return fb.get(low, "조금 더 구체적으로 말씀해 주시면 함께 방향을 찾아볼게요.")

def build_csv_all():
    from database import get_all_surveys
    surveys = get_all_surveys()
    if not surveys: return b""
    fields = ["id","name","email","created_at","issue","tone","answers",
              "behavior","natural_reward","constructive_thought","overall","role_model","is_post"]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, extrasaction='ignore')
    w.writeheader()
    for s in surveys: w.writerow(s)
    return ("\ufeff"+buf.getvalue()).encode("utf-8")

def build_user_csv(ss):
    scores = ss.get("scores") or {}
    pre = ss.get("pre_score"); post = ss.get("post_score")
    diff = round(post-pre,2) if (pre is not None and post is not None) else ""
    fields = ["created_at","issue","tone","behavior","natural","thought","overall",
              "role_model","pre_score","post_score","diff"]
    row = {"created_at":datetime.now().isoformat(timespec="seconds"),
           "issue":ss.get("issue",""),"tone":ss.get("tone",""),
           "behavior":scores.get("behavior",""),"natural":scores.get("natural",""),
           "thought":scores.get("thought",""),"overall":scores.get("overall",""),
           "role_model":ss.get("role_model",[""])[0],
           "pre_score":pre or "","post_score":post or "","diff":diff}
    buf = io.StringIO(); w = csv.DictWriter(buf,fieldnames=fields); w.writeheader(); w.writerow(row)
    return ("\ufeff"+buf.getvalue()).encode("utf-8")

def generate_pdf(user_info, scores):
    from fpdf import FPDF
    class PDF(FPDF):
        def header(self):
            self.set_font("NanumGothic","B",14); self.set_text_color(42,102,88)
            self.cell(0,10,"AI MATE — 셀프리더십 진단 리포트",ln=True,align="C")
            self.ln(4); self.set_draw_color(42,102,88); self.line(10,self.get_y(),200,self.get_y()); self.ln(6)
        def footer(self):
            self.set_y(-15); self.set_font("NanumGothic","",8); self.set_text_color(150,150,150)
            self.cell(0,10,f"AI MATE | {datetime.now():%Y-%m-%d} | page {self.page_no()}",align="C")

    font_path = os.path.join(os.path.dirname(__file__), "NanumGothic.ttf")
    if not os.path.exists(font_path):
        try:
            import urllib.request
            urllib.request.urlretrieve(
                "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf",
                font_path)
        except Exception: pass

    pdf = PDF()
    if os.path.exists(font_path):
        pdf.add_font("NanumGothic","",font_path,uni=True)
        pdf.add_font("NanumGothic","B",font_path,uni=True)
    else:
        # 폰트 없으면 기본 폰트 사용 (한글 깨질 수 있음)
        pdf.add_font("NanumGothic","",uni=True)
        pdf.add_font("NanumGothic","B",uni=True)

    pdf.add_page(); pdf.set_font("NanumGothic","",11); pdf.set_text_color(30,30,30)
    name = user_info.get("name","사용자"); email = user_info.get("id","")
    pdf.cell(0,8,f"이름: {name}  |  이메일: {email}  |  날짜: {datetime.now():%Y-%m-%d %H:%M}",ln=True)
    pdf.ln(6)
    pdf.set_font("NanumGothic","B",18); pdf.set_text_color(42,102,88)
    pdf.cell(0,12,f"전체 평균: {scores['overall']:.1f} / 5.0",ln=True,align="C"); pdf.ln(8)

    pdf.set_font("NanumGothic","B",10)
    pdf.set_fill_color(42,102,88); pdf.set_text_color(255,255,255)
    for h,w in [("요인",60),("점수",30),("해석",40),("설명",60)]:
        pdf.cell(w,8,h,1,0,"C",True)
    pdf.ln()
    pdf.set_font("NanumGothic","",9); pdf.set_text_color(30,30,30)
    for key,info in FACTORS.items():
        s = scores.get(key,3.0); label,_ = interpretation(s)
        pdf.set_fill_color(245,249,252)
        for txt,w in [(info["label"],60),(f"{s:.1f}",30),(label,40),(info["short"]+" 영역",60)]:
            pdf.cell(w,8,txt,1,0,"C" if w<50 else "L",True)
        pdf.ln()
    pdf.ln(6)
    low = scores.get("lowest","behavior"); fi = FACTORS[low]
    pdf.set_font("NanumGothic","B",11); pdf.set_text_color(194,90,61)
    pdf.cell(0,8,f"취약 요인: {fi['label']} ({scores[low]:.1f}점)",ln=True)
    pdf.set_font("NanumGothic","",10); pdf.set_text_color(80,80,80)
    pdf.multi_cell(0,7,f"실천과제: {fi['action_task']}")

    buf = io.BytesIO(); pdf.output(buf); return buf.getvalue()

# ═══════════ 유효성 검사 ═══════════
def validate_email(email):
    return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', email))

def validate_pwd(pwd):
    if not re.match(r'^\d{6}$', pwd): return False, "비밀번호는 숫자 6자리여야 합니다."
    for i in range(len(pwd)-2):
        if pwd[i]==pwd[i+1]==pwd[i+2]: return False, "같은 숫자가 3번 연속될 수 없습니다."
    return True, ""

def validate_name(name):
    if not name: return False
    if re.match(r'^[가-힣]{1,4}$', name): return True
    if re.match(r'^[a-zA-Z]{1,8}$', name): return True
    if re.match(r'^[가-힣a-zA-Z]{1,8}$', name): return True
    return False

def format_phone(raw):
    digits = re.sub(r'\D','',raw)
    if len(digits)==11: return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    if len(digits)==10: return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    return raw
