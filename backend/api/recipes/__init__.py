from flask import Blueprint

bp = Blueprint("recipes", __name__, url_prefix="/api")

from api.recipes import (  # noqa: F401, E402
    list,
    list_all,
    get,
    create,
    update,
    delete,
    bulk_delete,
    import_url,
    push_to_list,
    favorite,
)
