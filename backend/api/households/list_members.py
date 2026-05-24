from flask import jsonify

from api.households import bp
from core.security import token_required
from lang.lang_config import t
from core.utils import has_access
from db.session import get_db


@bp.get("/households/<int:hid>/members")
@token_required
def list_members(hid):
    if not has_access(hid):
        return jsonify({"error": t("error.no_access")}), 403
    rows = get_db().execute("""
        SELECT u.id, u.username, COALESCE(u.display_name, u.username) AS display_name,
               u.profile_image, hm.role, hm.joined_at
        FROM household_members hm
        JOIN users u ON hm.user_id = u.id
        WHERE hm.household_id = ?
    """, (hid,)).fetchall()
    return jsonify([dict(r) for r in rows])
