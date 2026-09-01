import os
import sqlite3

from flask import jsonify

from api.auth import bp
from core.config import DATABASE


@bp.get("/status")
def status():
    if not os.path.exists(DATABASE):
        return jsonify({"setup_done": False})
    db = sqlite3.connect(DATABASE)
    try:
        db.row_factory = sqlite3.Row
        row = db.execute(
            "SELECT setup_done, endpoint_url FROM settings WHERE id = 1"
        ).fetchone()
    finally:
        db.close()
    return jsonify({
        "setup_done":   bool(row and row["setup_done"]),
        "endpoint_url": row["endpoint_url"] if row else "",
    })
