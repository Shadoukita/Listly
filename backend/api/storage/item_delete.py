from flask import jsonify

from api.storage import bp
from core.security import token_required
from lang.lang_config import t
from core.utils import has_access
from db.session import get_db


@bp.delete("/storage/items/<int:iid>")
@token_required
def delete_storage_item(iid):
    db  = get_db()
    row = db.execute("SELECT * FROM storage_items WHERE id = ?", (iid,)).fetchone()
    if not row:
        return jsonify({"error": t("error.not_found")}), 404

    if not has_access(row["household_id"]):
        return jsonify({"error": t("error.no_access")}), 403

    db.execute("DELETE FROM storage_items WHERE id = ?", (iid,))
    db.commit()
    return jsonify({"ok": True})
