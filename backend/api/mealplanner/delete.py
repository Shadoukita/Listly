from flask import g, jsonify

from api.mealplanner import bp
from core.security import token_required
from lang.lang_config import t
from core.utils import is_hh_admin
from db.session import get_db


@bp.delete("/meal-plans/<int:pid>")
@token_required
def delete_meal_plan(pid):
    db  = get_db()
    row = db.execute("SELECT * FROM meal_plans WHERE id = ?", (pid,)).fetchone()
    if not row:
        return jsonify({"error": t("error.not_found")}), 404

    is_owner = row["user_id"] == g.current_user["id"]
    if not is_owner and not is_hh_admin(row["household_id"]):
        return jsonify({"error": t("error.no_access")}), 403

    db.execute("DELETE FROM meal_plans WHERE id = ?", (pid,))
    db.commit()
    return jsonify({"ok": True})
