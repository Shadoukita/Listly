-- ═══════════════════════════════════════════════
--  Einkaufsliste – Datenbank-Schema (SQLite)
-- ═══════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'member',
    display_name TEXT,
    profile_image TEXT,
    darkmode BOOLEAN DEFAULT TRUE,
    last_household_id INTEGER,
    -- Bumped to revoke every JWT issued for this user (see core/security.py)
    token_version INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS households (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    invite_code TEXT UNIQUE NOT NULL,
    is_public BOOLEAN DEFAULT FALSE,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS household_members (
    household_id INTEGER REFERENCES households(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (household_id, user_id)
);

CREATE TABLE IF NOT EXISTS shopping_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    household_id INTEGER REFERENCES households(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    quantity TEXT DEFAULT '1',
    category TEXT DEFAULT 'Sonstiges',
    checked BOOLEAN DEFAULT FALSE,
    added_by INTEGER REFERENCES users(id),
    checked_by INTEGER REFERENCES users(id),
    checked_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS invite_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token TEXT UNIQUE NOT NULL,
    created_by INTEGER REFERENCES users(id),
    used_by INTEGER REFERENCES users(id),
    used BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    setup_done BOOLEAN DEFAULT FALSE,
    endpoint_url TEXT DEFAULT ''
);

INSERT OR IGNORE INTO settings (id) VALUES (1);

CREATE TABLE IF NOT EXISTS user_modules (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    module  TEXT NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (user_id, module)
);

CREATE TABLE IF NOT EXISTS global_modules (
    module  TEXT PRIMARY KEY,
    enabled BOOLEAN DEFAULT TRUE
);
INSERT OR IGNORE INTO global_modules (module, enabled) VALUES ('shopping', TRUE);
INSERT OR IGNORE INTO global_modules (module, enabled) VALUES ('recipes', TRUE);

CREATE INDEX IF NOT EXISTS idx_items_household ON shopping_items(household_id);
CREATE INDEX IF NOT EXISTS idx_items_checked ON shopping_items(household_id, checked);
CREATE INDEX IF NOT EXISTS idx_members_user ON household_members(user_id);
CREATE INDEX IF NOT EXISTS idx_households_invite ON households(invite_code);
CREATE INDEX IF NOT EXISTS idx_invite_token ON invite_links(token);

CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    household_id INTEGER NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    image_url TEXT,
    prep_time TEXT,
    cook_time TEXT,
    servings TEXT,
    difficulty TEXT,
    source_url TEXT,
    tags_json TEXT,
    ingredients_json TEXT NOT NULL DEFAULT '[]',
    steps_json       TEXT NOT NULL DEFAULT '[]',
    methods_json     TEXT,
    calories         INTEGER,
    calories_unit    TEXT DEFAULT '100g',
    is_public        BOOLEAN DEFAULT TRUE,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_recipes_household ON recipes(household_id);

CREATE TABLE IF NOT EXISTS recipe_favorites (
    user_id   INTEGER REFERENCES users(id) ON DELETE CASCADE,
    recipe_id INTEGER REFERENCES recipes(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, recipe_id)
);
CREATE INDEX IF NOT EXISTS idx_favorites_user ON recipe_favorites(user_id);

-- ── Meal planner ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS meal_plans (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    household_id  INTEGER NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    user_id       INTEGER REFERENCES users(id) ON DELETE CASCADE,
    plan_date     TEXT NOT NULL,
    kind          TEXT NOT NULL DEFAULT 'manual',
    recipe_id     INTEGER REFERENCES recipes(id) ON DELETE SET NULL,
    title         TEXT,
    description   TEXT,
    notes         TEXT,
    sort_order    INTEGER DEFAULT 0,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_mealplans_hh_date ON meal_plans(household_id, plan_date);
CREATE INDEX IF NOT EXISTS idx_mealplans_user    ON meal_plans(user_id);

-- ── Storage ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS storage_locations (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    household_id  INTEGER NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    name          TEXT NOT NULL,
    icon          TEXT DEFAULT 'shelf',
    tone          TEXT DEFAULT '#9bd9ff',
    sort_order    INTEGER DEFAULT 0,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_storage_loc_hh ON storage_locations(household_id);

CREATE TABLE IF NOT EXISTS storage_items (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    household_id  INTEGER NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    location_id   INTEGER NOT NULL REFERENCES storage_locations(id) ON DELETE CASCADE,
    name          TEXT NOT NULL,
    quantity      INTEGER NOT NULL DEFAULT 0,
    unit          TEXT DEFAULT '',
    low_threshold INTEGER DEFAULT 0,
    added_by      INTEGER REFERENCES users(id),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_storage_items_loc ON storage_items(location_id);
CREATE INDEX IF NOT EXISTS idx_storage_items_hh  ON storage_items(household_id);

INSERT OR IGNORE INTO global_modules (module, enabled) VALUES ('mealplanner', TRUE);
INSERT OR IGNORE INTO global_modules (module, enabled) VALUES ('storage', TRUE);

-- ── Login throttling ─────────────────────────────────────────────────
-- Failed-login counters, in SQLite rather than process memory so they are
-- shared across Gunicorn workers. See core/ratelimit.py.
CREATE TABLE IF NOT EXISTS login_attempts (
    key          TEXT PRIMARY KEY,
    fails        INTEGER NOT NULL DEFAULT 0,
    window_start REAL    NOT NULL DEFAULT 0,
    locked_until REAL    NOT NULL DEFAULT 0
);
