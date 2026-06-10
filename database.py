"""
CineDNA – SQLite database layer.
Schema-safe, migration-capable, fully named-parameter SQL.
"""

import sqlite3
import json
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CineDNA.DB")

DB_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DB_DIR, "cine.db")

_conn = None

# --------------------------------------------------------------------------- #
#  Expected schema – single source of truth                                   #
# --------------------------------------------------------------------------- #
EXPECTED_COLUMNS = [
    ("user_id",            "TEXT"),
    ("favorite_genres",    "TEXT"),
    ("favorite_movies",    "TEXT"),
    ("favorite_characters","TEXT"),
    ("soul_profile",       "TEXT"),
    ("character_dna",      "TEXT"),
    ("hidden_taste",       "TEXT"),
    ("updated_at",         "DATETIME"),
]
EXPECTED_COLUMN_NAMES = [c[0] for c in EXPECTED_COLUMNS]


# --------------------------------------------------------------------------- #
#  Connection                                                                  #
# --------------------------------------------------------------------------- #
def _get_conn():
    global _conn
    if _conn is None:
        os.makedirs(DB_DIR, exist_ok=True)
        _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA journal_mode=WAL")
        _conn.execute("PRAGMA synchronous=NORMAL")
    return _conn


# --------------------------------------------------------------------------- #
#  Schema helpers                                                              #
# --------------------------------------------------------------------------- #
def _get_existing_columns(conn):
    cur = conn.execute("PRAGMA table_info(user_preferences)")
    return [(r[0], r[1], r[2]) for r in cur.fetchall()]


def _migrate_schema(conn):
    """Add missing columns without destroying data."""
    existing_names = [c[1] for c in _get_existing_columns(conn)]
    additions = {
        "favorite_genres":    "TEXT",
        "favorite_movies":    "TEXT",
        "favorite_characters":"TEXT",
        "soul_profile":       "TEXT",
        "character_dna":      "TEXT",
        "hidden_taste":       "TEXT",
        "updated_at":         "DATETIME DEFAULT CURRENT_TIMESTAMP",
        # Phase 4 addition
        "taste_evolution":    "TEXT",
    }
    migrated = False
    for col, col_type in additions.items():
        if col not in existing_names:
            try:
                conn.execute(f"ALTER TABLE user_preferences ADD COLUMN {col} {col_type}")
                logger.info(f"Migration: added column '{col}'")
                migrated = True
            except sqlite3.OperationalError as e:
                logger.error(f"Migration failed for '{col}': {e}")
    if migrated:
        conn.commit()


def _verify_schema(conn):
    existing = _get_existing_columns(conn)
    existing_names = [c[1] for c in existing]
    logger.info("=== user_preferences schema ===")
    for cid, name, typ in existing:
        flag = ""
        if cid < len(EXPECTED_COLUMN_NAMES) and name != EXPECTED_COLUMN_NAMES[cid]:
            flag = f"  [order differs – expected {EXPECTED_COLUMN_NAMES[cid]}]"
        logger.info(f"  [{cid}] {name} ({typ}){flag}")
    missing = [c for c in EXPECTED_COLUMN_NAMES if c not in existing_names]
    if missing:
        raise RuntimeError(f"Missing required columns: {missing}")
    logger.info("Schema OK.")


# --------------------------------------------------------------------------- #
#  init_db                                                                     #
# --------------------------------------------------------------------------- #
def init_db():
    conn = _get_conn()

    conn.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      TEXT,
            message_type TEXT,
            content      TEXT,
            timestamp    DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id            TEXT PRIMARY KEY,
            favorite_genres    TEXT,
            favorite_movies    TEXT,
            favorite_characters TEXT,
            soul_profile       TEXT,
            character_dna      TEXT,
            hidden_taste       TEXT,
            updated_at         DATETIME DEFAULT CURRENT_TIMESTAMP,
            taste_evolution    TEXT
        )
    ''')

    # Phase 4: movie ratings table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS movie_ratings (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     TEXT NOT NULL,
            movie_name  TEXT NOT NULL,
            rating      REAL NOT NULL CHECK(rating >= 0 AND rating <= 10),
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_chat_user
        ON chat_history(user_id, timestamp DESC)
    ''')
    conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_ratings_user
        ON movie_ratings(user_id, created_at DESC)
    ''')

    _migrate_schema(conn)
    conn.commit()
    _verify_schema(conn)
    logger.info("Database ready.")


# --------------------------------------------------------------------------- #
#  Chat history                                                                #
# --------------------------------------------------------------------------- #
def save_message(user_id: str, message_type: str, content: str):
    conn = _get_conn()
    conn.execute(
        "INSERT INTO chat_history (user_id, message_type, content) VALUES (?,?,?)",
        (user_id, message_type, content)
    )
    conn.commit()


def get_recent_messages(user_id: str, limit: int = 10):
    conn = _get_conn()
    rows = conn.execute(
        "SELECT message_type, content FROM chat_history "
        "WHERE user_id=? ORDER BY timestamp DESC LIMIT ?",
        (user_id, limit)
    ).fetchall()
    return [{"role": r["message_type"], "content": r["content"]} for r in reversed(rows)]


# --------------------------------------------------------------------------- #
#  User preferences                                                            #
# --------------------------------------------------------------------------- #
def save_user_preferences(user_id: str, favorite_genres=None, favorite_movies=None,
                          favorite_characters=None, soul_profile=None,
                          character_dna=None, hidden_taste=None,
                          taste_evolution=None):
    conn = _get_conn()
    existing = conn.execute(
        "SELECT * FROM user_preferences WHERE user_id=?", (user_id,)
    ).fetchone()

    def _j(new_val, field):
        """JSON-encode if it's a list/new value, else keep existing."""
        if new_val is not None:
            return json.dumps(new_val) if isinstance(new_val, list) else new_val
        return existing[field] if existing else None

    genres_str  = _j(favorite_genres,    "favorite_genres")
    movies_str  = _j(favorite_movies,    "favorite_movies")
    chars_str   = _j(favorite_characters,"favorite_characters")
    soul_str    = _j(soul_profile,        "soul_profile")
    dna_str     = _j(character_dna,       "character_dna")
    hidden_str  = _j(hidden_taste,        "hidden_taste")
    evo_str     = _j(taste_evolution,     "taste_evolution")

    logger.info("SAVE user_preferences user_id=%s", user_id)
    logger.info("  favorite_movies      = %s", movies_str)
    logger.info("  favorite_characters  = %s", chars_str)
    logger.info("  favorite_genres      = %s", genres_str)
    logger.info("  soul_profile         = %s", soul_str)
    logger.info("  character_dna        = %s", dna_str)
    logger.info("  hidden_taste         = %s", hidden_str)
    logger.info("  taste_evolution      = %s", evo_str)

    conn.execute(
        """INSERT INTO user_preferences
               (user_id, favorite_genres, favorite_movies, favorite_characters,
                soul_profile, character_dna, hidden_taste, updated_at, taste_evolution)
           VALUES
               (:user_id, :favorite_genres, :favorite_movies, :favorite_characters,
                :soul_profile, :character_dna, :hidden_taste, CURRENT_TIMESTAMP, :taste_evolution)
           ON CONFLICT(user_id) DO UPDATE SET
               favorite_genres     = :favorite_genres,
               favorite_movies     = :favorite_movies,
               favorite_characters = :favorite_characters,
               soul_profile        = :soul_profile,
               character_dna       = :character_dna,
               hidden_taste        = :hidden_taste,
               taste_evolution     = :taste_evolution,
               updated_at          = CURRENT_TIMESTAMP""",
        {
            "user_id":            user_id,
            "favorite_genres":    genres_str,
            "favorite_movies":    movies_str,
            "favorite_characters":chars_str,
            "soul_profile":       soul_str,
            "character_dna":      dna_str,
            "hidden_taste":       hidden_str,
            "taste_evolution":    evo_str,
        }
    )
    conn.commit()


def get_user_profile(user_id: str) -> dict:
    conn = _get_conn()
    row = conn.execute(
        "SELECT user_id, favorite_genres, favorite_movies, favorite_characters, "
        "soul_profile, character_dna, hidden_taste, taste_evolution, updated_at "
        "FROM user_preferences WHERE user_id=?",
        (user_id,)
    ).fetchone()

    if not row:
        return {}

    profile = {}
    for field in ("favorite_genres", "favorite_movies", "favorite_characters"):
        raw = row[field]
        if raw:
            try:
                profile[field] = json.loads(raw)
            except json.JSONDecodeError:
                profile[field] = raw

    for field in ("soul_profile", "character_dna", "hidden_taste", "taste_evolution"):
        if row[field]:
            profile[field] = row[field]

    logger.info("LOAD user_preferences user_id=%s => %s", user_id,
                {k: str(v)[:60] for k, v in profile.items()})
    return profile


# --------------------------------------------------------------------------- #
#  Movie ratings (Phase 4)                                                    #
# --------------------------------------------------------------------------- #
def save_movie_rating(user_id: str, movie_name: str, rating: float):
    """Save or update a movie rating (0–10)."""
    rating = max(0.0, min(10.0, float(rating)))
    conn = _get_conn()
    # If the user already rated this movie, update
    existing = conn.execute(
        "SELECT id FROM movie_ratings WHERE user_id=? AND movie_name=?",
        (user_id, movie_name)
    ).fetchone()
    if existing:
        conn.execute(
            "UPDATE movie_ratings SET rating=?, created_at=CURRENT_TIMESTAMP "
            "WHERE id=?",
            (rating, existing["id"])
        )
    else:
        conn.execute(
            "INSERT INTO movie_ratings (user_id, movie_name, rating) VALUES (?,?,?)",
            (user_id, movie_name, rating)
        )
    conn.commit()
    logger.info("Rating saved: user=%s movie=%s rating=%.1f", user_id, movie_name, rating)


def get_user_ratings(user_id: str, limit: int = 20) -> list:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT movie_name, rating, created_at FROM movie_ratings "
        "WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit)
    ).fetchall()
    return [{"movie_name": r["movie_name"], "rating": r["rating"],
             "created_at": r["created_at"]} for r in rows]


# --------------------------------------------------------------------------- #
#  Misc                                                                        #
# --------------------------------------------------------------------------- #
def clear_user_profile(user_id: str):
    conn = _get_conn()
    conn.execute("DELETE FROM user_preferences WHERE user_id=?", (user_id,))
    conn.execute("DELETE FROM chat_history WHERE user_id=?", (user_id,))
    conn.execute("DELETE FROM movie_ratings WHERE user_id=?", (user_id,))
    conn.commit()
    logger.info("Cleared all data for user '%s'", user_id)


def inspect_user_profile(user_id: str):
    """Debug: pretty-print a user's full profile."""
    conn = _get_conn()
    row = conn.execute(
        "SELECT user_id, favorite_genres, favorite_movies, favorite_characters, "
        "soul_profile, character_dna, hidden_taste, taste_evolution, updated_at "
        "FROM user_preferences WHERE user_id=?",
        (user_id,)
    ).fetchone()

    print("=" * 60)
    print(f"  USER PROFILE: {user_id}")
    print("=" * 60)
    if not row:
        print("  (no record found)")
        return

    for field in ("user_id", "favorite_movies", "favorite_characters",
                  "favorite_genres", "soul_profile", "character_dna",
                  "hidden_taste", "taste_evolution", "updated_at"):
        val = row[field]
        if val and field in ("favorite_movies", "favorite_characters", "favorite_genres"):
            try:
                val = json.loads(val)
            except Exception:
                pass
        print(f"  {field:25s}: {val}")
    print("=" * 60)

    ratings = get_user_ratings(user_id, limit=5)
    if ratings:
        print("  RECENT RATINGS:")
        for r in ratings:
            print(f"    {r['movie_name']:30s} {r['rating']}/10")
    print()


# Initialise on import
init_db()
