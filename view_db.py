"""
CineDNA Database Inspector
Prints schema, data, and runs diagnostics on the cine.db database.
"""
import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "cine.db")

def main():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # --- Tables ---
    print("\n" + "=" * 60)
    print("  TABLES IN DATABASE")
    print("=" * 60)
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchall()
    for table in tables:
        print(f"  • {table[0]}")

    # --- Schema ---
    print("\n" + "=" * 60)
    print("  SCHEMA: user_preferences")
    print("=" * 60)
    cols = conn.execute("PRAGMA table_info(user_preferences)").fetchall()
    col_names = []
    for col in cols:
        col_names.append(col[1])
        print(f"  [{col[0]}] {col[1]:25s} {col[2]}")

    expected_order = [
        "user_id", "favorite_genres", "favorite_movies",
        "favorite_characters", "soul_profile", "character_dna",
        "hidden_taste", "updated_at",
    ]
    print(f"\n  Expected order: {expected_order}")
    print(f"  Actual order:   {col_names}")
    if col_names == expected_order:
        print("  ✅ Column order matches expected schema.")
    else:
        print("  ⚠️  Column order DIFFERS from expected schema!")
        print("  (This is OK if all SQL uses explicit column names.)")

    # --- User Preferences Data ---
    print("\n" + "=" * 60)
    print("  USER PREFERENCES DATA")
    print("=" * 60)
    rows = conn.execute("SELECT * FROM user_preferences").fetchall()
    if not rows:
        print("  (no records)")
    for row in rows:
        print(f"\n  --- User: {row['user_id']} ---")
        fields = [
            "favorite_genres", "favorite_movies", "favorite_characters",
            "soul_profile", "character_dna", "hidden_taste", "updated_at",
        ]
        for field in fields:
            val = row[field]
            # Try to pretty-print JSON
            if val and field in ("favorite_movies", "favorite_characters", "favorite_genres"):
                try:
                    parsed = json.loads(val)
                    val = parsed
                except (json.JSONDecodeError, TypeError):
                    pass
            label = f"  {field:25s}"
            print(f"{label} : {val}")

        # Issue detection
        issues = []
        for f in ["soul_profile", "character_dna", "hidden_taste"]:
            v = row[f]
            if v and "Profile generation failed" in str(v):
                issues.append(f"  ⚠️  {f} = 'Profile generation failed.'")
        for f in ["favorite_movies", "favorite_characters", "favorite_genres"]:
            v = row[f]
            if v and ("Soul Type" in str(v) or "Character DNA" in str(v)):
                issues.append(f"  ❌ {f} contains profile text (misaligned data!)")

        if issues:
            print("\n  DATA ISSUES:")
            for issue in issues:
                print(issue)
        else:
            print("\n  ✅ Data looks consistent.")

    # --- Chat History (last 10) ---
    print("\n" + "=" * 60)
    print("  CHAT HISTORY (last 10)")
    print("=" * 60)
    rows = conn.execute(
        "SELECT * FROM chat_history ORDER BY timestamp DESC LIMIT 10"
    ).fetchall()
    if not rows:
        print("  (no records)")
    for row in rows:
        msg = str(row["content"])[:80].replace("\n", " ")
        print(f"  [{row['timestamp']}] {row['user_id']} ({row['message_type']}): {msg}")

    conn.close()
    print()


if __name__ == "__main__":
    main()