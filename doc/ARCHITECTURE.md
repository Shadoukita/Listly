# Architecture

## Overview

Everything runs in a single Docker container. Gunicorn handles incoming requests and routes them to either the Flask API or static files. The Vue SPA takes over client-side routing for everything that isn't an API call.

```
Browser
  │
  │  HTTPS
  ▼
┌─────────────────────────────────────────────────────┐
│  Docker container                                   │
│                                                     │
│  Gunicorn (2 workers)                               │
│    │                                                │
│    ├── /api/*  ──► Flask blueprints                 │
│    │                  ├── auth                      │
│    │                  ├── shopping                  │
│    │                  ├── recipes                   │
│    │                  ├── households                │
│    │                  ├── users                     │
│    │                  ├── invites                   │
│    │                  ├── modules                   │
│    │                  ├── settings                  │
│    │                  ├── uploads                   │
│    │                  ├── mealplanner               │
│    │                  └── storage                   │
│    │                       │                        │
│    │                  SQLite (per-request conn)     │
│    │                  /data/database.db             │
│    │                                                │
│    ├── /assets/*  ──► /data/assets/ (static)        │
│    │                                                │
│    └── /*  ──► frontend/dist/index.html             │
│               (Vue Router handles everything else)  │
│                                                     │
│  Volume: /data  (database + uploaded images)        │
└─────────────────────────────────────────────────────┘
```

---

## API requests

1. Client sends `Authorization: Bearer <jwt>`
2. `@token_required` decodes the token and puts the user into `flask.g.current_user`
3. The route handler does its thing against SQLite via `get_db()`
4. `get_db()` opens the connection with `PRAGMA foreign_keys = ON` (enforced for every request)
5. Boolean columns get converted from `INTEGER` to proper Python `bool` via `!= 0` in the `_dict()` helpers
6. Connection closes in the teardown hook

## Frontend routing

All non-API paths serve `frontend/dist/index.html`. Vue Router handles the rest client-side via `createWebHistory`. This means deep links and direct URL navigation work fine — the browser just gets the same HTML and Vue picks up the route.

---

## Database

SQLite, single file. Connection is opened fresh per request and stored in `flask.g` so it stays in scope for the whole request without being passed around everywhere.

A few things worth knowing:
- Foreign keys are **off** by default in SQLite. We turn them on with `PRAGMA foreign_keys = ON` at connect time.
- There's no native boolean type. Everything is stored as `INTEGER` (`1`/`0`) and converted in the `_dict()` helpers using `!= 0` — never `bool()`, because `bool(None)` returns `False` which silently breaks nullable columns.
- Migrations live in `db/migrations.py` and run automatically on startup. They're tracked in a `_migrations` table.

Full schema is in `backend/doc/DATABASE.md`.

---

## Auth

JWT tokens signed with `SECRET_KEY` using HS256. Two lifetimes:
- Normal login → 1 day
- "Stay logged in" → 365 days

Passwords are PBKDF2-SHA256, 100k iterations, random 16-byte salt.

`@token_required` validates the token and puts the user dict into `g.current_user`. `@admin_required` (always stacked after it) checks `g.current_user["role"] == "admin"` for instance-wide admin actions.

---

## Frontend

Single-page app built with Vite + Vue 3 Composition API (`<script setup>`).

```
App.vue
 └── router-view
      ├── LoginView / SetupView / InviteView   (no auth needed)
      └── AppLayout.vue                         (authenticated shell)
           ├── Sidebar.vue
           ├── mobile topbar
           └── router-view  ← keyed by hh.current.id
                ├── ShoppingView
                ├── RecipesView / RecipeDetailView / RecipeCreateView
                ├── MealPlannerView               ← daily / weekly / monthly calendar
                ├── StorageView                   ← location sections + inventory
                ├── ProfileView
                ├── SettingsView
                ├── AdminView
                └── HouseholdSettingsView
```

State is in Pinia stores (`auth`, `household`, `recipes`, `mealplan`, `storage`, `connection`). All API calls go through `stores/api.js` which attaches the JWT and handles offline detection.

The inner `router-view` has `:key="hh.current?.id"` on it — this forces a full remount when you switch households so everything reloads cleanly without needing to watch the household ID in every view.

---

## PWA

Vite PWA plugin + Workbox. Strategy:
- Network-first for `/api/*` (300s max age, 50 entries cached)
- Precache for all built static assets

The app shows cached data when offline and updates silently when a new version is deployed.

---

## Image uploads

Uploaded files are stored in `/data/assets/` (outside the app layer) so they survive redeployments.

- Recipe images → `/data/assets/recipes/<uuid>.<ext>`
- User avatars → `/data/assets/users/<uuid>.<ext>`

Served at `/assets/recipes/<filename>` and `/assets/users/<filename>`.
