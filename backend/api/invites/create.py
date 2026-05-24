import secrets

from flask import g, jsonify

from api.invites import bp
from core.security import admin_required, token_required
from db.session import get_db


@bp.post("/invites")
@token_required
@admin_required
def create_invite():
    token = secrets.token_urlsafe(24)
    db    = get_db()
    db.execute(
        "INSERT INTO invite_links (token, created_by) VALUES (?, ?)",
        (token, g.current_user["id"]),
    )
    db.commit()
    row = db.execute("SELECT endpoint_url FROM settings WHERE id = 1").fetchone()
    return jsonify({
        "token":        token,
        "endpoint_url": row["endpoint_url"] if row else "",
    }), 201
