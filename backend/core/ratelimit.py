"""
Failed-login throttling, backed by SQLite so the counters are shared across
Gunicorn workers (an in-process counter would be per-worker and trivially
bypassed by hitting a different worker).

Two independent keys are tracked:
  user:<username>  — the real defence; strict threshold
  ip:<address>     — catches spraying across many usernames; looser threshold,
                     because behind a reverse proxy every request can share one
                     source address (see TRUSTED_PROXY_COUNT in core/config).
"""
import time

_USER_MAX_FAILS = 8
_IP_MAX_FAILS   = 30
_WINDOW         = 300    # failures older than this start a fresh window
_LOCKOUT        = 900    # how long a tripped key stays locked


def _limit_for(key: str) -> int:
    return _IP_MAX_FAILS if key.startswith("ip:") else _USER_MAX_FAILS


def locked_for(db, keys: list[str]) -> int:
    """Seconds remaining on the longest active lockout across keys (0 if none)."""
    now       = time.time()
    remaining = 0
    for key in keys:
        row = db.execute(
            "SELECT locked_until FROM login_attempts WHERE key = ?", (key,)
        ).fetchone()
        if row and row["locked_until"] > now:
            remaining = max(remaining, int(row["locked_until"] - now))
    return remaining


def register_failure(db, keys: list[str]) -> None:
    """Count a failed attempt against each key, locking any that trips its limit."""
    now = time.time()
    for key in keys:
        row = db.execute(
            "SELECT fails, window_start FROM login_attempts WHERE key = ?", (key,)
        ).fetchone()

        if row and (now - row["window_start"]) < _WINDOW:
            fails = row["fails"] + 1
            start = row["window_start"]
        else:
            fails = 1
            start = now

        locked_until = now + _LOCKOUT if fails >= _limit_for(key) else 0
        db.execute(
            "INSERT INTO login_attempts (key, fails, window_start, locked_until) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT(key) DO UPDATE SET "
            "  fails = excluded.fails, "
            "  window_start = excluded.window_start, "
            "  locked_until = excluded.locked_until",
            (key, fails, start, locked_until),
        )
    db.commit()


def clear(db, keys: list[str]) -> None:
    """Wipe the counters for these keys after a successful login."""
    for key in keys:
        db.execute("DELETE FROM login_attempts WHERE key = ?", (key,))
    db.commit()
