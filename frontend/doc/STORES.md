# Stores

Pinia stores in `frontend/src/stores/`. All are composable-style (`defineStore` with `setup()`).

---

## `api.js` — fetch helper

Not a Pinia store. Just one function used by everything else:

```js
import { api } from '@/stores/api'

const data = await api(path, method = 'GET', body = null)
```

Automatically attaches the Bearer token and `Accept-Language` header, calls `markOnline()`/`markOffline()` based on the response, and throws on non-2xx with the error message from the response body.

---

## `connection.js` — online/offline state

Also not a Pinia store — just exported refs.

```js
import { serverOnline, setupAllowed, markOnline, markOffline } from '@/stores/connection'
```

| Export | Type | Description |
|---|---|---|
| `serverOnline` | `ref<boolean>` | is the server reachable |
| `setupAllowed` | `ref<boolean>` | true when setup_done is false |
| `markOnline()` | fn | sets online, stops poll, reloads if was offline |
| `markOffline()` | fn | sets offline, starts polling /api/status every 4s |

---

## `auth.js`

```js
import { useAuthStore } from '@/stores/auth'
const auth = useAuthStore()
```

**State / computed**

| Property | Type | Notes |
|---|---|---|
| `token` | `string\|null` | persisted to localStorage |
| `user` | `object\|null` | persisted to localStorage |
| `isLoggedIn` | computed | token is set |
| `isAdmin` | computed | `user.role === 'admin'` |
| `modules` | computed | effective module state (global AND user) |
| `userModules` | computed | per-user preferences |
| `globalModules` | computed | instance-wide settings |

**Actions**

```js
auth.setAuth(token, user)           // set and persist auth
auth.logout()                       // clear everything
await auth.fetchMe()                // GET /me
await auth.fetchModules()           // GET /me/modules
await auth.setModule(id, bool)      // PUT /me/modules
await auth.setGlobalModule(id, bool) // PUT /modules (admin)
await auth.setDarkmode(bool)        // PUT /me/darkmode
await auth.updateProfile(updates)   // PUT /me/profile
```

---

## `household.js`

```js
import { useHouseholdStore } from '@/stores/household'
const hh = useHouseholdStore()
```

**State**

| Property | Type | Notes |
|---|---|---|
| `households` | `array` | all households you're in |
| `current` | `object\|null` | active household |

**Constants**

```js
import { ROLE_RANK } from '@/stores/household'
// { owner: 4, admin: 3, member: 2, restricted: 1 }
```

**Actions**

```js
await hh.load()                         // GET /households
hh.select(household, save = true)        // switch active household
hh.restore(lastHouseholdId)             // auto-select on load

await hh.create(name)
await hh.join(code)
await hh.loadPublic()
await hh.joinPublic(hid)

await hh.updateHousehold(hid, data)     // PATCH
await hh.deleteHousehold(hid)

await hh.removeMember(hid, uid)
await hh.setMemberRole(hid, uid, role)
```

---

## `recipes.js`

```js
import { useRecipesStore } from '@/stores/recipes'
const recipes = useRecipesStore()
```

**State**

| Property | Type | Notes |
|---|---|---|
| `items` | `array` | current household's recipes |
| `allItems` | `array` | all visible recipes (own + public) |
| `current` | `object\|null` | recipe open in detail view |

**Actions**

```js
await recipes.load(householdId)       // GET /households/{hid}/recipes
await recipes.loadAll()               // GET /recipes/all
await recipes.get(id)                 // GET /recipes/{id}

await recipes.create(householdId, recipe)
await recipes.importFromUrl(url)      // POST /recipes/import
await recipes.update(id, patch)
await recipes.remove(id)
await recipes.bulkRemove(ids)         // returns { deleted, denied }
await recipes.pushToList(id)
```

---

## Note on the household key

`AppLayout.vue` passes `:key="hh.current?.id"` to the inner `<router-view>`. This forces a full remount whenever you switch households, so all views reload their data automatically without needing to watch the household ID themselves.
