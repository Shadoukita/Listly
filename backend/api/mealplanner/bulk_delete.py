from flask import g, jsonify, request

from api.mealplanner import bp
from core.security import token_required
from lang.lang_config import t
from core.utils import is_hh_admin
from db.session import get_db


@bp.delete("/meal-plans/bulk")
@token_required
def bulk_delete_meal_plans():
    body = request.get_json(silent=True) or {}
    ids  = body.get("ids", [])
    if not ids or not isinstance(ids, list):
        return jsonify({"error": t("error.bulk_ids_required")}), 400

    db      = get_db()
    deleted = []
    denied  = []

    for pid in ids:
        row = db.execute("SELECT * FROM meal_plans WHERE id = ?", (pid,)).fetchone()
        if not row:
            continue
        is_owner = row["user_id"] == g.current_user["id"]
        if not is_owner and not is_hh_admin(row["household_id"]):
            denied.append(pid)
            continue
        db.execute("DELETE FROM meal_plans WHERE id = ?", (pid,))
        deleted.append(pid)

    db.commit()
    return jsonify({"deleted": deleted, "denied": denied})
