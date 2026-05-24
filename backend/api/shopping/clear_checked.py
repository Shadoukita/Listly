from flask import jsonify

from api.shopping import bp
from core.security import token_required
from lang.lang_config import t
from core.utils import has_access
from db.session import get_db


@bp.delete("/households/<int:hid>/items/clear-checked")
@token_required
def clear_checked(hid):
    if not has_access(hid):
        return jsonify({"error": t("error.no_access")}), 403
    db = get_db()
    db.execute(
        "DELETE FROM shopping_items WHERE household_id = ? AND checked = 1", (hid,)
    )
    db.commit()
    return jsonify({"message": "Cleared"})
