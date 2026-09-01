import secrets

from flask import g, jsonify

from api.invites import bp
from core.security import admin_required, token_required
from core.invites import INVITE_TTL_DAYS
from db.session import get_db


@bp.post("/invites")
@token_required
@admin_required
def create_invite():
    token = secrets.token_urlsafe(24)
    db    = get_db()
    # Invites are single-use *and* time-limited — an unused link left in a chat
    # log should not stay redeemable forever.
    db.execute(
        "INSERT INTO invite_links (token, created_by, expires_at) "
        f"VALUES (?, ?, datetime('now', '+{INVITE_TTL_DAYS} days'))",
        (token, g.current_user["id"]),
    )
    db.commit()
    row = db.execute("SELECT endpoint_url FROM settings WHERE id = 1").fetchone()
    return jsonify({
        "token":        token,
        "endpoint_url": row["endpoint_url"] if row else "",
    }), 201
