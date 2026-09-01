from flask import g, jsonify, request

from api.modules import bp
from api.modules.helpers import module_response
from core.config import MODULES
from core.security import token_required
from db.session import get_db


@bp.put("/me/modules")
@token_required
def update_user_modules():
    d  = (request.get_json(silent=True) or {})
    db = get_db()
    for m in MODULES:
        if m in d:
            db.execute(
                "INSERT INTO user_modules (user_id, module, enabled) VALUES (?, ?, ?) "
                "ON CONFLICT(user_id, module) DO UPDATE SET enabled = excluded.enabled",
                (g.current_user["id"], m, 1 if d[m] else 0),
            )
    db.commit()
    return jsonify(module_response(db, g.current_user["id"]))
