from flask import g, jsonify, request

from api.mealplanner import bp
from core.security import token_required
from lang.lang_config import t
from core.utils import can_view_recipe, is_hh_admin
from db.session import get_db
from db.models import meal_plan_dict

_ALLOWED_FIELDS = [
    "plan_date", "kind", "recipe_id", "title", "description", "notes",
]


@bp.patch("/meal-plans/<int:pid>")
@token_required
def update_meal_plan(pid):
    db  = get_db()
    row = db.execute("SELECT * FROM meal_plans WHERE id = ?", (pid,)).fetchone()
    if not row:
        return jsonify({"error": t("error.not_found")}), 404

    is_owner = row["user_id"] == g.current_user["id"]
    if not is_owner and not is_hh_admin(row["household_id"]):
        return jsonify({"error": t("error.no_access")}), 403

    d       = request.get_json(silent=True) or {}
    updates = {f: d[f] for f in _ALLOWED_FIELDS if f in d}

    # Same leak as on create — a recipe_id the caller cannot see would come
    # straight back out through the JOIN below.
    if updates.get("recipe_id") is not None and not can_view_recipe(updates["recipe_id"]):
        return jsonify({"error": t("error.no_access")}), 403

    if not updates:
        return jsonify(meal_plan_dict(row))

    set_clause = ", ".join(f"{f} = ?" for f in updates)
    db.execute(
        f"UPDATE meal_plans SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        list(updates.values()) + [pid],
    )
    db.commit()
    updated = db.execute(
        """
        SELECT mp.*,
               r.name        AS recipe_name,
               r.description AS recipe_description,
               COALESCE(u.display_name, u.username) AS user_name
        FROM meal_plans mp
        LEFT JOIN recipes r ON mp.recipe_id = r.id
        LEFT JOIN users   u ON mp.user_id    = u.id
        WHERE mp.id = ?
        """,
        (pid,),
    ).fetchone()
    return jsonify(meal_plan_dict(updated))
