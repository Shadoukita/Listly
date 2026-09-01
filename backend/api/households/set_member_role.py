from flask import g, jsonify, request

from api.households import bp
from core.security import token_required
from lang.lang_config import t
from core.utils import is_hh_owner
from db.session import get_db

_VALID_ROLES = ("owner", "admin", "member", "restricted")


@bp.put("/households/<int:hid>/members/<int:uid>/role")
@token_required
def set_member_role(hid, uid):
    if not is_hh_owner(hid):
        return jsonify({"error": t("error.household_owner_only")}), 403
    if uid == g.current_user["id"]:
        return jsonify({"error": t("error.cannot_change_own_role")}), 400

    role = (request.get_json(silent=True) or {}).get("role")
    if role not in _VALID_ROLES:
        return jsonify({"error": t("error.invalid_role")}), 400

    db = get_db()
    result = db.execute(
        "UPDATE household_members SET role = ? WHERE household_id = ? AND user_id = ?",
        (role, hid, uid),
    )
    if result.rowcount == 0:
        return jsonify({"error": t("error.not_found")}), 404
    db.commit()
    return jsonify({"ok": True, "role": role})
