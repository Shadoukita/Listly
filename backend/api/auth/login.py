from flask import jsonify, request

from api.auth import bp
from core import ratelimit
from core.security import hash_pw, make_token, needs_rehash, verify_pw
from lang.lang_config import t
from db.session import get_db
from db.models import udict


@bp.post("/login")
def login():
    d        = request.get_json(silent=True) or {}
    username = d.get("username", "").strip()
    password = d.get("password", "")
    db       = get_db()

    # Throttle before touching the password, so a locked account costs an
    # attacker a request without costing us a PBKDF2 derivation.
    keys = [f"user:{username.lower()}", f"ip:{request.remote_addr or 'unknown'}"]
    if retry_after := ratelimit.locked_for(db, keys):
        resp = jsonify({"error": t("error.too_many_attempts")})
        resp.headers["Retry-After"] = str(retry_after)
        return resp, 429

    user = db.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()

    if not user or not verify_pw(password, user["password_hash"]):
        ratelimit.register_failure(db, keys)
        return jsonify({"error": t("error.invalid_credentials")}), 401

    ratelimit.clear(db, keys)

    # Transparently upgrade legacy/low-iteration hashes now that we hold the
    # plaintext and know it is correct.
    if needs_rehash(user["password_hash"]):
        db.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (hash_pw(password), user["id"]),
        )
        db.commit()

    return jsonify({
        "token": make_token(user, d.get("remember", False)),
        "user":  udict(user),
    })
