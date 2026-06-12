import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from core.config import settings

DB_PATH = Path(settings.DB_PATH)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Create all tables if they don't exist."""
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                favorite_movies TEXT DEFAULT '[]',
                favorite_characters TEXT DEFAULT '[]',
                favorite_genres TEXT DEFAULT '[]',
                soul_profile TEXT DEFAULT '',
                character_dna TEXT DEFAULT '',
                hidden_taste TEXT DEFAULT '',
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                movie_id INTEGER,
                movie_title TEXT NOT NULL,
                rating REAL NOT NULL,
                review TEXT DEFAULT '',
                rated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS recommendation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                movie_id INTEGER,
                movie_title TEXT NOT NULL,
                reason TEXT DEFAULT '',
                recommended_at TEXT DEFAULT CURRENT_TIMESTAMP,
                clicked INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS taste_evolution (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                snapshot TEXT DEFAULT '{}',
                analysis TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """)


# ─── User ────────────────────────────────────────────────────────────────────

def ensure_user(user_id: str):
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,)
        )
        conn.execute(
            "INSERT OR IGNORE INTO user_profiles (user_id) VALUES (?)", (user_id,)
        )


# ─── Profile ─────────────────────────────────────────────────────────────────

def get_profile(user_id: str) -> Optional[Dict[str, Any]]:
    ensure_user(user_id)
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM user_profiles WHERE user_id = ?", (user_id,)
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        d["favorite_movies"] = json.loads(d["favorite_movies"])
        d["favorite_characters"] = json.loads(d["favorite_characters"])
        d["favorite_genres"] = json.loads(d["favorite_genres"])
        return d


def update_profile(user_id: str, data: Dict[str, Any]):
    ensure_user(user_id)
    now = datetime.utcnow().isoformat()
    fields = []
    values = []
    list_fields = {"favorite_movies", "favorite_characters", "favorite_genres"}
    for k, v in data.items():
        if k in list_fields:
            v = json.dumps(v)
        fields.append(f"{k} = ?")
        values.append(v)
    fields.append("updated_at = ?")
    values.append(now)
    values.append(user_id)
    with get_connection() as conn:
        conn.execute(
            f"UPDATE user_profiles SET {', '.join(fields)} WHERE user_id = ?",
            values
        )


# ─── Ratings ─────────────────────────────────────────────────────────────────

def add_rating(user_id: str, movie_id: int, movie_title: str, rating: float, review: str = ""):
    ensure_user(user_id)
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO ratings (user_id, movie_id, movie_title, rating, review)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, movie_id, movie_title, rating, review)
        )


def get_ratings(user_id: str) -> List[Dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM ratings WHERE user_id = ? ORDER BY rated_at DESC",
            (user_id,)
        ).fetchall()
        return [dict(r) for r in rows]


# ─── Recommendation History ───────────────────────────────────────────────────

def add_recommendation(user_id: str, movie_id: int, movie_title: str, reason: str):
    ensure_user(user_id)
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO recommendation_history (user_id, movie_id, movie_title, reason)
               VALUES (?, ?, ?, ?)""",
            (user_id, movie_id, movie_title, reason)
        )


def get_recommendation_history(user_id: str, limit: int = 20) -> List[Dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT * FROM recommendation_history
               WHERE user_id = ? ORDER BY recommended_at DESC LIMIT ?""",
            (user_id, limit)
        ).fetchall()
        return [dict(r) for r in rows]


# ─── Taste Evolution ──────────────────────────────────────────────────────────

def add_taste_snapshot(user_id: str, snapshot: Dict, analysis: str):
    ensure_user(user_id)
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO taste_evolution (user_id, snapshot, analysis) VALUES (?, ?, ?)",
            (user_id, json.dumps(snapshot), analysis)
        )


def get_taste_evolution(user_id: str, limit: int = 10) -> List[Dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT * FROM taste_evolution
               WHERE user_id = ? ORDER BY created_at DESC LIMIT ?""",
            (user_id, limit)
        ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["snapshot"] = json.loads(d["snapshot"])
            result.append(d)
        return result


# ─── Chat History ─────────────────────────────────────────────────────────────

def add_chat_message(user_id: str, role: str, content: str):
    ensure_user(user_id)
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO chat_history (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, role, content)
        )


def get_chat_history(user_id: str, limit: int = 20) -> List[Dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT role, content, timestamp FROM chat_history
               WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?""",
            (user_id, limit)
        ).fetchall()
        return list(reversed([dict(r) for r in rows]))


def clear_chat_history(user_id: str):
    """Delete all chat messages for a user."""
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM chat_history WHERE user_id = ?", (user_id,)
        )
