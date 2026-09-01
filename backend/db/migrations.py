"""
Database bootstrap and migration runner.

Call init_db() once at startup.

Migration rules
───────────────
• Always APPEND to the list — never edit or remove an existing entry.
• One logical change per entry.
• Multi-statement SQL (contains newlines / multiple semicolons) is run with
  executescript(); single-line SQL uses execute().
"""
import os
import sqlite3

from core.config import BASE_DIR, DATABASE

_SCHEMA = os.path.join(BASE_DIR, "db", "schema.sql")


def init_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row

    # Base schema — every statement uses CREATE TABLE IF NOT EXISTS,
    # so this is safe to re-run against an existing database.
    if os.path.exists(_SCHEMA):
        with open(_SCHEMA, "r", encoding="utf-8") as f:
            db.executescript(f.read())

    # Migration tracking table
    db.execute("""
        CREATE TABLE IF NOT EXISTS _migrations (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT UNIQUE NOT NULL,
            applied_at TEXT DEFAULT (datetime('now'))
        )
    """)
    db.commit()

    # ── Migration list ────────────────────────────────────────────────────────
    # v1.0.0 — full schema is in db/schema.sql, no patches needed yet.
    # When you need to change the database in a future release, append here:
    #
    #   ("007_example", "ALTER TABLE foo ADD COLUMN bar TEXT"),
    #
    migrations = [
        ("001_add_user_profile_image", "ALTER TABLE users ADD COLUMN profile_image TEXT"),
        ("002_add_recipe_calories",      "ALTER TABLE recipes ADD COLUMN calories INTEGER"),
        ("003_add_recipe_calories_unit", "ALTER TABLE recipes ADD COLUMN calories_unit TEXT DEFAULT 'serving'"),
        ("004_rename_hh_admin_to_owner", "UPDATE household_members SET role = 'owner' WHERE role = 'admin'"),
        ("005_add_user_token_version",   "ALTER TABLE users ADD COLUMN token_version INTEGER NOT NULL DEFAULT 0"),
        ("006_add_invite_expires_at",    "ALTER TABLE invite_links ADD COLUMN expires_at TIMESTAMP"),
    ]
    # ─────────────────────────────────────────────────────────────────────────

    applied = {r["name"] for r in db.execute("SELECT name FROM _migrations")}

    for name, sql in migrations:
        if name in applied:
            continue
        try:
            if sql.strip().count(";") > 1 or "\n" in sql.strip():
                db.executescript(sql)
            else:
                db.execute(sql)
            db.execute("INSERT INTO _migrations (name) VALUES (?)", (name,))
            db.commit()
            print(f"  [migration] applied: {name}")
        except Exception as e:
            print(f"  [migration] skipped ({name}): {e}")

    db.close()
