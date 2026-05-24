# Auth

Stateless JWT auth. No sessions on the server — every request carries a signed token.

---

## Tokens

Signed with `SECRET_KEY` using HS256 (PyJWT). Payload is just `{ "sub": <user_id>, "exp": <timestamp> }`.

| Login type | Lifetime |
|---|---|
| Normal | 1 day |
| "Stay logged in" | 365 days |

If `SECRET_KEY` changes, all tokens become invalid and everyone has to log in again.

```python
from core.security import make_token
token = make_token(user_id, remember=False)
```

---

## Passwords

PBKDF2-SHA256, 100k iterations, random 16-byte salt. Stored as:
```
pbkdf2:sha256:100000$<hex-salt>$<hex-hash>
```

```python
from core.security import hash_pw, verify_pw

stored = hash_pw("hunter2")
ok = verify_pw("hunter2", stored)  # True / False
```

---

## Decorators

### `@token_required`

Validates the `Authorization: Bearer <token>` header, loads the user from the DB, and puts them into `flask.g.current_user`. Returns `401` if anything's wrong.

```python
from core.security import token_required

@bp.get("/protected")
@token_required
def my_view():
    user = g.current_user
```

### `@admin_required`

Checks `g.current_user["role"] == "admin"`. Always goes after `@token_required`. Returns `403` if the user isn't a global admin.

```python
@bp.delete("/admin/only")
@token_required
@admin_required
def admin_action():
    ...
```

---

## Two role systems

These are separate and shouldn't be confused.

**Global role** (`users.role`) — `admin` or `member`. Controls access to the admin panel and instance-wide operations. Checked by `@admin_required`.

**Household role** (`household_members.role`) — scoped per household. Controls what you can do within a specific household.

| Role | Rank | Can do |
|---|---|---|
| `owner` | 4 | everything — rename/delete household, change member roles |
| `admin` | 3 | kick members (lower rank only), edit/delete any recipe |
| `member` | 2 | add/edit recipes, manage shopping list |
| `restricted` | 1 | view only |

Comparisons use the numeric rank, not string equality. You can only act on someone whose rank is strictly below yours.

**Helpers** in `core/utils.py`:

```python
from core.utils import get_member_role, has_access, is_hh_admin, is_hh_owner, ROLE_RANK

role = get_member_role(household_id)   # current user's role, or None
has_access(hid)    # True if they're a member at all
is_hh_admin(hid)   # True if admin or owner
is_hh_owner(hid)   # True if owner
ROLE_RANK["owner"] # 4
```

---

## First-time setup

1. On a fresh install, `settings.setup_done` is `0`
2. `GET /api/status` returns `{ "setup_done": false }` and the frontend redirects to `/setup`
3. `POST /api/setup` creates the admin account and sets `setup_done = 1`
4. After that, `/api/setup` returns `409`

---

## Invite flow

New users can only register if they have an invite link (or it's a fresh setup).

1. Admin calls `POST /api/invites` → gets a signed token
2. Admin shares `<endpoint_url>/invite/<token>`
3. Visitor checks `GET /api/invite/<token>` — no auth needed, just validates it
4. `POST /api/invite/<token>/register` creates the account and marks the invite used
5. Invites are one-time. Once used, they can't be used again and can't be revoked.

---

## Things to watch out for

- Rotate `SECRET_KEY` immediately if it leaks — all tokens invalidate
- You can't revoke a used invite
- Global admin deletion preserves all content — FK references are NULLed and the UI shows "Deleted User"
- Household role checks prevent escalation — you can't give someone a rank equal to or higher than your own
