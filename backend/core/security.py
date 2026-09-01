"""
Security helpers and route decorators.

  hash_pw / verify_pw   — PBKDF2-SHA256 password hashing
  needs_rehash          — True when a stored hash uses outdated parameters
  make_token            — issue a signed JWT bound to the user's token_version
  token_required        — decorator: validates Bearer token, sets g.current_user
  admin_required        — decorator: requires role == 'admin' (use after token_required)

Password hash format
────────────────────
    pbkdf2_sha256$<iterations>$<salt_hex>$<digest_hex>

The legacy two-field format (`<salt_hex>:<digest_hex>`, 100_000 iterations) is
still verified so existing accounts keep working; those hashes are upgraded
in place on the next successful login. See api/auth/login.py.

Token revocation
────────────────
Every JWT carries the issuing user's `token_version`. Bumping
users.token_version invalidates every token ever issued for that account —
that is what makes a password change actually log other sessions out.
"""
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import g, jsonify, request

from core.config import SECRET_KEY
from lang.lang_config import t
from db.session import get_db

_ALGORITHM        = "pbkdf2_sha256"
_ITERATIONS       = 600_000   # OWASP guidance for PBKDF2-HMAC-SHA256
_LEGACY_ITERATIONS = 100_000

# Token lifetimes. "Remember me" is long-lived but no longer unbounded, and
# token_version means a leaked token can always be revoked.
_TTL_DEFAULT  = timedelta(days=1)
_TTL_REMEMBER = timedelta(days=30)


def _derive(password: str, salt: str, iterations: int) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), iterations
    ).hex()


def hash_pw(password: str) -> str:
    salt = secrets.token_hex(16)
    return f"{_ALGORITHM}${_ITERATIONS}${salt}${_derive(password, salt, _ITERATIONS)}"


def _parse(stored: str) -> tuple[str, str, int] | None:
    """Return (salt, digest, iterations) for either hash format, or None if malformed."""
    if stored.startswith(f"{_ALGORITHM}$"):
        try:
            _, raw_iterations, salt, digest = stored.split("$", 3)
            return salt, digest, int(raw_iterations)
        except ValueError:
            return None
    # Legacy "<salt>:<digest>" at a fixed 100k iterations
    try:
        salt, digest = stored.split(":", 1)
    except ValueError:
        return None
    return salt, digest, _LEGACY_ITERATIONS


def verify_pw(password: str, stored: str) -> bool:
    """Constant-time password check. Returns False for a malformed hash, never raises."""
    parsed = _parse(stored or "")
    if not parsed:
        return False
    salt, digest, iterations = parsed
    try:
        candidate = _derive(password, salt, iterations)
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(candidate, digest)


def needs_rehash(stored: str) -> bool:
    """True when the stored hash should be replaced with current parameters."""
    parsed = _parse(stored or "")
    if not parsed:
        return True
    _, _, iterations = parsed
    return not stored.startswith(f"{_ALGORITHM}$") or iterations < _ITERATIONS


def token_version_of(user) -> int:
    """Read token_version from a sqlite3.Row or dict, defaulting to 0."""
    try:
        value = user["token_version"]
    except (KeyError, IndexError):
        return 0
    return int(value or 0)


def make_token(user, remember: bool = False) -> str:
    """Issue a JWT for a user row (or dict). Bound to the row's token_version."""
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "user_id": user["id"],
            "tv":      token_version_of(user),
            "iat":     now,
            "exp":     now + (_TTL_REMEMBER if remember else _TTL_DEFAULT),
        },
        SECRET_KEY,
        algorithm="HS256",
    )


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        token  = header[7:] if header.startswith("Bearer ") else None
        if not token:
            return jsonify({"error": t("error.token_missing")}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user = get_db().execute(
                "SELECT * FROM users WHERE id = ?", (data["user_id"],)
            ).fetchone()
            if not user:
                return jsonify({"error": t("error.user_not_found")}), 401
            user = dict(user)
            # Revocation check — a stale token_version means the credential
            # changed (or the session was revoked) after this token was issued.
            if int(data.get("tv", 0)) != token_version_of(user):
                return jsonify({"error": t("error.token_invalid")}), 401
            g.current_user = user
        except jwt.ExpiredSignatureError:
            return jsonify({"error": t("error.token_expired")}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": t("error.token_invalid")}), 401
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if g.current_user.get("role") != "admin":
            return jsonify({"error": t("error.admins_only")}), 403
        return f(*args, **kwargs)
    return decorated
