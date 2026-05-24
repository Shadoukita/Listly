from flask import g, jsonify, request

from api.modules import bp
from api.modules.helpers import module_response
from core.config import MODULES
from core.security import admin_required, token_required
from db.session import get_db


@bp.put("/modules")
@token_required
@admin_required
def update_global_modules():
    d  = request.get_json()
    db = get_db()
    for m in MODULES:
        if m in d:
            db.execute(
                "INSERT INTO global_modules (module, enabled) VALUES (?, ?) "
                "ON CONFLICT(module) DO UPDATE SET enabled = excluded.enabled",
                (m, 1 if d[m] else 0),
            )
    db.commit()
    return jsonify(module_response(db, g.current_user["id"]))
