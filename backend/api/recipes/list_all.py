from flask import g, jsonify

from api.recipes import bp
from core.security import token_required
from db.session import get_db
from db.models import recipe_dict

_SELECT = """
    SELECT r.*, COALESCE(u.display_name, u.username, 'Deleted User') AS created_by_name,
           u.profile_image AS created_by_profile_image,
           h.name AS household_name
    FROM recipes r
    LEFT JOIN users u ON r.created_by  = u.id
    LEFT JOIN households h ON r.household_id = h.id
"""


@bp.get("/recipes/all")
@token_required
def list_all_recipes():
    db      = get_db()
    user_hh = [
        r["household_id"]
        for r in db.execute(
            "SELECT household_id FROM household_members WHERE user_id = ?",
            (g.current_user["id"],),
        ).fetchall()
    ]

    if user_hh:
        placeholders = ", ".join("?" * len(user_hh))
        rows = db.execute(
            f"{_SELECT} WHERE r.household_id IN ({placeholders}) OR r.is_public = 1"
            " ORDER BY r.created_at DESC",
            user_hh,
        ).fetchall()
    else:
        rows = db.execute(
            f"{_SELECT} WHERE r.is_public = 1 ORDER BY r.created_at DESC"
        ).fetchall()

    # Deduplicate — a recipe can match both the household and is_public conditions
    seen, result = set(), []
    for r in rows:
        if r["id"] not in seen:
            seen.add(r["id"])
            result.append(recipe_dict(r))
    return jsonify(result)
