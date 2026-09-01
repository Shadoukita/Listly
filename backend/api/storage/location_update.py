from flask import jsonify, request

from api.storage import bp
from core.security import token_required
from lang.lang_config import t
from core.utils import is_hh_admin
from db.session import get_db
from db.models import storage_location_dict

_ALLOWED_FIELDS = ["name", "icon", "tone", "sort_order"]


@bp.patch("/storage/locations/<int:lid>")
@token_required
def update_storage_location(lid):
    db  = get_db()
    row = db.execute("SELECT * FROM storage_locations WHERE id = ?", (lid,)).fetchone()
    if not row:
        return jsonify({"error": t("error.not_found")}), 404

    if not is_hh_admin(row["household_id"]):
        return jsonify({"error": t("error.household_admins_only")}), 403

    d       = request.get_json(silent=True) or {}
    updates = {f: d[f] for f in _ALLOWED_FIELDS if f in d}
    if not updates:
        return jsonify(storage_location_dict(row))

    set_clause = ", ".join(f"{f} = ?" for f in updates)
    db.execute(
        f"UPDATE storage_locations SET {set_clause} WHERE id = ?",
        list(updates.values()) + [lid],
    )
    db.commit()
    updated = db.execute(
        "SELECT * FROM storage_locations WHERE id = ?", (lid,)
    ).fetchone()
    return jsonify(storage_location_dict(updated))
