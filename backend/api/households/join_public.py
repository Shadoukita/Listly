import sqlite3

from flask import g, jsonify

from api.households import bp
from core.security import token_required
from lang.lang_config import t
from db.session import get_db


@bp.post("/households/<int:hid>/join-public")
@token_required
def join_public_household(hid):
    db = get_db()
    hh = db.execute(
        "SELECT * FROM households WHERE id = ? AND is_public = 1", (hid,)
    ).fetchone()
    if not hh:
        return jsonify({"error": t("error.household_not_public")}), 404
    try:
        db.execute(
            "INSERT INTO household_members (household_id, user_id) VALUES (?, ?)",
            (hid, g.current_user["id"]),
        )
        db.commit()
        return jsonify({"message": "Joined!", "household_id": hid})
    except sqlite3.IntegrityError:
        return jsonify({"error": t("error.already_member")}), 409
