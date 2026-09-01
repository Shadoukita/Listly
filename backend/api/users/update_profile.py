from flask import g, jsonify, request

from api.users import bp
from core.security import hash_pw, make_token, token_required, verify_pw
from lang.lang_config import t
from db.session import get_db
from db.models import udict


@bp.put("/me/profile")
@token_required
def update_profile():
    d          = request.get_json(silent=True) or {}
    display    = d.get("display_name", "").strip()
    new_pw     = d.get("new_password", "")
    current_pw = d.get("current_password", "")
    uid        = g.current_user["id"]
    db         = get_db()

    # Validate the password change first — returning early after writing the
    # other fields would discard them (no commit runs on that path).
    if new_pw:
        if len(new_pw) < 6:
            return jsonify({"error": t("error.password_too_short")}), 400
        if not current_pw:
            return jsonify({"error": t("error.current_pw_required")}), 400
        if not verify_pw(current_pw, g.current_user["password_hash"]):
            return jsonify({"error": t("error.current_pw_wrong")}), 400

    if display:
        db.execute("UPDATE users SET display_name = ? WHERE id = ?", (display, uid))

    profile_image = d.get("profile_image")
    if profile_image is not None:
        db.execute("UPDATE users SET profile_image = ? WHERE id = ?", (profile_image, uid))

    if new_pw:
        # Bumping token_version invalidates every JWT issued for this account,
        # so a password change actually signs other sessions out.
        db.execute(
            "UPDATE users SET password_hash = ?, "
            "token_version = COALESCE(token_version, 0) + 1 WHERE id = ?",
            (hash_pw(new_pw), uid),
        )

    db.commit()
    user = db.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
    body = udict(user)

    # The caller's own token was just revoked along with the rest — hand back a
    # fresh one so the session that made the change stays signed in.
    if new_pw:
        body["token"] = make_token(user, True)

    return jsonify(body)
