import sqlite3

from flask import g, jsonify, request

from api.households import bp
from core.security import token_required
from lang.lang_config import t
from db.session import get_db


@bp.post("/households/join")
@token_required
def join_by_code():
    code = (request.get_json(silent=True) or {}).get("invite_code", "").strip()
    db   = get_db()
    hh   = db.execute(
        "SELECT * FROM households WHERE invite_code = ?", (code,)
    ).fetchone()
    if not hh:
        return jsonify({"error": t("error.invite_invalid")}), 404
    try:
        db.execute(
            "INSERT INTO household_members (household_id, user_id) VALUES (?, ?)",
            (hh["id"], g.current_user["id"]),
        )
        db.commit()
        return jsonify({"message": "Joined!", "household_id": hh["id"]})
    except sqlite3.IntegrityError:
        return jsonify({"error": t("error.already_member")}), 409
