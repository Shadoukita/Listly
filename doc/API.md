# API Reference

All endpoints are under `/api`. Protected routes need `Authorization: Bearer <token>` in the header.

Errors always come back as `{"error": "<message>"}` with an appropriate status code. Booleans are always proper JSON `true`/`false`, never `0`/`1`.

---

## Auth

### `POST /api/login`
```json
{ "username": "alice", "password": "hunter2", "remember": false }
```
Returns a token and the user object. Set `remember: true` for a 365-day token instead of 1-day.

---

### `GET /api/status`
No auth. Returns whether the app has been set up yet.
```json
{ "setup_done": false, "endpoint_url": "" }
```

---

### `POST /api/setup`
Only works when `setup_done` is false. Creates the first admin account.
```json
{ "username": "admin", "password": "secret", "endpoint_url": "https://list.example.com" }
```

---

## Households

### `GET /api/households`
Your households, with your role and member count for each.

### `POST /api/households`
Create one. Body: `{ "name": "Home" }`

### `PATCH /api/households/<hid>`
Rename or toggle public. Requires household `admin` or `owner`.
Body: `{ "name": "New Name", "is_public": true }` — both optional.

### `DELETE /api/households/<hid>`
Delete it and all its data. Owner only.

### `POST /api/households/join`
Join via invite code. Body: `{ "code": "abc123" }`

### `GET /api/households/public`
List public households you haven't joined yet.

### `POST /api/households/<hid>/join-public`
Join a public household without a code.

### `POST /api/households/<hid>/regenerate-code`
Generate a new invite code. Old one stops working. Requires `admin` or `owner`.

---

## Members

### `GET /api/households/<hid>/members`
Everyone in the household with their roles and join dates.

### `DELETE /api/households/<hid>/members/<uid>`
Remove someone. Requires `admin` or `owner`. You can't remove yourself. You can only remove people with a lower role rank than yours.

### `PUT /api/households/<hid>/members/<uid>/role`
Change someone's role. Owner only. Body: `{ "role": "admin" }`
Valid values: `owner`, `admin`, `member`, `restricted`.

---

## Shopping

### `GET /api/households/<hid>/items`
The shopping list. Unchecked items first, then checked, both sorted by creation date.

```json
[
  {
    "id": 1, "name": "Milk", "quantity": "2L", "category": "Dairy",
    "checked": false, "added_by": 1, "added_by_name": "alice",
    "checked_by": null, "checked_by_name": null, "checked_at": null
  }
]
```

### `POST /api/households/<hid>/items`
Add an item. Only `name` is required; `quantity` and `category` are optional.

### `PATCH /api/items/<iid>/toggle`
Check or uncheck an item. Records who did it and when.

### `DELETE /api/items/<iid>`
Delete an item.

### `DELETE /api/households/<hid>/items/clear-checked`
Remove all checked items at once. Returns `{ "deleted": 5 }`.

---

## Recipes

### `GET /api/households/<hid>/recipes`
Recipes in a specific household.

### `GET /api/recipes/all`
Everything visible to you — your households' recipes plus all public ones, deduplicated.

### `GET /api/recipes/<rid>`
One recipe in full. Accessible if it's public or you're in its household.

### `POST /api/households/<hid>/recipes`
Create a recipe. `restricted` members can't do this.

Fields (all optional except `name`):
```json
{
  "name": "Pasta",
  "description": "...",
  "image_url": "/assets/recipes/uuid.jpg",
  "prep_time": 10, "cook_time": 20, "servings": 4,
  "difficulty": "easy",
  "tags_json": "[\"Italian\"]",
  "ingredients_json": "[[\"200g\", \"pasta\"]]",
  "steps_json": "[\"Boil water\"]",
  "methods_json": "[\"Boiling\"]",
  "calories": 400, "calories_unit": "serving",
  "source_url": "https://...",
  "is_public": false
}
```

### `PATCH /api/recipes/<rid>`
Partial update. Same fields as creation. Household members or global admin only.

### `DELETE /api/recipes/<rid>`
Delete a recipe. Requires global admin or household `admin`/`owner`.

### `DELETE /api/recipes/bulk`
Delete multiple at once. Permissions are checked per recipe.
Body: `{ "ids": [1, 2, 3] }` → returns `{ "deleted": 2, "denied": 1 }`.

### `POST /api/recipes/import`
Scrape a recipe from a URL.
Body: `{ "url": "https://..." }` → returns parsed fields ready to fill the form.

### `POST /api/recipes/<rid>/push-to-list`
Add a recipe's ingredients to your current shopping list.
Returns `{ "added": 6 }`.

---

## Meal Planner

### `GET /api/households/<hid>/meal-plans`
Fetch plans for a date range. Query params:
- `from` — start date `YYYY-MM-DD` (required)
- `to` — end date `YYYY-MM-DD` (required)
- `scope` — `mine` (default) or `household` (all members' plans)

```json
[
  {
    "id": 1, "household_id": 1, "user_id": 2, "user_name": "alice",
    "plan_date": "2026-06-20", "kind": "recipe",
    "recipe_id": 5, "recipe_name": "Pasta", "recipe_description": "...",
    "title": null, "description": null, "notes": "double the garlic",
    "sort_order": 0, "created_at": "2026-06-18T10:00:00"
  }
]
```

### `POST /api/households/<hid>/meal-plans`
Create a plan.

```json
{
  "plan_date": "2026-06-20",
  "kind": "recipe",
  "recipe_id": 5,
  "notes": "optional note"
}
```
For `kind: "manual"` use `title` and `description` instead of `recipe_id`.

### `PATCH /api/meal-plans/<id>`
Partial update. Any field from the create payload is accepted, including `plan_date` (used when dragging a plan to a different day).

### `DELETE /api/meal-plans/<id>`
Delete a single plan.

### `DELETE /api/meal-plans/bulk`
Delete multiple plans. Body: `{ "ids": [1, 2, 3] }` → `{ "deleted": [1, 2, 3] }`.

### `PATCH /api/households/<hid>/meal-plans/reorder`
Reorder plans within a single day. Body: `{ "plan_date": "2026-06-20", "ids": [3, 1, 2] }` — the order of IDs becomes the new `sort_order`.

---

## Storage

### `GET /api/households/<hid>/storage/locations`
All storage locations for the household.

```json
[{ "id": 1, "household_id": 1, "name": "Fridge", "icon": "fridge", "tone": "#9bd9ff" }]
```

### `POST /api/households/<hid>/storage/locations`
Create a location. Requires household `admin` or `owner`.
Body: `{ "name": "Fridge", "icon": "fridge", "tone": "#9bd9ff" }`

### `PATCH /api/storage/locations/<id>`
Update a location's name, icon, or tone. Admin/owner only.

### `DELETE /api/storage/locations/<id>`
Delete a location. Admin/owner only. Cascade-deletes all items in it.

### `GET /api/households/<hid>/storage/items`
All items across all locations for the household.

```json
[
  {
    "id": 1, "household_id": 1, "location_id": 2,
    "name": "Milk", "quantity": 2, "unit": "L",
    "low_threshold": 1, "is_low": false,
    "added_by": 3, "added_by_name": "alice"
  }
]
```

### `POST /api/households/<hid>/storage/items`
Add an item. `name` and `location_id` are required.

```json
{ "name": "Milk", "location_id": 2, "quantity": 2, "unit": "L", "low_threshold": 1 }
```

### `PATCH /api/storage/items/<id>`
Update an item. Accepts any field from creation, including `location_id` (used when dragging an item to a different location section).

### `DELETE /api/storage/items/<id>`
Delete an item.

---

## Users

### `GET /api/me`
Your profile.

### `PUT /api/me/household`
Save your last selected household. Body: `{ "household_id": 2 }`

### `PUT /api/me/darkmode`
Body: `{ "darkmode": true }`

### `PUT /api/me/profile`
Update display name, password, or avatar. Password change needs `current_password`.
```json
{
  "display_name": "Alice",
  "profile_image": "/assets/users/uuid.jpg",
  "new_password": "newpass",
  "current_password": "oldpass"
}
```

### `GET /api/users`
All users on the instance. Global admin only.

### `DELETE /api/users/<uid>`
Delete a user. Global admin only. Can't delete yourself. All their content is preserved — FK references are set to NULL and the UI shows "Deleted User".

---

## Admin

### `GET /api/admin/stats`
Global admin only. Returns `{ "households": 4, "recipes": 12 }`.

---

## Invites

### `POST /api/invites`
Create an invite link. Admin only.

### `GET /api/invites`
All invite links with their usage status. Admin only.

### `DELETE /api/invites/<iid>`
Revoke an invite. Can't revoke one that's already been used.

### `GET /api/invite/<token>`
Check if a token is valid. No auth required. Returns `{ "valid": true }`.

### `POST /api/invite/<token>/register`
Register using an invite. No auth required.
Body: `{ "username": "carol", "password": "pass" }` → returns token + user.

---

## Settings

### `GET /api/settings`
Returns `{ "endpoint_url": "https://list.example.com" }`.

### `PUT /api/settings`
Update the endpoint URL. Admin only.

---

## Modules

### `GET /api/me/modules`
Your module state — global setting, your personal override, and the effective value (both must be true).
```json
{
  "shopping":  { "global": true,  "user": true,  "effective": true },
  "recipes":   { "global": true,  "user": false, "effective": false }
}
```

### `PUT /api/me/modules`
Update your personal module preferences. Body: `{ "shopping": true, "recipes": false }`

### `PUT /api/modules`
Update global module settings. Admin only.

---

## Uploads

### `POST /api/upload`
Upload an image (file or URL). Returns the asset path to store in `image_url`.

File upload:
```
type=recipe   (or "user")
file=<binary>
```

URL download:
```
type=recipe
url=https://example.com/image.jpg
```

Response: `{ "url": "/assets/recipes/<uuid>.jpg" }`

Max 20 MB. Supported formats: JPEG, PNG, WebP, GIF.
