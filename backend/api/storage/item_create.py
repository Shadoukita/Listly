from flask import g, jsonify, request

from api.storage import bp
from core.security import token_required
from lang.lang_config import t
from core.utils import get_member_role, location_in_household
from db.session import get_db
from db.models import storage_item_dict


@bp.post("/households/<int:hid>/storage/items")
@token_required
def create_storage_item(hid):
    role = get_member_role(hid)
    if not role:
        return jsonify({"error": t("error.no_access")}), 403
    if role == "restricted":
        return jsonify({"error": t("error.no_access")}), 403

    d    = request.get_json(silent=True) or {}
    name = (d.get("name") or "").strip()
    if not name:
        return jsonify({"error": t("error.name_required")}), 400

    location_id = d.get("location_id")
    if not location_id:
        return jsonify({"error": t("error.not_found")}), 400
    # Must be a location of *this* household, not an arbitrary ID
    if not location_in_household(location_id, hid):
        return jsonify({"error": t("error.not_found")}), 400

    db  = get_db()
    cur = db.execute(
        """
        INSERT INTO storage_items
            (household_id, location_id, name, quantity, unit, low_threshold, added_by)
        VALUES (?,?,?,?,?,?,?)
        """,
        (
            hid, location_id, name,
            int(d.get("quantity") or 0),
            d.get("unit", ""),
            int(d.get("low_threshold") or 0),
            g.current_user["id"],
        ),
    )
    db.commit()
    row = db.execute(
        """
        SELECT si.*,
               COALESCE(u.display_name, u.username) AS added_by_name
        FROM storage_items si
        LEFT JOIN users u ON si.added_by = u.id
        WHERE si.id = ?
        """,
        (cur.lastrowid,),
    ).fetchone()
    return jsonify(storage_item_dict(row)), 201
