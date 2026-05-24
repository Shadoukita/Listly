"""
Translation loader for Listly backend.

Lang files live in lang/locales/<locale>.json — one file per language.
To add a new language:
  1. Create lang/locales/fr_FR.json with the same keys as en_US.json
  2. Add  "fr": "fr_FR"  to _LOCALE_MAP below

Nothing else needs to change. The loader caches each file on first use.
"""
import json
import os
from functools import lru_cache

from flask import request

# Maps the two-letter prefix from the Accept-Language header to a locale file.
_LOCALE_MAP: dict[str, str] = {
    "en": "en_US",
    "de": "de_DE",
}

_FALLBACK  = "en_US"
_LOCALES_DIR = os.path.join(os.path.dirname(__file__), "locales")


@lru_cache(maxsize=None)
def _load(locale: str) -> dict[str, str]:
    """Read and cache lang/locales/<locale>.json. Returns {} if the file is missing."""
    path = os.path.join(_LOCALES_DIR, f"{locale}.json")
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {}


def _resolve_locale() -> str:
    """Pick the best matching locale from the incoming Accept-Language header."""
    header = request.headers.get("Accept-Language", "")
    for tag in header.replace(",", " ").split():
        prefix = tag.split("-")[0].split(";")[0].lower()
        if prefix in _LOCALE_MAP:
            return _LOCALE_MAP[prefix]
    return _FALLBACK


def t(key: str) -> str:
    """Return the translated string for *key* in the request's locale."""
    locale = _resolve_locale()
    return (
        _load(locale).get(key)
        or _load(_FALLBACK).get(key)
        or key
    )
