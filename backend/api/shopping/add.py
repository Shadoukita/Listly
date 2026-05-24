from flask import g, jsonify, request

from api.shopping import bp
from core.security import token_required
from lang.lang_config import t
from core.utils import has_access
from db.session import get_db
from db.models import item_dict

_SELECT = """
    SELECT si.*,
           COALESCE(u1.display_name, u1.username) AS added_by_name,
           COALESCE(u2.display_name, u2.username) AS checked_by_name
    FROM shopping_items si
    LEFT JOIN users u1 ON si.added_by   = u1.id
    LEFT JOIN users u2 ON si.checked_by = u2.id
"""


@bp.post("/households/<int:hid>/items")
@token_required
def add_item(hid):
    if not has_access(hid):
        return jsonify({"error": t("error.no_access")}), 403
    d    = request.get_json()
    name = d.get("name", "").strip()
    if not name:
        return jsonify({"error": t("error.name_required")}), 400
    db  = get_db()
    cur = db.execute(
        "INSERT INTO shopping_items (household_id, name, quantity, category, added_by) VALUES (?, ?, ?, ?, ?)",
        (hid, name, d.get("quantity", "1"), d.get("category", "Sonstiges"), g.current_user["id"]),
    )
    db.commit()
    item = db.execute(_SELECT + " WHERE si.id = ?", (cur.lastrowid,)).fetchone()
    return jsonify(item_dict(item)), 201
