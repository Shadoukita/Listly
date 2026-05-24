from flask import jsonify

from api.settings import bp
from core.security import token_required
from db.session import get_db


@bp.get("/settings")
@token_required
def get_settings():
    row = get_db().execute(
        "SELECT endpoint_url FROM settings WHERE id = 1"
    ).fetchone()
    return jsonify({"endpoint_url": row["endpoint_url"] if row else ""})
