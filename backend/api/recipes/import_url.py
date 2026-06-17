import re
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

# Matches a leading quantity (number + optional unit) at the start of an
# ingredient string.
# Group 1 = full quantity string (e.g. "125g", "1 EL", "1 Pck.", "500 ml")
# Group 2 = ingredient name (everything after the quantity + whitespace)
_QTY_RE = re.compile(
    r'^'
    r'('
        r'[\d½¼¾⅓⅔]+[\d\.,]*'
        r'(?:\s*[-–]\s*[\d]+[\d\.,]*)?'
        r'(?:\s*/\s*[\d]+)?'
        r'(?:\s*'
            r'(?:kg|g|mg|l|L|ml|cl|dl'
            r'|oz|fl\.?\s*oz|lb|lbs'
            r'|EL|el|TL|tl'
            r'|Teelöffel|teelöffel|Esslöffel|esslöffel'
            r'|tbsp|tsp'
            r'|cup|cups'
            r'|Pck\.|Pck|Pckg\.|Pckg|Pkg\.|Pkg'
            r'|Prise|prise'
            r'|Stück|stück|Stk\.?|stk'
            r'|Msp\.?|Messerspitze|messerspitze'
            r'|Bund|bund'
            r'|Dose|dose'
            r'|Glas|glas'
            r'|Flasche|flasche'
            r'|Tüte|tüte'
            r'|Scheibe|scheiben|scheibe'
            r'|Zehe|zehen'
            r'|Blatt|blätter|blatt'
            r'|Stange|stangen'
            r'|Stiel|stiele'
            r'|Zweig|zweige'
            r'|x|X'
            r'|can|cans|piece|pieces'
            r')\.?)?'
    r')'
    r'\s+'
    r'(.+)$',
    re.UNICODE | re.IGNORECASE,
)


def _parse_ingredient(text: str) -> dict:
    """
    Parse a raw ingredient string into {name, quantity}.

    "125g Butter"           → {name: "Butter",       quantity: "125g"}
    "1 Pck. Vanillezucker"  → {name: "Vanillezucker", quantity: "1 Pck."}
    "500 ml Milch"          → {name: "Milch",         quantity: "500 ml"}
    "2 Eier"                → {name: "Eier",          quantity: "2"}
    "Salz nach Geschmack"   → {name: "Salz …",        quantity: ""}
    """
    text = text.strip()
    m = _QTY_RE.match(text)
    if m:
        return {"name": m.group(2).strip(), "quantity": m.group(1).strip()}
    return {"name": text, "quantity": ""}


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

        # All ingredients land in a single unnamed section.
        # The user can split them into sections manually using drag & drop.
        raw_ingredients = _safe(s.ingredients) or []
        items = [_parse_ingredient(i) for i in raw_ingredients if i.strip()]
        ingredient_sections = [{"name": "", "items": items}]

        return jsonify({
            "name":                _safe(s.title),
            "description":         _safe(s.description),
            "image_url":           _safe(s.image),
            "prep_time":           str(prep) if prep else None,
            "cook_time":           str(cook) if cook else None,
            "servings":            _safe(s.yields),
            "ingredient_sections": ingredient_sections,
            "steps":               [ln for ln in (_safe(s.instructions) or "").split("\n") if ln.strip()],
            "tags":                [],
            "source_url":          url,
        })
    except requests.RequestException as e:
        return jsonify({"error": f"Could not fetch URL: {e}"}), 400
    except Exception as e:
        return jsonify({"error": f"Could not scrape: {e}"}), 400
