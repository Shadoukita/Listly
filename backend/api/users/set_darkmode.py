from flask import g, jsonify, request

from api.users import bp
from core.security import token_required
from db.session import get_db


@bp.put("/me/darkmode")
@token_required
def set_darkmode():
    value = 1 if (request.get_json(silent=True) or {}).get("darkmode") else 0
    db    = get_db()
    db.execute(
        "UPDATE users SET darkmode = ? WHERE id = ?",
        (value, g.current_user["id"]),
    )
    db.commit()
    return jsonify({"darkmode": bool(value)})
