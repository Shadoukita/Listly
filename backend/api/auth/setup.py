import sqlite3

from flask import jsonify, request

from api.auth import bp
from core.security import hash_pw, make_token
from lang.lang_config import t
from db.session import get_db
from db.models import udict


@bp.post("/setup")
def setup():
    db  = get_db()
    row = db.execute("SELECT setup_done FROM settings WHERE id = 1").fetchone()
    if row and row["setup_done"]:
        return jsonify({"error": t("error.setup_done")}), 400

    d        = (request.get_json(silent=True) or {})
    username = d.get("username", "").strip()
    password = d.get("password", "")
    endpoint = d.get("endpoint_url", "").strip().rstrip("/")

    if not username or not password:
        return jsonify({"error": t("error.credentials_required")}), 400
    if len(password) < 6:
        return jsonify({"error": t("error.password_too_short")}), 400

    try:
        db.execute(
            "INSERT INTO users (username, password_hash, role, display_name) VALUES (?, ?, 'admin', ?)",
            (username, hash_pw(password), username),
        )
        db.execute(
            "UPDATE settings SET setup_done = 1, endpoint_url = ? WHERE id = 1",
            (endpoint,),
        )
        db.commit()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        return jsonify({"token": make_token(user, True), "user": udict(user)}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": t("error.username_taken")}), 409
