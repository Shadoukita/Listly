from flask import g, jsonify

from api.modules import bp
from api.modules.helpers import module_response
from core.security import token_required
from db.session import get_db


@bp.get("/me/modules")
@token_required
def get_modules():
    return jsonify(module_response(get_db(), g.current_user["id"]))
