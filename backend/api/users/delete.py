from flask import g, jsonify

from api.users import bp
from core.security import admin_required, token_required
from lang.lang_config import t
from db.session import get_db


@bp.delete("/users/<int:uid>")
@token_required
@admin_required
def delete_user(uid):
    if uid == g.current_user["id"]:
        return jsonify({"error": t("error.cannot_delete_self")}), 400

    db = get_db()
    db.execute("DELETE FROM household_members WHERE user_id = ?", (uid,))
    db.execute("UPDATE households     SET created_by = NULL WHERE created_by = ?", (uid,))
    db.execute("UPDATE shopping_items SET added_by   = NULL WHERE added_by   = ?", (uid,))
    db.execute("UPDATE shopping_items SET checked_by = NULL WHERE checked_by = ?", (uid,))
    db.execute("UPDATE invite_links   SET created_by = NULL WHERE created_by = ?", (uid,))
    db.execute("UPDATE invite_links   SET used_by    = NULL WHERE used_by    = ?", (uid,))
    db.execute("UPDATE recipes        SET created_by = NULL WHERE created_by = ?", (uid,))
    db.execute("DELETE FROM users WHERE id = ?", (uid,))
    db.commit()
    return jsonify({"message": "Deleted"})
