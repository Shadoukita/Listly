from flask import g, jsonify

from api.households import bp
from core.security import token_required
from lang.lang_config import t
from core.utils import get_member_role, ROLE_RANK
from db.session import get_db


@bp.delete("/households/<int:hid>/members/<int:uid>")
@token_required
def remove_member(hid, uid):
    my_role = get_member_role(hid)
    if not my_role or ROLE_RANK.get(my_role, 0) < ROLE_RANK["admin"]:
        return jsonify({"error": t("error.household_admins_only")}), 403
    if uid == g.current_user["id"]:
        return jsonify({"error": t("error.cannot_remove_self")}), 400

    db = get_db()
    target = db.execute(
        "SELECT role FROM household_members WHERE household_id = ? AND user_id = ?",
        (hid, uid),
    ).fetchone()
    if not target:
        return jsonify({"error": t("error.not_found")}), 404
    if ROLE_RANK.get(target["role"], 0) >= ROLE_RANK.get(my_role, 0):
        return jsonify({"error": t("error.no_access")}), 403

    db.execute(
        "DELETE FROM household_members WHERE household_id = ? AND user_id = ?",
        (hid, uid),
    )
    db.commit()
    return jsonify({"message": "Removed"})
