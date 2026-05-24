from flask import Blueprint

bp = Blueprint("shopping", __name__, url_prefix="/api")

from api.shopping import list, add, toggle, delete, clear_checked  # noqa: F401, E402
