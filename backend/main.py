"""
Entry point.

  Production / Docker:  set SECRET_KEY in the environment or in backend/.env
  Local dev:            python main.py  (key is auto-generated and saved to .env)

  ENV_FILE overrides where a generated key is written (Docker points it at the
  /data volume so the key survives image upgrades).

  WSGI:  gunicorn "main:app"
"""
import os
import secrets

from dotenv import load_dotenv, set_key

# ── Secret key ────────────────────────────────────────────────────────────────
# Must be resolved BEFORE any other import touches core/config.py.
#
# Priority:
#   1. SECRET_KEY already in the environment  ← Docker / production
#   2. SECRET_KEY in backend/.env             ← local dev, persists across restarts
#   3. Generate + save to backend/.env        ← first local run

# Where the auto-generated key is persisted. Defaults to backend/.env for local
# dev. Docker overrides it to /data/.env — the mounted volume — because the
# container's own filesystem is discarded on every image upgrade, which would
# silently mint a new key and sign every user out.
_ENV_FILE = os.environ.get("ENV_FILE") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".env"
)

load_dotenv(_ENV_FILE)

if not os.environ.get("SECRET_KEY"):
    key = secrets.token_hex(32)
    set_key(_ENV_FILE, "SECRET_KEY", key)
    os.environ["SECRET_KEY"] = key
    print("  🔑 Generated new secret key → backend/.env")

# ── App ───────────────────────────────────────────────────────────────────────
from db.migrations import init_db
from app import create_app
from core.config import PORT

init_db()
app = create_app()

if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    print(f"🚀 Listly dev server → http://0.0.0.0:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=debug)
