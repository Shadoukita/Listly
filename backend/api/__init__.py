"""
Blueprint registry.

To add a new resource:
  1. Create api/<resource>/ with __init__.py (defines bp) and one file per operation.
  2. Import the blueprint below and add it to register_blueprints().
"""
from api.auth        import bp as auth_bp
from api.users       import bp as users_bp
from api.households  import bp as households_bp
from api.shopping    import bp as shopping_bp
from api.recipes     import bp as recipes_bp
from api.invites     import bp as invites_bp
from api.modules     import bp as modules_bp
from api.settings    import bp as settings_bp
from api.uploads     import bp as uploads_bp
from api.mealplanner import bp as mealplanner_bp
from api.storage     import bp as storage_bp


def register_blueprints(app):
    for blueprint in (
        auth_bp,
        users_bp,
        households_bp,
        shopping_bp,
        recipes_bp,
        invites_bp,
        modules_bp,
        settings_bp,
        uploads_bp,
        mealplanner_bp,
        storage_bp,
    ):
        app.register_blueprint(blueprint)
