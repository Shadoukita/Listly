# Listly — Build Progress

## Frontend

| # | Step | Status |
|---|------|--------|
| 1 | Read existing code + design handoff, confirm understanding | ✅ Done |
| 2 | Read design handoff (`README.md`, `web.jsx`, assets) | ✅ Done |
| 3 | Scaffold frontend (Vite + Vue 3 + Pinia + Router + i18n + PWA) | ✅ Done |
| 4 | Design system — `tokens.css`, `base.css`, Geist font | ✅ Done |
| 5 | Shared components (Logo, Sidebar, Field, Button, Pill, Avatar, Chip, Toggle, SectionHeader, ImageSlot, RecipeCard, ToggleRow) | ✅ Done |
| 6 | Stores (api, auth, household, recipes) | ✅ Done |
| 7 | Auth screens: Setup → Login → InviteView | ✅ Done |
| 8 | App shell + Shopping view (polling, sort/filter, qty parse) | ✅ Done |
| 9 | Profile + Settings + Admin views | ✅ Done |
| 10 | Household settings view | ✅ Done |
| 11 | Recipes library view | ✅ Done |
| 12 | Recipe detail view | ✅ Done |
| 13 | Recipe create/edit view | ✅ Done |
| 14 | PWA config (`vite-plugin-pwa`, service worker, manifest) | ✅ Done |
| 15 | Full i18n — all strings moved to `lang/en-US.json` + `lang/de-DE.json` | ✅ Done |
| 16 | Role system UI (owner/admin/member/restricted, role picker, conditional sections) | ✅ Done |
| 17 | Language persists across logout | ✅ Done |
| 18 | Household switch re-mounts active view (`:key` on `<router-view>`) | ✅ Done |
| 19 | Old `frontend/` removed, `frontend-new/` renamed to `frontend/` | ✅ Done |
| 20 | Mobile sidebar fix — inner panel gets `z-index: 1` so the overlay doesn't eat clicks | ✅ Done |
| 21 | Meal Planner module — daily/weekly/monthly calendar, recipe + manual plans, drag-and-drop reorder, multi-select delete, mine/household scope | ✅ Done |
| 22 | Storage module — location management with icons + colours, stock tracking, low-stock threshold + banner, push to shopping list | ✅ Done |
| 23 | MODULES extended with `icon` field — Sidebar, Settings and Admin icon lookups are now driven by module data instead of hardcoded conditionals | ✅ Done |
| 24 | PlanCard component — compact + full modes, tone rail from recipe_id, long-press multi-select, drag handles | ✅ Done |
| 25 | Meal Planner UX pass — cross-day drag & drop (move plans between days), delete button on detail modal, click anywhere on a day column to select it, today marker reduced to number-only highlight, drag-over dashed outline on target day | ✅ Done |
| 26 | Storage drag & drop — drag items between location sections, drag-over dashed accent outline on the target location, grab cursor on draggable rows | ✅ Done |

---

## Backend

| # | Step | Status |
|---|------|--------|
| 1 | Recipe endpoints (CRUD + import + push-to-list + upload) | ✅ Done |
| 2 | Modular API structure (`api/`, `core/`, `db/`, `lang/`) | ✅ Done |
| 3 | Backend i18n (`lang_config.py` + locale files) | ✅ Done |
| 4 | `.env` replaces `secret_key.txt` | ✅ Done |
| 5 | SQLite migrations system — append-only | ✅ Done |
| 6 | Role system — owner / admin / member / restricted | ✅ Done |
| 7 | `core/utils.py` — role helpers and `ROLE_RANK` | ✅ Done |
| 8 | Public recipe visibility across households | ✅ Done |
| 9 | `set_member_role` endpoint | ✅ Done |
| 10 | Recipe import fixed for `recipe-scrapers` 15.x | ✅ Done |
| 11 | User delete FK fix — NULL-out all FK references before deleting the row | ✅ Done |
| 12 | "Deleted User" attribution in shopping and recipe queries | ✅ Done |
| 13 | Household remove-member only removes the membership row, content stays | ✅ Done |
| 14 | Meal planner API blueprint — list, create, update, delete, bulk-delete, reorder endpoints | ✅ Done |
| 15 | Storage API blueprint — location CRUD (admin-gated) + item CRUD (member+) | ✅ Done |
| 16 | `meal_plans`, `storage_locations`, `storage_items` tables added to schema.sql | ✅ Done |
| 17 | `meal_plan_dict`, `storage_location_dict`, `storage_item_dict` helpers added to db/models.py | ✅ Done |
| 18 | `is_low` fix — only flags items low when `low_threshold > 0`, so default items don't show false alerts | ✅ Done |

---

## Docker

| # | Step | Status |
|---|------|--------|
| 1 | Multi-stage Dockerfile (Node build → Python serve) | ✅ Done |
| 2 | `docker-compose.yml` with persistent `/data` volume | ✅ Done |
| 3 | Configurable port via `PORT` + `HOST_PORT` | ✅ Done |
| 4 | `.env` and `assets/` excluded via `.dockerignore` | ✅ Done |
| 5 | Uploaded assets go to `/data/assets/` volume | ✅ Done |
| 6 | Gunicorn entry point fixed to `main:app` | ✅ Done |
| 7 | Published to Docker Hub as `shadoukita/listly:1.0` | ✅ Done |

---

## Documentation

| # | Step | Status |
|---|------|--------|
| 1 | `doc/README.md` | ✅ Done |
| 2 | `doc/ARCHITECTURE.md` | ✅ Done |
| 3 | `doc/DEPLOYMENT.md` | ✅ Done |
| 4 | `doc/API.md` | ✅ Done |
| 5 | `backend/doc/README.md` | ✅ Done |
| 6 | `backend/doc/DATABASE.md` | ✅ Done |
| 7 | `backend/doc/AUTH.md` | ✅ Done |
| 8 | `frontend/doc/README.md` | ✅ Done |
| 9 | `frontend/doc/STORES.md` | ✅ Done |
| 10 | `frontend/doc/COMPONENTS.md` | ✅ Done |
| 11 | `frontend/doc/VIEWS.md` | ✅ Done |

---

## Design decisions worth remembering

- Dark-only theme, no light mode planned
- All icons are inline SVG paths in `src/components/icons.js` — no icon library
- Sidebar is 272px, slides in from the left on mobile
- Household settings is a full route, not a modal
- Quantity pill appears in the add-bar while typing (`3x Milch` → `QTY 3`)
- Avatar color is derived from `user.id` across a 6-color palette
- Role ranks are numeric: owner=4, admin=3, member=2, restricted=1 — rank comparisons are used everywhere instead of string checks
- `recipe-scrapers` v15+ uses `scrape_html` — we fetch the HTML ourselves with `requests` and a spoofed User-Agent
- `app.py` is a factory (`create_app()`), so the Gunicorn entry point is `main:app` not `app:app`
- Deleting a user NULLs all FK references and keeps content; the UI shows "Deleted User" via COALESCE
- Kicking a member only removes the `household_members` row — all their recipes and shopping items stay

---

## i18n rule — never hardcode strings

Every user-facing string goes through vue-i18n. No exceptions.

```vue
<!-- template -->
{{ $t('some.key') }}

<!-- script -->
const { t } = useI18n()
const msg = t('some.key')
```

Add new keys to both files at the same time:
- `frontend/src/lang/en-US.json`
- `frontend/src/lang/de-DE.json`

Backend strings go in:
- `backend/lang/locales/en_US.json`
- `backend/lang/locales/de_DE.json`

Used via `from lang.lang_config import t`. Hardcoded strings don't throw errors, they just silently stay in English forever.
