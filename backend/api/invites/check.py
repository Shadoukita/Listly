import os
import sqlite3

from flask import jsonify

from api.invites import bp
from core.config import DATABASE
from core.invites import VALID_INVITE_SQL


@bp.get("/invite/<token>")
def check_invite(token):
    if not os.path.exists(DATABASE):
        return jsonify({"valid": False}), 404
    db = sqlite3.connect(DATABASE)
    try:
        db.row_factory = sqlite3.Row
        row = db.execute(
            f"SELECT 1 FROM invite_links WHERE token = ? AND {VALID_INVITE_SQL}",
            (token,),
        ).fetchone()
    finally:
        db.close()
    return jsonify({"valid": True}) if row else (jsonify({"valid": False}), 404)
