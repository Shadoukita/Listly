from flask import g, jsonify, request

from api.users import bp
from core.security import token_required
from lang.lang_config import t
from core.utils import has_access
from db.session import get_db


@bp.put("/me/household")
@token_required
def set_household():
    hid = request.get_json().get("household_id")
    if hid and not has_access(hid):
        return jsonify({"error": t("error.no_access")}), 403
    db = get_db()
    db.execute(
        "UPDATE users SET last_household_id = ? WHERE id = ?",
        (hid, g.current_user["id"]),
    )
    db.commit()
    return jsonify({"ok": True})
