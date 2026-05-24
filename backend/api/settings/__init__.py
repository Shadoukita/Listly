from flask import Blueprint

bp = Blueprint("settings", __name__, url_prefix="/api")

from api.settings import get, update  # noqa: F401, E402
