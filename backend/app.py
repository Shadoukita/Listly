"""
Flask application factory.

Usage
-----
Development:  python main.py
WSGI:         gunicorn "main:app"
"""
import os

from flask import Flask, abort, send_from_directory
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from core.config import (
    ASSETS_DIR,
    CORS_ORIGINS,
    DIST_DIR,
    ENABLE_HSTS,
    SECRET_KEY,
    TRUSTED_PROXY_COUNT,
)
from db.session import close_db

# Content-Security-Policy.
#   script-src has no 'unsafe-inline' / 'unsafe-eval' — the Vite build emits no
#   inline scripts (modulePreload.polyfill is disabled in vite.config.js).
#   style-src needs 'unsafe-inline' for Vue's :style bindings.
#   img-src needs blob: for local upload previews and https: for recipe images
#   imported from external sites.
_CSP = "; ".join([
    "default-src 'self'",
    "base-uri 'self'",
    "object-src 'none'",
    "frame-ancestors 'none'",
    "form-action 'self'",
    "script-src 'self'",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' data: https://fonts.gstatic.com",
    "img-src 'self' data: blob: https:",
    "connect-src 'self'",
    "manifest-src 'self'",
    "worker-src 'self'",
])


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY
    # Hard ceiling on request bodies. The upload route caps what it *reads* at
    # 10 MB, but Werkzeug parses the whole multipart body first, so without
    # this an authenticated user could push arbitrarily large bodies at memory
    # and disk. Slightly above the upload limit to leave room for MIME framing.
    app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024

    # Only trust X-Forwarded-* when explicitly told how many proxies sit in
    # front — otherwise a client could spoof its address past the login throttle.
    if TRUSTED_PROXY_COUNT > 0:
        app.wsgi_app = ProxyFix(
            app.wsgi_app, x_for=TRUSTED_PROXY_COUNT, x_proto=TRUSTED_PROXY_COUNT
        )

    # Same-origin by default; opt in via CORS_ORIGINS only if you host the
    # frontend separately. A wildcard would let any site call the API.
    if CORS_ORIGINS:
        CORS(app, origins=CORS_ORIGINS, supports_credentials=False)

    # Register all API blueprints
    from api import register_blueprints
    register_blueprints(app)

    # Close the SQLite connection at the end of every request context
    app.teardown_appcontext(close_db)

    @app.after_request
    def _security_headers(resp):
        resp.headers.setdefault("Content-Security-Policy", _CSP)
        # Stops the browser sniffing an uploaded file into something executable
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("Referrer-Policy", "no-referrer")
        resp.headers.setdefault(
            "Permissions-Policy", "geolocation=(), microphone=(), camera=()"
        )
        if ENABLE_HSTS:
            resp.headers.setdefault(
                "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
            )
        return resp

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
