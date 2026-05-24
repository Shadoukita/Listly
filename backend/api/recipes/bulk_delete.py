from flask import g, jsonify, request

from api.recipes import bp
from api.recipes.delete import _delete_recipe_image
from core.security import token_required
from lang.lang_config import t
from core.utils import has_access
from db.session import get_db


@bp.delete("/recipes/bulk")
@token_required
def bulk_delete_recipes():
    ids = request.get_json(silent=True) or {}
    ids = ids.get("ids", [])
    if not ids or not isinstance(ids, list):
        return jsonify({"error": t("error.bulk_ids_required")}), 400

    db      = get_db()
    deleted = []
    denied  = []

    for rid in ids:
        row = db.execute("SELECT * FROM recipes WHERE id = ?", (rid,)).fetchone()
        if not row:
            continue
        if not has_access(row["household_id"]):
            denied.append(rid)
            continue
        if row["created_by"] != g.current_user["id"] and g.current_user.get("role") != "admin":
            denied.append(rid)
            continue
        _delete_recipe_image(row["image_url"])
        db.execute("DELETE FROM recipes WHERE id = ?", (rid,))
        deleted.append(rid)

    db.commit()
    return jsonify({"deleted": deleted, "denied": denied})
