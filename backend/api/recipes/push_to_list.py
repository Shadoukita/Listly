import json

from flask import g, jsonify

from api.recipes import bp
from core.security import token_required
from lang.lang_config import t
from core.utils import has_access
from db.session import get_db


@bp.post("/recipes/<int:rid>/push-to-list")
@token_required
def push_to_list(rid):
    db  = get_db()
    row = db.execute("SELECT * FROM recipes WHERE id = ?", (rid,)).fetchone()
    if not row:
        return jsonify({"error": t("error.not_found")}), 404

    in_hh = has_access(row["household_id"])
    if not in_hh and not row["is_public"]:
        return jsonify({"error": t("error.no_access")}), 403

    target_hh = g.current_user.get("last_household_id") or row["household_id"]
    if not has_access(target_hh):
        target_hh = row["household_id"]

    try:
        ingredients = json.loads(row["ingredients_json"] or "[]")
    except Exception:
        ingredients = []

    added = 0
    for ing in ingredients:
        name = (ing.get("name", "") if isinstance(ing, dict) else str(ing)).strip()
        if not name:
            continue
        qty = ing.get("quantity", "1") if isinstance(ing, dict) else "1"
        db.execute(
            "INSERT INTO shopping_items (household_id, name, quantity, category, added_by) VALUES (?, ?, ?, ?, ?)",
            (target_hh, name, qty or "1", "Rezept", g.current_user["id"]),
        )
        added += 1

    db.commit()
    return jsonify({"added": added})
