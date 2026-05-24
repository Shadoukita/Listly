from flask import jsonify

from api.households import bp
from core.security import token_required
from lang.lang_config import t
from core.utils import is_hh_owner
from db.session import get_db


@bp.delete("/households/<int:hid>")
@token_required
def delete_household(hid):
    if not is_hh_owner(hid):
        return jsonify({"error": t("error.household_owner_only")}), 403
    db = get_db()
    db.execute("DELETE FROM households WHERE id = ?", (hid,))
    db.commit()
    return jsonify({"message": "Deleted"})
