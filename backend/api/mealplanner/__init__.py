from flask import Blueprint

bp = Blueprint("mealplanner", __name__, url_prefix="/api")

from api.mealplanner import list, create, update, delete, bulk_delete, reorder  # noqa: F401, E402
