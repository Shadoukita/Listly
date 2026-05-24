"""
Flask application factory.

Usage
-----
Development:  python main.py
WSGI:         gunicorn "main:app"
"""
import os

import os

from flask import Flask, abort, send_from_directory
from flask_cors import CORS

from core.config import ASSETS_DIR, DIST_DIR, SECRET_KEY
from db.session import close_db


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY

    CORS(app)

    # Register all API blueprints
    from api import register_blueprints
    register_blueprints(app)

    # Close the SQLite connection at the end of every request context
    app.teardown_appcontext(close_db)

    # ── Static routes ─────────────────────────────────────────────────────────

    _ASSET_FOLDERS = {"recipes", "users"}

    @app.route("/assets/<string:folder>/<string:filename>")
    def serve_asset(folder, filename):
        if folder not in _ASSET_FOLDERS:
            abort(404)
        return send_from_directory(os.path.join(ASSETS_DIR, folder), filename)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        if path and os.path.exists(os.path.join(DIST_DIR, path)):
            return send_from_directory(DIST_DIR, path)
        index = os.path.join(DIST_DIR, "index.html")
        if os.path.exists(index):
            return send_from_directory(DIST_DIR, "index.html")
        return (
            "<h3>Frontend not built. "
            "<code>cd frontend && npm install && npm run build</code></h3>",
            404,
        )

    return app
