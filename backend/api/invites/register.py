import sqlite3

from flask import jsonify, request

from api.invites import bp
from core.security import hash_pw, make_token
from core.invites import VALID_INVITE_SQL
from lang.lang_config import t
from db.session import get_db
from db.models import udict


@bp.post("/invite/<token>/register")
def register_with_invite(token):
    db  = get_db()
    inv = db.execute(
        f"SELECT * FROM invite_links WHERE token = ? AND {VALID_INVITE_SQL}", (token,)
    ).fetchone()
    if not inv:
        return jsonify({"error": t("error.invite_invalid")}), 404

    d        = (request.get_json(silent=True) or {})
    username = d.get("username", "").strip()
    password = d.get("password", "")

    if not username or not password:
        return jsonify({"error": t("error.credentials_required")}), 400
    if len(password) < 6:
        return jsonify({"error": t("error.password_too_short")}), 400

    try:
        db.execute(
            "INSERT INTO users (username, password_hash, role, display_name) VALUES (?, ?, 'member', ?)",
            (username, hash_pw(password), username),
        )
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        db.execute(
            "UPDATE invite_links SET used = 1, used_by = ? WHERE id = ?",
            (user["id"], inv["id"]),
        )
        db.commit()
        return jsonify({"token": make_token(user, True), "user": udict(user)}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": t("error.username_taken")}), 409
