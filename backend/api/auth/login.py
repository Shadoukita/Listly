from flask import jsonify, request

from api.auth import bp
from core.security import make_token, verify_pw
from lang.lang_config import t
from db.session import get_db
from db.models import udict


@bp.post("/login")
def login():
    d    = request.get_json()
    user = get_db().execute(
        "SELECT * FROM users WHERE username = ?",
        (d.get("username", "").strip(),),
    ).fetchone()
    if not user or not verify_pw(d.get("password", ""), user["password_hash"]):
        return jsonify({"error": t("error.invalid_credentials")}), 401
    return jsonify({
        "token": make_token(user["id"], d.get("remember", False)),
        "user":  udict(user),
    })
