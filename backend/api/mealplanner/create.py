from flask import g, jsonify, request

from api.mealplanner import bp
from core.security import token_required
from lang.lang_config import t
from core.utils import get_member_role
from db.session import get_db
from db.models import meal_plan_dict


@bp.post("/households/<int:hid>/meal-plans")
@token_required
def create_meal_plan(hid):
    role = get_member_role(hid)
    if not role:
        return jsonify({"error": t("error.no_access")}), 403
    if role == "restricted":
        return jsonify({"error": t("error.no_access")}), 403

    d    = request.get_json() or {}
    date = (d.get("plan_date") or "").strip()
    kind = d.get("kind", "manual")

    if not date:
        return jsonify({"error": t("error.date_required")}), 400
    if kind == "recipe" and not d.get("recipe_id"):
        return jsonify({"error": t("error.recipe_required")}), 400
    if kind == "manual" and not (d.get("title") or "").strip():
        return jsonify({"error": t("error.title_required")}), 400

    db  = get_db()
    nxt = db.execute(
        "SELECT COALESCE(MAX(sort_order)+1, 0) AS n FROM meal_plans "
        "WHERE household_id=? AND plan_date=? AND user_id=?",
        (hid, date, g.current_user["id"]),
    ).fetchone()["n"]

    cur = db.execute(
        """
        INSERT INTO meal_plans
            (household_id, user_id, plan_date, kind, recipe_id,
             title, description, notes, sort_order)
        VALUES (?,?,?,?,?,?,?,?,?)
        """,
        (
            hid, g.current_user["id"], date, kind,
            d.get("recipe_id"),
            d.get("title"), d.get("description"), d.get("notes"),
            nxt,
        ),
    )
    db.commit()
    row = db.execute(
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
        (cur.lastrowid,),
    ).fetchone()
    return jsonify(meal_plan_dict(row)), 201
