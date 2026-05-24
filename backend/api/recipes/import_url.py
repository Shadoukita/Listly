import requests
from flask import jsonify, request

from api.recipes import bp
from core.security import token_required
from lang.lang_config import t

_SCRAPE_HTML = None
_SCRAPE_ERR  = None
try:
    from recipe_scrapers import scrape_html as _SCRAPE_HTML
except Exception as _e:
    _SCRAPE_ERR = str(_e)


_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Listly-recipe-importer/1.0)"
}


def _safe(fn):
    try:
        val = fn()
        return val if val else None
    except Exception:
        return None


@bp.post("/recipes/import")
@token_required
def import_recipe():
    if _SCRAPE_HTML is None:
        msg = (
            f"recipe-scrapers unavailable: {_SCRAPE_ERR}"
            if _SCRAPE_ERR
            else "recipe-scrapers not installed. Run: pip install recipe-scrapers"
        )
        return jsonify({"error": msg}), 501

    url = request.get_json().get("url", "").strip()
    if not url:
        return jsonify({"error": t("error.url_required")}), 400

    try:
        resp = requests.get(url, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        s = _SCRAPE_HTML(resp.text, org_url=url, wild_mode=True)

        prep = _safe(s.prep_time)
        cook = _safe(s.cook_time)

        return jsonify({
            "name":        _safe(s.title),
            "description": _safe(s.description),
            "image_url":   _safe(s.image),
            "prep_time":   str(prep) if prep else None,
            "cook_time":   str(cook) if cook else None,
            "servings":    _safe(s.yields),
            "ingredients": [{"name": i, "quantity": ""} for i in (_safe(s.ingredients) or [])],
            "steps":       [ln for ln in (_safe(s.instructions) or "").split("\n") if ln.strip()],
            "tags":        [],
            "source_url":  url,
        })
    except requests.RequestException as e:
        return jsonify({"error": f"Could not fetch URL: {e}"}), 400
    except Exception as e:
        return jsonify({"error": f"Could not scrape: {e}"}), 400
