"""
Security helpers and route decorators.

  hash_pw / verify_pw   — PBKDF2-SHA256 password hashing
  make_token            — issue a signed JWT
  token_required        — decorator: validates Bearer token, sets g.current_user
  admin_required        — decorator: requires role == 'admin' (use after token_required)
"""
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import g, jsonify, request

from core.config import SECRET_KEY
from lang.lang_config import t
from db.session import get_db


def hash_pw(password: str) -> str:
    salt   = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()
    return f"{salt}:{digest}"


def verify_pw(password: str, stored: str) -> bool:
    salt, digest = stored.split(":")
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex() == digest


def make_token(user_id: int, remember: bool = False) -> str:
    return jwt.encode(
        {
            "user_id": user_id,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(days=365 if remember else 1),
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
            g.current_user = dict(user)
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
