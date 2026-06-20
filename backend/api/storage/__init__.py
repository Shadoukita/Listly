from flask import Blueprint

bp = Blueprint("storage", __name__, url_prefix="/api")

from api.storage import (  # noqa: F401, E402
    locations_list,
    location_create,
    location_update,
    location_delete,
    items_list,
    item_create,
    item_update,
    item_delete,
)
