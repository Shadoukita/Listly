from flask import jsonify

from api.users import bp
from core.security import admin_required, token_required
from db.session import get_db


@bp.get("/admin/stats")
@token_required
@admin_required
def admin_stats():
    db = get_db()
    households = db.execute("SELECT COUNT(*) FROM households").fetchone()[0]
    recipes    = db.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
    return jsonify({"households": households, "recipes": recipes})
