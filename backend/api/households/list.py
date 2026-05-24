from flask import g, jsonify

from api.households import bp
from core.security import token_required
from db.session import get_db
from db.models import hh_dict


@bp.get("/households")
@token_required
def list_households():
    rows = get_db().execute("""
        SELECT h.*, hm.role,
               (SELECT COUNT(*) FROM household_members WHERE household_id = h.id) AS member_count
        FROM households h
        JOIN household_members hm ON h.id = hm.household_id
        WHERE hm.user_id = ?
        ORDER BY h.created_at DESC
    """, (g.current_user["id"],)).fetchall()
    return jsonify([hh_dict(r) for r in rows])
