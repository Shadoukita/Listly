from flask import jsonify

from api.users import bp
from core.security import admin_required, token_required
from db.session import get_db


@bp.get("/users")
@token_required
@admin_required
def list_users():
    rows = get_db().execute(
        "SELECT id, username, COALESCE(display_name, username) AS display_name, "
        "role, profile_image, darkmode, created_at FROM users ORDER BY created_at"
    ).fetchall()
    return jsonify([{**dict(r), "darkmode": r["darkmode"] != 0} for r in rows])
