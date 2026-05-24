from flask import jsonify

from api.shopping import bp
from core.security import token_required
from lang.lang_config import t
from core.utils import has_access
from db.session import get_db


@bp.delete("/items/<int:iid>")
@token_required
def delete_item(iid):
    db   = get_db()
    item = db.execute("SELECT * FROM shopping_items WHERE id = ?", (iid,)).fetchone()
    if not item:
        return jsonify({"error": t("error.not_found")}), 404
    if not has_access(item["household_id"]):
        return jsonify({"error": t("error.no_access")}), 403
    db.execute("DELETE FROM shopping_items WHERE id = ?", (iid,))
    db.commit()
    return jsonify({"message": "Deleted"})
