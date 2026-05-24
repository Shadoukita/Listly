from flask import jsonify

from api.invites import bp
from core.security import admin_required, token_required
from db.session import get_db
from db.models import inv_dict


@bp.get("/invites")
@token_required
@admin_required
def list_invites():
    rows = get_db().execute("""
        SELECT il.*, u.username AS used_by_name
        FROM invite_links il
        LEFT JOIN users u ON il.used_by = u.id
        ORDER BY il.created_at DESC
    """).fetchall()
    return jsonify([inv_dict(r) for r in rows])
