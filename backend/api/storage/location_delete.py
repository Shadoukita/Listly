from flask import jsonify

from api.storage import bp
from core.security import token_required
from lang.lang_config import t
from core.utils import is_hh_admin
from db.session import get_db


@bp.delete("/storage/locations/<int:lid>")
@token_required
def delete_storage_location(lid):
    db  = get_db()
    row = db.execute("SELECT * FROM storage_locations WHERE id = ?", (lid,)).fetchone()
    if not row:
        return jsonify({"error": t("error.not_found")}), 404

    if not is_hh_admin(row["household_id"]):
        return jsonify({"error": t("error.household_admins_only")}), 403

    # Items cascade via FK ON DELETE CASCADE
    db.execute("DELETE FROM storage_locations WHERE id = ?", (lid,))
    db.commit()
    return jsonify({"ok": True})
