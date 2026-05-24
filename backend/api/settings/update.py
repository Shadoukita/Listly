from flask import jsonify, request

from api.settings import bp
from core.security import admin_required, token_required
from db.session import get_db


@bp.put("/settings")
@token_required
@admin_required
def update_settings():
    endpoint = request.get_json().get("endpoint_url", "").strip().rstrip("/")
    db       = get_db()
    db.execute("UPDATE settings SET endpoint_url = ? WHERE id = 1", (endpoint,))
    db.commit()
    return jsonify({"endpoint_url": endpoint})
