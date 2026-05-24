from flask import g, jsonify

from api.users import bp
from core.security import token_required
from db.models import udict


@bp.get("/me")
@token_required
def me():
    return jsonify(udict(g.current_user))
