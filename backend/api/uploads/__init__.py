from flask import Blueprint

bp = Blueprint("uploads", __name__, url_prefix="/api")

from api.uploads import upload  # noqa: F401, E402
