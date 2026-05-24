from flask import Blueprint

bp = Blueprint("modules", __name__, url_prefix="/api")

from api.modules import get, update_user, update_global  # noqa: F401, E402
