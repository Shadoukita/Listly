from flask import g, jsonify

from api.households import bp
from core.security import token_required
from db.session import get_db
from db.models import hh_dict


@bp.get("/households/public")
@token_required
def list_public_households():
    rows = get_db().execute("""
        SELECT h.id, h.name, h.is_public, h.created_at,
               (SELECT COUNT(*) FROM household_members WHERE household_id = h.id) AS member_count
        FROM households h
        WHERE h.is_public = 1
          AND h.id NOT IN (
              SELECT household_id FROM household_members WHERE user_id = ?
          )
        ORDER BY h.created_at DESC
    """, (g.current_user["id"],)).fetchall()
    return jsonify([hh_dict(r) for r in rows])
