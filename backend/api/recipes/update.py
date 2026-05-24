from flask import g, jsonify, request

from api.recipes import bp
from core.security import token_required
from lang.lang_config import t
from core.utils import get_member_role, ROLE_RANK
from db.session import get_db
from db.models import recipe_dict

_ALLOWED_FIELDS = [
    "name", "description", "image_url", "prep_time", "cook_time",
    "servings", "difficulty", "source_url", "tags_json",
    "ingredients_json", "steps_json", "methods_json", "calories", "calories_unit", "is_public",
]


@bp.patch("/recipes/<int:rid>")
@token_required
def update_recipe(rid):
    db  = get_db()
    row = db.execute("SELECT * FROM recipes WHERE id = ?", (rid,)).fetchone()
    if not row:
        return jsonify({"error": t("error.not_found")}), 404

    # Global admin can always edit
    if g.current_user.get("role") != "admin":
        my_role = get_member_role(row["household_id"])
        # Must be a member with at least 'member' rank to edit
        if not my_role or ROLE_RANK.get(my_role, 0) < ROLE_RANK["member"]:
            return jsonify({"error": t("error.no_access")}), 403

    d       = request.get_json()
    updates = {f: d[f] for f in _ALLOWED_FIELDS if f in d}
    if "is_public" in updates:
        updates["is_public"] = 1 if updates["is_public"] else 0
    if "calories" in updates:
        cal = updates["calories"]
        updates["calories"] = int(cal) if cal not in (None, "") else None
    if not updates:
        return jsonify(recipe_dict(row))

    set_clause = ", ".join(f"{f} = ?" for f in updates)
    db.execute(
        f"UPDATE recipes SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        list(updates.values()) + [rid],
    )
    db.commit()
    updated = db.execute("""
        SELECT r.*, COALESCE(u.display_name, u.username) AS created_by_name
        FROM recipes r LEFT JOIN users u ON r.created_by = u.id WHERE r.id = ?
    """, (rid,)).fetchone()
    return jsonify(recipe_dict(updated))
