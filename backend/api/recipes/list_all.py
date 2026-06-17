from flask import g, jsonify

from api.recipes import bp
from core.security import token_required
from db.session import get_db
from db.models import recipe_dict


def _select(uid):
    return f"""
        SELECT r.*,
               COALESCE(u.display_name, u.username, 'Deleted User') AS created_by_name,
               u.profile_image AS created_by_profile_image,
               h.name AS household_name,
               CASE WHEN rf.user_id IS NOT NULL THEN 1 ELSE 0 END AS is_favorited
        FROM recipes r
        LEFT JOIN users u  ON r.created_by   = u.id
        LEFT JOIN households h ON r.household_id = h.id
        LEFT JOIN recipe_favorites rf ON rf.recipe_id = r.id AND rf.user_id = {uid}
    """


@bp.get("/recipes/all")
@token_required
def list_all_recipes():
    db   = get_db()
    uid  = g.current_user["id"]
    user_hh = [
        r["household_id"]
        for r in db.execute(
            "SELECT household_id FROM household_members WHERE user_id = ?",
            (uid,),
        ).fetchall()
    ]

    sel = _select(uid)
    if user_hh:
        placeholders = ", ".join("?" * len(user_hh))
        rows = db.execute(
            f"{sel} WHERE r.household_id IN ({placeholders}) OR r.is_public = 1"
            " ORDER BY r.created_at DESC",
            user_hh,
        ).fetchall()
    else:
        rows = db.execute(
            f"{sel} WHERE r.is_public = 1 ORDER BY r.created_at DESC"
        ).fetchall()

    # Deduplicate — a recipe can match both the household and is_public conditions
    seen, result = set(), []
    for r in rows:
        if r["id"] not in seen:
            seen.add(r["id"])
            result.append(recipe_dict(r))
    return jsonify(result)
