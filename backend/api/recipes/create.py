from flask import g, jsonify, request

from api.recipes import bp
from core.security import token_required
from lang.lang_config import t
from core.utils import get_member_role
from db.session import get_db
from db.models import recipe_dict


@bp.post("/households/<int:hid>/recipes")
@token_required
def create_recipe(hid):
    my_role = get_member_role(hid)
    if not my_role:
        return jsonify({"error": t("error.no_access")}), 403
    if my_role == "restricted":
        return jsonify({"error": t("error.no_access")}), 403

    d    = request.get_json()
    name = d.get("name", "").strip()
    if not name:
        return jsonify({"error": t("error.name_required")}), 400

    is_public = 0 if d.get("is_public") is False else 1
    cal_raw       = d.get("calories")
    calories      = int(cal_raw) if cal_raw not in (None, "") else None
    calories_unit = d.get("calories_unit") or "100g"
    db  = get_db()
    cur = db.execute("""
        INSERT INTO recipes
            (household_id, name, description, image_url, prep_time, cook_time,
             servings, difficulty, source_url, tags_json, ingredients_json,
             steps_json, methods_json, calories, calories_unit, is_public, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        hid, name,
        d.get("description"), d.get("image_url"),
        d.get("prep_time"),   d.get("cook_time"),
        d.get("servings"),    d.get("difficulty"),
        d.get("source_url"),
        d.get("tags_json",        "[]"),
        d.get("ingredients_json", "[]"),
        d.get("steps_json",       "[]"),
        d.get("methods_json"),
        calories, calories_unit,
        is_public,
        g.current_user["id"],
    ))
    db.commit()
    row = db.execute("""
        SELECT r.*, COALESCE(u.display_name, u.username) AS created_by_name
        FROM recipes r LEFT JOIN users u ON r.created_by = u.id WHERE r.id = ?
    """, (cur.lastrowid,)).fetchone()
    return jsonify(recipe_dict(row)), 201
