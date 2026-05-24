import glob
import os

from flask import g, jsonify

from api.recipes import bp
from core.config import ASSETS_DIR
from core.security import token_required
from lang.lang_config import t
from core.utils import get_member_role, ROLE_RANK
from db.session import get_db


def _delete_recipe_image(image_url: str | None) -> None:
    """Remove the local image file for a recipe if it lives in assets/recipes/."""
    if not image_url or not image_url.startswith("/assets/recipes/"):
        return
    filename = image_url.split("/assets/recipes/")[-1]
    for path in glob.glob(os.path.join(ASSETS_DIR, "recipes", filename)):
        try:
            os.remove(path)
        except OSError:
            pass


@bp.delete("/recipes/<int:rid>")
@token_required
def delete_recipe(rid):
    db  = get_db()
    row = db.execute("SELECT * FROM recipes WHERE id = ?", (rid,)).fetchone()
    if not row:
        return jsonify({"error": t("error.not_found")}), 404

    # Global admin can always delete
    if g.current_user.get("role") != "admin":
        my_role = get_member_role(row["household_id"])
        # Must be at least household admin rank to delete
        if not my_role or ROLE_RANK.get(my_role, 0) < ROLE_RANK["admin"]:
            return jsonify({"error": t("error.no_access")}), 403

    _delete_recipe_image(row["image_url"])
    db.execute("DELETE FROM recipes WHERE id = ?", (rid,))
    db.commit()
    return jsonify({"ok": True})
