from flask import jsonify, request

from api.households import bp
from core.security import token_required
from lang.lang_config import t
from core.utils import is_hh_admin
from db.session import get_db
from db.models import hh_dict


@bp.patch("/households/<int:hid>")
@token_required
def update_household(hid):
    if not is_hh_admin(hid):
        return jsonify({"error": t("error.household_admins_only")}), 403

    d  = request.get_json()
    db = get_db()

    if name := d.get("name", "").strip():
        db.execute("UPDATE households SET name = ? WHERE id = ?", (name, hid))
    if "is_public" in d:
        db.execute(
            "UPDATE households SET is_public = ? WHERE id = ?",
            (1 if d["is_public"] else 0, hid),
        )

    db.commit()
    return jsonify(hh_dict(db.execute("SELECT * FROM households WHERE id = ?", (hid,)).fetchone()))
