from flask import jsonify

from api.recipes import bp
from core.security import token_required
from core.utils import has_access
from db.session import get_db
from db.models import recipe_dict


@bp.get("/households/<int:hid>/recipes")
@token_required
def list_recipes(hid):
    if not has_access(hid):
        return jsonify({"error": "No access"}), 403
    rows = get_db().execute("""
        SELECT r.*, COALESCE(u.display_name, u.username, 'Deleted User') AS created_by_name,
               u.profile_image AS created_by_profile_image,
               h.name AS household_name
        FROM recipes r
        LEFT JOIN users u ON r.created_by  = u.id
        LEFT JOIN households h ON r.household_id = h.id
        WHERE r.household_id = ?
        ORDER BY r.created_at DESC
    """, (hid,)).fetchall()
    return jsonify([recipe_dict(r) for r in rows])
