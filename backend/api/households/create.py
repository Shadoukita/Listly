import secrets

from flask import g, jsonify, request

from api.households import bp
from core.security import token_required
from lang.lang_config import t
from db.session import get_db


@bp.post("/households")
@token_required
def create_household():
    name = (request.get_json(silent=True) or {}).get("name", "").strip()
    if not name:
        return jsonify({"error": t("error.name_required")}), 400

    code = secrets.token_urlsafe(8)
    db   = get_db()
    cur  = db.execute(
        "INSERT INTO households (name, invite_code, created_by) VALUES (?, ?, ?)",
        (name, code, g.current_user["id"]),
    )
    hid = cur.lastrowid
    db.execute(
        "INSERT INTO household_members (household_id, user_id, role) VALUES (?, ?, 'owner')",
        (hid, g.current_user["id"]),
    )
    db.commit()
    return jsonify({"id": hid, "name": name, "invite_code": code, "role": "owner"}), 201
