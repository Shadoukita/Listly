from flask import g, jsonify

from api.recipes import bp
from core.security import token_required
from db.session import get_db


@bp.post("/recipes/<int:rid>/favorite")
@token_required
def add_favorite(rid):
    db  = get_db()
    uid = g.current_user["id"]
    db.execute(
        "INSERT OR IGNORE INTO recipe_favorites (user_id, recipe_id) VALUES (?, ?)",
        (uid, rid),
    )
    db.commit()
    return jsonify({"is_favorited": True})


@bp.delete("/recipes/<int:rid>/favorite")
@token_required
def remove_favorite(rid):
    db  = get_db()
    uid = g.current_user["id"]
    db.execute(
        "DELETE FROM recipe_favorites WHERE user_id = ? AND recipe_id = ?",
        (uid, rid),
    )
    db.commit()
    return jsonify({"is_favorited": False})
