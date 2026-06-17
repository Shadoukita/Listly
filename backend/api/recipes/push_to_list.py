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

    body = request.get_json(silent=True) or {}

    # If the frontend passes pre-scaled items, use those directly.
    custom_items = body.get("items")

    if custom_items is not None:
        flat = custom_items
    else:
        try:
            ingredients = json.loads(row["ingredients_json"] or "[]")
        except Exception:
            ingredients = []

        # Support both the new sectioned format and the legacy flat format.
        # New:  [{"name": "Section", "items": [{"name": "Butter", "quantity": "125g"}, …]}, …]
        # Old:  [{"name": "Butter", "quantity": "125g"}, …]
        def _flat_items(ing_list):
            if ing_list and isinstance(ing_list[0], dict) and "items" in ing_list[0]:
                for section in ing_list:
                    yield from (section.get("items") or [])
            else:
                yield from ing_list

        flat = list(_flat_items(ingredients))

    added = 0
    for ing in flat:
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
