import os

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # backend/

DIST_DIR   = os.environ.get(
    "DIST_DIR",
    os.path.join(BASE_DIR, "..", "frontend", "dist"),
)
DATABASE   = os.environ.get("DATABASE",   os.path.join(BASE_DIR, "database.db"))
ASSETS_DIR = os.environ.get("ASSETS_DIR", os.path.join(BASE_DIR, "assets"))
PORT       = int(os.environ.get("PORT", 5000))
SECRET_KEY = os.environ["SECRET_KEY"]  # guaranteed set by main.py before import

# Placeholder values that ship in example config. Booting on one of these means
# anyone who has read the repo can forge a JWT for any account, so refuse.
_PLACEHOLDER_SECRETS = {
    "change-me-to-a-random-secret",
    "changeme",
    "secret",
    "please-change-me",
}
if SECRET_KEY.strip().lower() in _PLACEHOLDER_SECRETS or len(SECRET_KEY.strip()) < 32:
    raise RuntimeError(
        "SECRET_KEY is a placeholder or too short. Anyone with this value can "
        "forge admin sessions. Generate one with:\n"
        '  python -c "import secrets; print(secrets.token_hex(32))"\n'
        "and set it in docker/.env (Docker) or backend/.env (local)."
    )

# Cross-origin access. Listly serves its own frontend, and the Vite dev server
# proxies /api, so both are same-origin and no CORS headers are needed. Set
# CORS_ORIGINS to a comma-separated origin list only if you front the API with
# a separately-hosted client.
CORS_ORIGINS = [
    o.strip() for o in os.environ.get("CORS_ORIGINS", "").split(",") if o.strip()
]

# Number of trusted reverse proxies in front of the app. Leave at 0 unless you
# run behind nginx/Traefik — setting it when you should not lets a client spoof
# its own address via X-Forwarded-For and evade the login throttle.
TRUSTED_PROXY_COUNT = int(os.environ.get("TRUSTED_PROXY_COUNT", 0))

# Send HSTS. Off by default: most self-hosted installs are reachable over plain
# HTTP on a LAN, and HSTS would make the browser refuse those.
ENABLE_HSTS = os.environ.get("ENABLE_HSTS", "0") == "1"

MODULES = ["shopping", "recipes", "mealplanner", "storage"]
