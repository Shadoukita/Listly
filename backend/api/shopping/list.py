from flask import jsonify

from api.shopping import bp
from core.security import token_required
from lang.lang_config import t
from core.utils import has_access
from db.session import get_db
from db.models import item_dict

_SELECT = """
    SELECT si.*,
           COALESCE(u1.display_name, u1.username, 'Deleted User') AS added_by_name,
           COALESCE(u2.display_name, u2.username, 'Deleted User') AS checked_by_name,
           u1.profile_image AS added_by_profile_image,
           u2.profile_image AS checked_by_profile_image
    FROM shopping_items si
    LEFT JOIN users u1 ON si.added_by   = u1.id
    LEFT JOIN users u2 ON si.checked_by = u2.id
"""


@bp.get("/households/<int:hid>/items")
@token_required
def list_items(hid):
    if not has_access(hid):
        return jsonify({"error": t("error.no_access")}), 403
    rows = get_db().execute(
        _SELECT + " WHERE si.household_id = ? ORDER BY si.checked ASC, si.created_at DESC",
        (hid,),
    ).fetchall()
    return jsonify([item_dict(r) for r in rows])
