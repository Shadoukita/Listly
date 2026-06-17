"""
Row-to-dict conversion helpers.

Each function accepts a sqlite3.Row (or plain dict) and returns a plain dict
with all INTEGER-stored boolean columns converted via != 0 — never bool(),
which silently mishandles NULL (bool(None) == False).

See CLAUDE.md → "SQLite boolean rule" for full rationale.
"""


def udict(u) -> dict:
    return {
        "id":                u["id"],
        "username":          u["username"],
        "display_name":      u["display_name"] or u["username"],
        "role":              u["role"],
        "profile_image":     u["profile_image"],
        "darkmode":          u["darkmode"] != 0,
        "last_household_id": u["last_household_id"],
    }


def hh_dict(r) -> dict:
    d = dict(r)
    d["is_public"] = d.get("is_public", 0) != 0
    return d


def item_dict(r) -> dict:
    d = dict(r)
    d["checked"] = d.get("checked", 0) != 0
    return d


def inv_dict(r) -> dict:
    d = dict(r)
    d["used"] = d.get("used", 0) != 0
    return d


def recipe_dict(r) -> dict:
    d = dict(r)
    v = d.get("is_public")
    d["is_public"]     = True if (v is None or v != 0) else False
    d["is_favorited"]  = d.get("is_favorited", 0) != 0
    # calories is nullable INTEGER — keep None as None, coerce stored value to int
    cal = d.get("calories")
    d["calories"]      = int(cal) if cal is not None else None
    d["calories_unit"] = d.get("calories_unit") or "100g"
    return d
