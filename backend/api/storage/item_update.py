from flask import jsonify, request

from api.storage import bp
from core.security import token_required
from lang.lang_config import t
from core.utils import has_access
from db.session import get_db
from db.models import storage_item_dict

_ALLOWED_FIELDS = ["name", "location_id", "quantity", "unit", "low_threshold"]


@bp.patch("/storage/items/<int:iid>")
@token_required
def update_storage_item(iid):
    db  = get_db()
    row = db.execute("SELECT * FROM storage_items WHERE id = ?", (iid,)).fetchone()
    if not row:
        return jsonify({"error": t("error.not_found")}), 404

    if not has_access(row["household_id"]):
        return jsonify({"error": t("error.no_access")}), 403

    d       = request.get_json() or {}
    updates = {f: d[f] for f in _ALLOWED_FIELDS if f in d}
    # Coerce numeric fields
    for field in ("quantity", "low_threshold", "location_id"):
        if field in updates:
            updates[field] = int(updates[field] or 0)

    if not updates:
        return jsonify(storage_item_dict(row))

    set_clause = ", ".join(f"{f} = ?" for f in updates)
    db.execute(
        f"UPDATE storage_items SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        list(updates.values()) + [iid],
    )
    db.commit()
    updated = db.execute(
        """
        SELECT si.*,
               COALESCE(u.display_name, u.username) AS added_by_name
        FROM storage_items si
        LEFT JOIN users u ON si.added_by = u.id
        WHERE si.id = ?
        """,
        (iid,),
    ).fetchone()
    return jsonify(storage_item_dict(updated))
