from flask import g, jsonify, request

from api.mealplanner import bp
from core.security import token_required
from core.utils import has_access
from db.session import get_db
from db.models import meal_plan_dict


@bp.get("/households/<int:hid>/meal-plans")
@token_required
def list_meal_plans(hid):
    if not has_access(hid):
        from lang.lang_config import t
        return jsonify({"error": t("error.no_access")}), 403

    from_date = request.args.get("from", "")
    to_date   = request.args.get("to",   "")
    scope     = request.args.get("scope", "mine")

    db = get_db()
    if scope == "household":
        rows = db.execute(
            """
            SELECT mp.*,
                   r.name        AS recipe_name,
                   r.description AS recipe_description,
                   COALESCE(u.display_name, u.username) AS user_name
            FROM meal_plans mp
            LEFT JOIN recipes r ON mp.recipe_id = r.id
            LEFT JOIN users   u ON mp.user_id    = u.id
            WHERE mp.household_id = ? AND mp.plan_date BETWEEN ? AND ?
            ORDER BY mp.plan_date, mp.sort_order
            """,
            (hid, from_date, to_date),
        ).fetchall()
    else:
        rows = db.execute(
            """
            SELECT mp.*,
                   r.name        AS recipe_name,
                   r.description AS recipe_description,
                   COALESCE(u.display_name, u.username) AS user_name
            FROM meal_plans mp
            LEFT JOIN recipes r ON mp.recipe_id = r.id
            LEFT JOIN users   u ON mp.user_id    = u.id
            WHERE mp.household_id = ? AND mp.plan_date BETWEEN ? AND ?
              AND mp.user_id = ?
            ORDER BY mp.plan_date, mp.sort_order
            """,
            (hid, from_date, to_date, g.current_user["id"]),
        ).fetchall()

    return jsonify([meal_plan_dict(r) for r in rows])
