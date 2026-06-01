# database.py — SQLite: user / survey / questions / chats / journals
import sqlite3, os, hashlib, json
from config import DEFAULT_QUESTIONS

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aiMate.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def _hash(pw): return hashlib.sha256(pw.encode()).hexdigest()

# ═══════════ 초기화 ═══════════
def init_db():
    c = get_conn()
    c.executescript("""
    -- user 테이블: idx 자동증가 PK, id=이메일
    CREATE TABLE IF NOT EXISTS user (
        idx       INTEGER PRIMARY KEY AUTOINCREMENT,
        id        TEXT    UNIQUE NOT NULL,      -- 이메일
        pwd_hash  TEXT    NOT NULL,
        name      TEXT    NOT NULL,
        gender    TEXT,
        age       INTEGER,
        phone     TEXT,
        created_at TEXT DEFAULT (datetime('now','localtime'))
    );

    -- survey 테이블: 문항별 점수(INTEGER) + 요인별 평균(REAL)
    CREATE TABLE IF NOT EXISTS survey (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_idx   INTEGER REFERENCES user(idx),
        created_at TEXT DEFAULT (datetime('now','localtime')),
        issue      TEXT,
        tone       TEXT,
        answers    TEXT,       -- JSON: {"A1":3,"A2":4,...}
        behavior       REAL,
        natural_reward REAL,
        constructive_thought REAL,
        overall        REAL,
        role_model     TEXT,
        is_post        INTEGER DEFAULT 0
    );

    -- 문항 관리 (관리자 수정 가능)
    CREATE TABLE IF NOT EXISTS questions (
        qid        TEXT PRIMARY KEY,
        factor     TEXT NOT NULL,
        text       TEXT NOT NULL,
        sort_order INTEGER DEFAULT 0,
        active     INTEGER DEFAULT 1
    );

    -- 채팅 로그
    CREATE TABLE IF NOT EXISTS chats (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        survey_id  INTEGER,
        role       TEXT,
        content    TEXT,
        created_at TEXT DEFAULT (datetime('now','localtime'))
    );

    -- 성찰 일지
    CREATE TABLE IF NOT EXISTS journals (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_idx   INTEGER,
        action     TEXT,
        reflection TEXT,
        created_at TEXT DEFAULT (datetime('now','localtime'))
    );
    """)
    # 기본 문항 시드
    if c.execute("SELECT COUNT(*) FROM questions").fetchone()[0] == 0:
        for i, (qid, factor, text) in enumerate(DEFAULT_QUESTIONS):
            c.execute("INSERT INTO questions (qid,factor,text,sort_order) VALUES (?,?,?,?)",
                      (qid, factor, text, i))
    c.commit(); c.close()

# ═══════════ user CRUD ═══════════
def register_user(email, pwd, name, gender, age, phone):
    c = get_conn()
    try:
        c.execute("INSERT INTO user (id,pwd_hash,name,gender,age,phone) VALUES (?,?,?,?,?,?)",
                  (email, _hash(pwd), name, gender, int(age), phone))
        c.commit(); return True, "등록 완료"
    except sqlite3.IntegrityError:
        return False, "이미 등록된 이메일입니다."
    finally: c.close()

def check_email_available(email):
    c = get_conn()
    r = c.execute("SELECT idx FROM user WHERE id=?", (email,)).fetchone()
    c.close(); return r is None

def login_user(email, pwd):
    c = get_conn()
    r = c.execute("SELECT * FROM user WHERE id=? AND pwd_hash=?",
                  (email, _hash(pwd))).fetchone()
    c.close(); return dict(r) if r else None

def get_all_users():
    c = get_conn()
    rows = c.execute("SELECT * FROM user ORDER BY created_at DESC").fetchall()
    c.close(); return [dict(r) for r in rows]

def get_user_by_idx(idx):
    c = get_conn()
    r = c.execute("SELECT * FROM user WHERE idx=?", (idx,)).fetchone()
    c.close(); return dict(r) if r else None

def reset_user_pwd(idx, new_pwd="000000"):
    c = get_conn()
    c.execute("UPDATE user SET pwd_hash=? WHERE idx=?", (_hash(new_pwd), idx))
    c.commit(); c.close()

def get_user_count():
    c = get_conn(); n = c.execute("SELECT COUNT(*) FROM user").fetchone()[0]; c.close(); return n

def get_age_distribution():
    c = get_conn()
    rows = c.execute("SELECT age FROM user WHERE age IS NOT NULL").fetchall()
    c.close()
    dist = {f"{d}0대": 0 for d in range(1, 9)}
    for r in rows:
        decade = min(max(r["age"] // 10, 1), 8)
        dist[f"{decade}0대"] += 1
    return dist

# ═══════════ questions (관리자) ═══════════
def get_questions():
    c = get_conn()
    rows = c.execute("SELECT * FROM questions WHERE active=1 ORDER BY sort_order, qid").fetchall()
    c.close(); return [dict(r) for r in rows]

def get_all_questions_admin():
    c = get_conn()
    rows = c.execute("SELECT * FROM questions ORDER BY sort_order, qid").fetchall()
    c.close(); return [dict(r) for r in rows]

def add_question(qid, factor, text):
    c = get_conn()
    mx = c.execute("SELECT COALESCE(MAX(sort_order),0)+1 FROM questions").fetchone()[0]
    c.execute("INSERT OR REPLACE INTO questions (qid,factor,text,sort_order,active) VALUES (?,?,?,?,1)",
              (qid, factor, text, mx))
    c.commit(); c.close()

def update_question(qid, factor, text):
    c = get_conn()
    c.execute("UPDATE questions SET factor=?, text=? WHERE qid=?", (factor, text, qid))
    c.commit(); c.close()

def toggle_question(qid, active):
    c = get_conn()
    c.execute("UPDATE questions SET active=? WHERE qid=?", (1 if active else 0, qid))
    c.commit(); c.close()

# ═══════════ survey (진단 결과) ═══════════
def save_survey(user_idx, issue, tone, answers_dict, scores, role_model, is_post=0):
    """answers_dict = {"A1": 3, "A2": 4, ...}"""
    c = get_conn(); cur = c.cursor()
    cur.execute(
        "INSERT INTO survey (user_idx,issue,tone,answers,behavior,natural_reward,"
        "constructive_thought,overall,role_model,is_post) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (user_idx, issue, tone, json.dumps(answers_dict, ensure_ascii=False),
         scores["behavior"], scores["natural"], scores["thought"],
         scores["overall"], role_model[0] if role_model else "", is_post))
    c.commit(); sid = cur.lastrowid; c.close(); return sid

def get_user_surveys(user_idx):
    c = get_conn()
    rows = c.execute("SELECT * FROM survey WHERE user_idx=? ORDER BY created_at DESC",
                     (user_idx,)).fetchall()
    c.close(); return [dict(r) for r in rows]

def get_all_surveys():
    c = get_conn()
    rows = c.execute("""
        SELECT s.*, u.name, u.id as email FROM survey s
        LEFT JOIN user u ON s.user_idx = u.idx
        ORDER BY s.created_at DESC
    """).fetchall()
    c.close(); return [dict(r) for r in rows]

def get_survey_count():
    c = get_conn(); n = c.execute("SELECT COUNT(*) FROM survey").fetchone()[0]; c.close(); return n

# ═══════════ chats ═══════════
def save_chat(survey_id, role, content):
    if not survey_id: return
    c = get_conn()
    c.execute("INSERT INTO chats (survey_id,role,content) VALUES (?,?,?)",
              (survey_id, role, content))
    c.commit(); c.close()

def get_chat_count():
    c = get_conn(); n = c.execute("SELECT COUNT(*) FROM chats WHERE role='user'").fetchone()[0]
    c.close(); return n

# ═══════════ journals ═══════════
def save_journal(user_idx, action, reflection):
    c = get_conn()
    c.execute("INSERT INTO journals (user_idx,action,reflection) VALUES (?,?,?)",
              (user_idx, action, reflection))
    c.commit(); c.close()

def get_journals(user_idx=None, limit=30):
    c = get_conn()
    if user_idx:
        rows = c.execute("SELECT * FROM journals WHERE user_idx=? ORDER BY created_at DESC LIMIT ?",
                         (user_idx, limit)).fetchall()
    else:
        rows = c.execute("SELECT * FROM journals ORDER BY created_at DESC LIMIT ?",
                         (limit,)).fetchall()
    c.close(); return [dict(r) for r in rows]
