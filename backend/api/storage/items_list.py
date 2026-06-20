from flask import jsonify

from api.storage import bp
from core.security import token_required
from lang.lang_config import t
from core.utils import has_access
from db.session import get_db
from db.models import storage_item_dict


@bp.get("/households/<int:hid>/storage/items")
@token_required
def list_storage_items(hid):
    if not has_access(hid):
        return jsonify({"error": t("error.no_access")}), 403

    rows = get_db().execute(
        """
        SELECT si.*,
               COALESCE(u.display_name, u.username) AS added_by_name
        FROM storage_items si
        LEFT JOIN users u ON si.added_by = u.id
        WHERE si.household_id = ?
        ORDER BY si.location_id, si.id
        """,
        (hid,),
    ).fetchall()
    return jsonify([storage_item_dict(r) for r in rows])
