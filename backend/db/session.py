"""
Per-request SQLite connection management.
"""
import sqlite3

from flask import g

from core.config import DATABASE


def get_db():
    """Return the per-request DB connection, opening it on first call."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(exc=None):
    """Teardown hook — close connection at end of request context."""
    db = g.pop("db", None)
    if db:
        db.close()
