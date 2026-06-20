# Database

SQLite, single file. Path set by the `DATABASE` env var — defaults to `backend/database.db` locally, `/data/database.db` in Docker.

---

## Connection

```python
from db.session import get_db

db = get_db()
row = db.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
```

`get_db()` opens a connection on first call and caches it in `flask.g` for the rest of the request. `close_db()` is a teardown hook that closes it afterwards. `PRAGMA foreign_keys = ON` is applied at connect time — all FK constraints are enforced.

---

## The boolean thing

SQLite has no boolean type. Everything is stored as `INTEGER` (`1` = true, `0` = false, `NULL` = absent).

When reading into Python, always use `!= 0` — never `bool()`:

```python
d["checked"] = d.get("checked", 0) != 0   # correct
d["checked"] = bool(d.get("checked", 0))  # wrong — bool(None) is False
```

The `_dict()` helpers in `db/models.py` already handle this. When writing, convert explicitly:

```python
db.execute("UPDATE ... SET is_public = ?", (1 if value else 0,))
```

---

## Tables

### `users`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `username` | TEXT UNIQUE NOT NULL | |
| `password_hash` | TEXT NOT NULL | `pbkdf2:sha256:<iters>$<salt>$<hash>` |
| `role` | TEXT DEFAULT `'member'` | `'admin'` or `'member'` — instance-wide |
| `display_name` | TEXT | optional, shown instead of username |
| `profile_image` | TEXT | URL path to avatar |
| `darkmode` | BOOLEAN DEFAULT `1` | |
| `last_household_id` | INTEGER FK→households | last selected household |
| `created_at` | DATETIME | |

---

### `households`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `name` | TEXT NOT NULL | |
| `invite_code` | TEXT UNIQUE NOT NULL | 8-char random code |
| `is_public` | BOOLEAN DEFAULT `0` | joinable without an invite code |
| `created_by` | INTEGER FK→users NULL | NULLed when creator is deleted |
| `created_at` | DATETIME | |

---

### `household_members`

| Column | Type | Notes |
|---|---|---|
| `household_id` | INTEGER FK→households PK | |
| `user_id` | INTEGER FK→users PK | |
| `role` | TEXT NOT NULL | `owner`, `admin`, `member`, `restricted` |
| `joined_at` | DATETIME | |

---

### `shopping_items`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `household_id` | INTEGER FK→households NOT NULL | |
| `name` | TEXT NOT NULL | |
| `quantity` | TEXT | optional |
| `category` | TEXT | optional |
| `checked` | BOOLEAN DEFAULT `0` | |
| `added_by` | INTEGER FK→users NULL | NULLed when user is deleted |
| `checked_by` | INTEGER FK→users NULL | NULLed when user is deleted |
| `checked_at` | DATETIME | |
| `created_at` | DATETIME | |
| `updated_at` | DATETIME | |

---

### `recipes`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `household_id` | INTEGER FK→households NOT NULL | |
| `name` | TEXT NOT NULL | |
| `description` | TEXT | |
| `image_url` | TEXT | |
| `prep_time` | INTEGER | minutes |
| `cook_time` | INTEGER | minutes |
| `servings` | INTEGER | |
| `difficulty` | TEXT | `easy`, `medium`, `hard` |
| `source_url` | TEXT | original URL for imports |
| `tags_json` | TEXT | JSON array of strings |
| `ingredients_json` | TEXT | JSON array of `[amount, name]` pairs |
| `steps_json` | TEXT | JSON array of strings |
| `methods_json` | TEXT | JSON array of strings |
| `calories` | INTEGER NULL | |
| `calories_unit` | TEXT DEFAULT `'serving'` | `'serving'` or `'100g'` |
| `is_public` | BOOLEAN DEFAULT `0` | visible across all households when true |
| `created_by` | INTEGER FK→users NULL | NULLed when user is deleted |
| `created_at` | DATETIME | |
| `updated_at` | DATETIME | |

---

### `invite_links`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `token` | TEXT UNIQUE NOT NULL | signed JWT |
| `created_by` | INTEGER FK→users NULL | |
| `used_by` | INTEGER FK→users NULL | |
| `used` | BOOLEAN DEFAULT `0` | |
| `created_at` | DATETIME | |

---

### `settings`

Singleton row (`id` must equal 1).

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK CHECK `id = 1` | |
| `setup_done` | BOOLEAN DEFAULT `0` | |
| `endpoint_url` | TEXT DEFAULT `''` | base URL for invite links |

---

### `meal_plans`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `household_id` | INTEGER FK→households NOT NULL | |
| `user_id` | INTEGER FK→users NULL | NULLed when user is deleted |
| `plan_date` | TEXT NOT NULL | `YYYY-MM-DD` |
| `kind` | TEXT NOT NULL | `'recipe'` or `'manual'` |
| `recipe_id` | INTEGER FK→recipes NULL | set when `kind = 'recipe'` |
| `title` | TEXT | set when `kind = 'manual'` |
| `description` | TEXT | set when `kind = 'manual'` |
| `notes` | TEXT | optional free-text note on any plan |
| `sort_order` | INTEGER DEFAULT `0` | controls display order within a day |
| `created_at` | DATETIME | |

---

### `storage_locations`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `household_id` | INTEGER FK→households NOT NULL | |
| `name` | TEXT NOT NULL | |
| `icon` | TEXT DEFAULT `'shelf'` | one of: `shelf`, `fridge`, `freezer`, `pantry`, `cooler`, `basket`, `box` |
| `tone` | TEXT DEFAULT `'#9bd9ff'` | hex colour used for the location chip and status dot |
| `created_at` | DATETIME | |

---

### `storage_items`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `household_id` | INTEGER FK→households NOT NULL | |
| `location_id` | INTEGER FK→storage_locations NOT NULL | updated when item is dragged to another location |
| `name` | TEXT NOT NULL | |
| `quantity` | REAL DEFAULT `0` | |
| `unit` | TEXT DEFAULT `''` | e.g. `kg`, `pcs`, `L` |
| `low_threshold` | REAL DEFAULT `0` | alert when `quantity ≤ threshold`; `0` disables the alert |
| `is_low` | BOOLEAN DEFAULT `0` | set by the backend: true when `low_threshold > 0 AND quantity ≤ low_threshold` |
| `added_by` | INTEGER FK→users NULL | NULLed when user is deleted |
| `created_at` | DATETIME | |
| `updated_at` | DATETIME | |

---

### `user_modules` / `global_modules`

`user_modules`: per-user on/off preference per module.
`global_modules`: instance-wide on/off per module.

Effective state = `global AND user`. If the global is off, user preference doesn't matter.

---

### `_migrations`

Tracks which migrations have been applied.

| Column | Type |
|---|---|
| `id` | INTEGER PK |
| `name` | TEXT UNIQUE |
| `applied_at` | DATETIME |

---

## Indexes

```sql
CREATE INDEX idx_items_household   ON shopping_items(household_id);
CREATE INDEX idx_items_checked     ON shopping_items(household_id, checked);
CREATE INDEX idx_members_user      ON household_members(user_id);
CREATE INDEX idx_households_invite ON households(invite_code);
CREATE INDEX idx_invite_token      ON invite_links(token);
CREATE INDEX idx_recipes_household ON recipes(household_id);
```

---

## Migrations

Migrations run automatically on startup via `init_db()` in `db/migrations.py`. Each one is a `(name, sql)` tuple tracked in `_migrations`.

**Applied migrations:**

| Name | What it does |
|---|---|
| `001_add_user_profile_image` | adds `profile_image TEXT` to users |
| `002_add_recipe_calories` | adds `calories INTEGER` to recipes |
| `003_add_recipe_calories_unit` | adds `calories_unit TEXT DEFAULT 'serving'` |
| `004_rename_hh_admin_to_owner` | renames role value `'admin'` → `'owner'` in household_members |
| `005_add_meal_plans` | creates `meal_plans` table |
| `006_add_storage_locations` | creates `storage_locations` table |
| `007_add_storage_items` | creates `storage_items` table |

**To add a migration**, append to the list in `db/migrations.py` — never edit or reorder existing ones:

```python
("005_my_change", "ALTER TABLE recipes ADD COLUMN source_notes TEXT"),
```

It'll run on next startup and get recorded in `_migrations`.

---

## Row → dict helpers (`db/models.py`)

Always use these before passing data to `jsonify()`:

| Helper | Table | Converts |
|---|---|---|
| `udict(row)` | users | `darkmode` |
| `hh_dict(row)` | households | `is_public` |
| `item_dict(row)` | shopping_items | `checked` |
| `inv_dict(row)` | invite_links | `used` |
| `recipe_dict(row)` | recipes | `is_public` |
| `meal_plan_dict(row)` | meal_plans | _(no booleans; joins recipe name/description and user name)_ |
| `storage_location_dict(row)` | storage_locations | _(no booleans)_ |
| `storage_item_dict(row)` | storage_items | `is_low` |
