from flask import g, jsonify, request

from api.users import bp
from core.security import hash_pw, token_required, verify_pw
from lang.lang_config import t
from db.session import get_db
from db.models import udict


@bp.put("/me/profile")
@token_required
def update_profile():
    d          = request.get_json()
    display    = d.get("display_name", "").strip()
    new_pw     = d.get("new_password", "")
    current_pw = d.get("current_password", "")
    db         = get_db()

    if display:
        db.execute(
            "UPDATE users SET display_name = ? WHERE id = ?",
            (display, g.current_user["id"]),
        )

    profile_image = d.get("profile_image")
    if profile_image is not None:
        db.execute(
            "UPDATE users SET profile_image = ? WHERE id = ?",
            (profile_image, g.current_user["id"]),
        )

    if new_pw:
        if len(new_pw) < 6:
            return jsonify({"error": t("error.password_too_short")}), 400
        if not current_pw:
            return jsonify({"error": t("error.current_pw_required")}), 400
        if not verify_pw(current_pw, g.current_user["password_hash"]):
            return jsonify({"error": t("error.current_pw_wrong")}), 400
        db.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (hash_pw(new_pw), g.current_user["id"]),
        )

    db.commit()
    user = db.execute("SELECT * FROM users WHERE id = ?", (g.current_user["id"],)).fetchone()
    return jsonify(udict(user))
