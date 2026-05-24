"""
Shared helpers for building the module-state response.
Imported by get.py, update_user.py, and update_global.py.
"""
from core.config import MODULES
from db.session import get_db


def global_mods(db) -> dict:
    rows   = db.execute("SELECT module, enabled FROM global_modules").fetchall()
    result = {m: True for m in MODULES}
    for r in rows:
        if r["module"] in MODULES:
            result[r["module"]] = r["enabled"] != 0
    return result


def user_mods(db, user_id: int) -> dict:
    rows   = db.execute(
        "SELECT module, enabled FROM user_modules WHERE user_id = ?", (user_id,)
    ).fetchall()
    result = {m: True for m in MODULES}
    for r in rows:
        if r["module"] in MODULES:
            result[r["module"]] = r["enabled"] != 0
    return result


def module_response(db, user_id: int) -> dict:
    gm = global_mods(db)
    um = user_mods(db, user_id)
    return {
        m: {"global": gm[m], "user": um[m], "effective": gm[m] and um[m]}
        for m in MODULES
    }
