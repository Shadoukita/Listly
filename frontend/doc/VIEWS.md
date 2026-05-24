# Views

Page components in `frontend/src/views/`. All `<script setup>`.

---

## Unauthenticated

### `LoginView.vue` — `/login`

Two tabs: **Login** and **Register**.

Login tab is straightforward — username, password, remember-me checkbox. On success calls `auth.setAuth()` and redirects.

Register tab is invite-only. The invite token can come from the URL (`?invite=<token>`) or be typed in manually. It validates the token first (`GET /api/invite/<token>`), then shows the registration form.

---

### `SetupView.vue` — `/setup`

First-run only. Two steps:
1. Create the admin account
2. Set the public endpoint URL (optional — used for invite links)

Redirects to `/login` if `setup_done` is already true.

---

### `InviteView.vue` — `/invite/:token`

Validates the token from the URL on mount. If it's invalid or already used, redirects to `/login`. Otherwise shows a simple username/password form. On success, sets auth and redirects into the app.

---

## App shell

### `AppLayout.vue`

The authenticated wrapper. Runs on mount:
1. `hh.load()` — fetch household list
2. `hh.restore(user.last_household_id)` — select the last household
3. `auth.fetchModules()` — load module state

Contains the Sidebar, the mobile topbar with the hamburger, and the inner `<router-view :key="hh.current?.id">`. The key is important — it forces a full remount on household switch so all views reload cleanly.

---

## Shopping

### `ShoppingView.vue` — `/shopping`

The shopping list for the active household.

- Add bar at the top — name plus optional quantity and category
- Items rendered as `<ItemRow>` components
- Tap the checkbox to toggle checked state
- Trash icon to delete
- "Clear checked" button at the top right to remove all checked items at once

Data: `GET /api/households/<hid>/items` on mount. Household switch triggers remount, so data reloads automatically.

---

## Recipes

### `RecipesView.vue` — `/recipes`

Recipe browser.

- Search by name
- Toggle between current household only vs. all visible recipes
- `<RecipeCard>` grid
- Bulk select mode → bulk delete (with per-recipe permission check)
- Random recipe button
- FAB to create a new recipe

### `RecipeDetailView.vue` — `/recipes/:id`

Full recipe view:
- Cover image
- Metadata: prep/cook time, servings, difficulty, methods
- Ingredients table
- Step-by-step instructions
- Nutrition (calories + unit)
- Public badge and source URL
- "Add to shopping list" button
- Edit / Delete actions (shown based on your role)

### `RecipeCreateView.vue` — `/recipes/new` and `/recipes/:id/edit`

The recipe form. Works for both create and edit.

Six sections you scroll through:
1. Basics — name, description, difficulty, servings, times
2. Image — file upload or URL; if you imported from URL this auto-fills
3. Ingredients — add/remove/reorder `[amount, item]` pairs
4. Steps — add/remove/reorder instruction steps
5. Methods & Tags — cooking method chips, tag chips
6. Save / publish

Import from URL: paste a link → hits `POST /api/recipes/import` → fills the form. User can edit anything before saving.

---

## User

### `ProfileView.vue` — `/profile`

Avatar upload (or URL), display name, and password change. Password change requires the current password. Calls `auth.updateProfile()`.

### `SettingsView.vue` — `/settings`

- Dark mode toggle
- Language picker (en-US / de-DE) — persisted to localStorage
- Module toggles — enable/disable Shopping and Recipes for yourself

---

## Admin

### `AdminView.vue` — `/admin`

Instance admin panel. Only accessible to global admins.

Four sections:
1. **Stats** — household and recipe counts from `GET /api/admin/stats`
2. **Modules** — global toggles for each module
3. **Users** — table of all users; trash icon deletes with a browser `confirm()` dialog
4. **Invites** — list of invite links, create new, revoke unused

### `HouseholdSettingsView.vue` — `/household/settings`

Settings for the active household. Requires at least `admin` role.

- Rename the household
- Toggle public/private
- Invite code — copy, regenerate
- Member list with role pickers (owner only) and kick buttons
- Kick = remove from household only, no content is deleted, uses a browser `confirm()` dialog
- Delete household (owner only, danger zone at the bottom)
