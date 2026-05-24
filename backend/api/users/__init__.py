from flask import Blueprint

bp = Blueprint("users", __name__, url_prefix="/api")

from api.users import me, set_household, set_darkmode, update_profile, list, delete, stats  # noqa: F401, E402
