from flask import jsonify, request

from api.storage import bp
from core.security import token_required
from lang.lang_config import t
from core.utils import is_hh_admin
from db.session import get_db
from db.models import storage_location_dict


@bp.post("/households/<int:hid>/storage/locations")
@token_required
def create_storage_location(hid):
    if not is_hh_admin(hid):
        return jsonify({"error": t("error.household_admins_only")}), 403

    d    = request.get_json(silent=True) or {}
    name = (d.get("name") or "").strip()
    if not name:
        return jsonify({"error": t("error.name_required")}), 400

    db  = get_db()
    nxt = db.execute(
        "SELECT COALESCE(MAX(sort_order)+1, 0) AS n FROM storage_locations WHERE household_id = ?",
        (hid,),
    ).fetchone()["n"]

    cur = db.execute(
        "INSERT INTO storage_locations (household_id, name, icon, tone, sort_order) VALUES (?,?,?,?,?)",
        (hid, name, d.get("icon", "shelf"), d.get("tone", "#9bd9ff"), nxt),
    )
    db.commit()
    row = db.execute(
        "SELECT * FROM storage_locations WHERE id = ?", (cur.lastrowid,)
    ).fetchone()
    return jsonify(storage_location_dict(row)), 201
