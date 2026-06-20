from flask import jsonify

from api.storage import bp
from core.security import token_required
from lang.lang_config import t
from core.utils import has_access
from db.session import get_db
from db.models import storage_location_dict


@bp.get("/households/<int:hid>/storage/locations")
@token_required
def list_storage_locations(hid):
    if not has_access(hid):
        return jsonify({"error": t("error.no_access")}), 403

    rows = get_db().execute(
        "SELECT * FROM storage_locations WHERE household_id = ? ORDER BY sort_order, id",
        (hid,),
    ).fetchall()
    return jsonify([storage_location_dict(r) for r in rows])
