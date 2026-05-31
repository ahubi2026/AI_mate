# ============================================================
#  database.py — SQLite 초기화 + 전체 CRUD 함수
# ============================================================

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aiMate.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT DEFAULT (datetime('now','localtime')),
        issue TEXT, tone TEXT,
        behavior REAL, natural_reward REAL, constructive_thought REAL,
        overall REAL, role_model TEXT, is_post INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER, role TEXT, content TEXT,
        created_at TEXT DEFAULT (datetime('now','localtime'))
    );
    CREATE TABLE IF NOT EXISTS journals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT, reflection TEXT,
        created_at TEXT DEFAULT (datetime('now','localtime'))
    );
    """)
    conn.commit()
    conn.close()


# ── sessions ─────────────────────────────────────────────
def db_save_session(issue, tone, scores, role_model, is_post=0):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO sessions (issue,tone,behavior,natural_reward,"
        "constructive_thought,overall,role_model,is_post) VALUES (?,?,?,?,?,?,?,?)",
        (issue, tone,
         scores["behavior"], scores["natural"], scores["thought"],
         scores["overall"], role_model[0] if role_model else "", is_post)
    )
    conn.commit()
    sid = cur.lastrowid
    conn.close()
    return sid


def db_get_session_count():
    conn = get_conn()
    row  = conn.execute("SELECT COUNT(*) AS n FROM sessions").fetchone()
    conn.close()
    return row["n"] if row else 0


# ── chats ─────────────────────────────────────────────────
def db_save_chat(session_id, role, content):
    if not session_id:
        return
    conn = get_conn()
    conn.execute(
        "INSERT INTO chats (session_id,role,content) VALUES (?,?,?)",
        (session_id, role, content)
    )
    conn.commit()
    conn.close()


def db_get_chat_count():
    conn = get_conn()
    row  = conn.execute("SELECT COUNT(*) AS n FROM chats WHERE role='user'").fetchone()
    conn.close()
    return row["n"] if row else 0


# ── journals ──────────────────────────────────────────────
def db_save_journal(action, reflection):
    conn = get_conn()
    conn.execute(
        "INSERT INTO journals (action,reflection) VALUES (?,?)",
        (action, reflection)
    )
    conn.commit()
    conn.close()


def db_get_journals(limit=30):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM journals ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
