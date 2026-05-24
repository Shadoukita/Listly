import os
import sqlite3

from flask import jsonify

from api.invites import bp
from core.config import DATABASE


@bp.get("/invite/<token>")
def check_invite(token):
    if not os.path.exists(DATABASE):
        return jsonify({"valid": False}), 404
    db  = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    row = db.execute(
        "SELECT 1 FROM invite_links WHERE token = ? AND used = 0", (token,)
    ).fetchone()
    db.close()
    return jsonify({"valid": True}) if row else (jsonify({"valid": False}), 404)
