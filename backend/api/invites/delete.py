from flask import jsonify

from api.invites import bp
from core.security import admin_required, token_required
from lang.lang_config import t
from db.session import get_db


@bp.delete("/invites/<int:iid>")
@token_required
@admin_required
def delete_invite(iid):
    db  = get_db()
    inv = db.execute("SELECT * FROM invite_links WHERE id = ?", (iid,)).fetchone()
    if not inv:
        return jsonify({"error": t("error.not_found")}), 404
    if inv["used"]:
        return jsonify({"error": t("error.invite_already_used")}), 400
    db.execute("DELETE FROM invite_links WHERE id = ?", (iid,))
    db.commit()
    return jsonify({"message": "Deleted"})
