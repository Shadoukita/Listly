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
