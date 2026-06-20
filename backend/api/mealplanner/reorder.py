from flask import jsonify, request

from api.mealplanner import bp
from core.security import token_required
from lang.lang_config import t
from core.utils import has_access
from db.session import get_db


@bp.patch("/households/<int:hid>/meal-plans/reorder")
@token_required
def reorder_meal_plans(hid):
    if not has_access(hid):
        return jsonify({"error": t("error.no_access")}), 403

    body      = request.get_json() or {}
    plan_date = body.get("plan_date", "")
    ids       = body.get("ids", [])
    if not plan_date or not ids:
        return jsonify({"error": t("error.date_required")}), 400

    db = get_db()
    for order, pid in enumerate(ids):
        db.execute(
            "UPDATE meal_plans SET sort_order = ? WHERE id = ? AND household_id = ? AND plan_date = ?",
            (order, pid, hid, plan_date),
        )
    db.commit()
    return jsonify({"ok": True})
