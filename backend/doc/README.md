# Backend

Flask API + SQLite. Also serves the built Vue SPA for all non-API routes.

---

## Layout

```
backend/
├── api/                  # route blueprints, one directory per feature
│   ├── auth/
│   ├── shopping/
│   ├── recipes/
│   ├── households/
│   ├── users/
│   ├── invites/
│   ├── modules/
│   ├── settings/
│   └── uploads/
│
├── core/
│   ├── config.py         # reads env vars
│   ├── security.py       # JWT, password hashing, @token_required, @admin_required
│   └── utils.py          # household access helpers, ROLE_RANK
│
├── db/
│   ├── session.py        # per-request SQLite connection
│   ├── models.py         # row → dict helpers (handles boolean conversion)
│   ├── migrations.py     # migration runner + list of migrations
│   └── schema.sql        # base schema DDL
│
├── lang/
│   ├── lang_config.py    # t() — picks locale from Accept-Language header
│   └── locales/
│       ├── en_US.json
│       └── de_DE.json
│
├── assets/               # uploaded images at runtime (not committed)
├── app.py                # create_app() factory
└── main.py               # Gunicorn entry point
```

---

## How a request flows through

```
HTTP request
  │
  ├─ /api/*
  │    ├─ @token_required  — decodes JWT, sets g.current_user
  │    ├─ @admin_required  — checks role == "admin" (when needed)
  │    └─ route handler
  │         └─ get_db() → SQLite with PRAGMA foreign_keys = ON
  │
  ├─ /assets/*   → static file from ASSETS_DIR
  └─ /*          → frontend/dist/index.html
```

`create_app()` in `app.py` wires all of this together: loads config, runs migrations, registers blueprints, sets up the static routes, and registers `close_db` as a teardown hook.

---

## Config

All config comes from environment variables (`core/config.py`):

| Variable | Default | Notes |
|---|---|---|
| `SECRET_KEY` | **required** | JWT signing secret |
| `DATABASE` | `backend/database.db` | SQLite file |
| `DIST_DIR` | `../frontend/dist` | Built Vue app |
| `ASSETS_DIR` | `backend/assets` | Image upload directory |
| `PORT` | `5000` | Gunicorn port |

---

## Auth decorators

- `@token_required` — validates the Bearer token, puts the user dict into `g.current_user`
- `@admin_required` — checks `g.current_user["role"] == "admin"` for instance-wide admin actions, always stacked after `@token_required`

Household-level access uses helper functions from `core/utils.py` instead of decorators — see `backend/doc/AUTH.md`.

---

## Database

See `backend/doc/DATABASE.md` for the full schema and migration guide.

Quick notes:
- `get_db()` opens or returns the per-request connection
- `close_db()` is a teardown hook, runs after every request
- Booleans are stored as `INTEGER` — always convert with `!= 0` in `_dict()` helpers, never `bool()`

---

## i18n

The backend selects a locale from the `Accept-Language` header:

```python
from lang.lang_config import t
t("error.not_found")   # "Not found" or "Nicht gefunden"
```

Available locales: `en_US` (default) and `de_DE`. Strings live in `lang/locales/<locale>.json`.

---

## Errors

All error responses look like:

```json
{ "error": "<localised message>" }
```

Status codes used: `400` validation, `401` auth, `403` permission, `404` not found, `409` conflict.

---

## Adding a new route

1. Create a directory under `api/` with an `__init__.py` that defines a `Blueprint`
2. Add one file per endpoint (e.g. `list.py`, `create.py`, `delete.py`)
3. Import your route files in the blueprint `__init__.py`
4. Register the blueprint in `app.py`

Look at `api/shopping/` for a straightforward example.
