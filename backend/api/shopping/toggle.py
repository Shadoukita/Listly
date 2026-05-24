from datetime import datetime

from flask import g, jsonify

from api.shopping import bp
from core.security import token_required
from lang.lang_config import t
from core.utils import has_access
from db.session import get_db


@bp.patch("/items/<int:iid>/toggle")
@token_required
def toggle_item(iid):
    db   = get_db()
    item = db.execute("SELECT * FROM shopping_items WHERE id = ?", (iid,)).fetchone()
    if not item:
        return jsonify({"error": t("error.not_found")}), 404
    if not has_access(item["household_id"]):
        return jsonify({"error": t("error.no_access")}), 403

    new_checked = 0 if item["checked"] else 1
    db.execute(
        "UPDATE shopping_items "
        "SET checked = ?, checked_by = ?, checked_at = ?, updated_at = CURRENT_TIMESTAMP "
        "WHERE id = ?",
        (
            new_checked,
            g.current_user["id"] if new_checked else None,
            datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") if new_checked else None,
            iid,
        ),
    )
    db.commit()
    return jsonify({"id": iid, "checked": bool(new_checked)})
