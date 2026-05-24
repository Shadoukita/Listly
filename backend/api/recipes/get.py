from flask import jsonify

from api.recipes import bp
from core.security import token_required
from lang.lang_config import t
from core.utils import has_access
from db.session import get_db
from db.models import recipe_dict


@bp.get("/recipes/<int:rid>")
@token_required
def get_recipe(rid):
    row = get_db().execute("""
        SELECT r.*, COALESCE(u.display_name, u.username) AS created_by_name,
               u.profile_image AS created_by_profile_image
        FROM recipes r
        LEFT JOIN users u ON r.created_by = u.id
        WHERE r.id = ?
    """, (rid,)).fetchone()
    if not row:
        return jsonify({"error": t("error.not_found")}), 404
    if not row["is_public"] and not has_access(row["household_id"]):
        return jsonify({"error": t("error.no_access")}), 403
    return jsonify(recipe_dict(row))
