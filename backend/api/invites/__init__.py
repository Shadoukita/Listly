from flask import Blueprint

bp = Blueprint("invites", __name__, url_prefix="/api")

from api.invites import create, list, delete, check, register  # noqa: F401, E402
