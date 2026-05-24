import secrets

from flask import jsonify

from api.households import bp
from core.security import token_required
from lang.lang_config import t
from core.utils import is_hh_admin
from db.session import get_db


@bp.post("/households/<int:hid>/regenerate-code")
@token_required
def regenerate_code(hid):
    if not is_hh_admin(hid):
        return jsonify({"error": t("error.household_admins_only")}), 403
    code = secrets.token_urlsafe(8)
    db   = get_db()
    db.execute("UPDATE households SET invite_code = ? WHERE id = ?", (code, hid))
    db.commit()
    return jsonify({"invite_code": code})
