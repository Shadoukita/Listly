# Frontend

Vue 3 SPA built with Vite. State in Pinia, routing via Vue Router, translations via Vue i18n.

---

## Layout

```
frontend/src/
├── views/           # page components (one per route)
├── components/      # shared UI components
├── stores/          # Pinia stores + api.js helper
├── plugins/         # Vue plugin setup (i18n)
├── lang/
│   ├── en-US.json
│   └── de-DE.json
├── assets/
│   └── tokens.css   # CSS custom properties (design tokens)
├── router.js
├── main.js
└── App.vue
```

---

## Routing

Uses `createWebHistory` — Flask serves `index.html` for everything that isn't `/api/*`, so deep links and refreshes work fine.

**Unauthenticated routes**

| Path | View |
|---|---|
| `/login` | login + invite-based register |
| `/setup` | first-run admin setup |
| `/invite/:token` | register via invite link |

**Authenticated routes** (inside `AppLayout`)

| Path | View |
|---|---|
| `/shopping` | shopping list |
| `/recipes` | recipe browser |
| `/recipes/new` | create a recipe |
| `/recipes/:id` | recipe detail |
| `/recipes/:id/edit` | edit a recipe |
| `/profile` | user profile |
| `/settings` | user preferences |
| `/admin` | instance admin panel |
| `/household/settings` | household settings |

Guards redirect unauthenticated users to `/login` and logged-in users away from it.

---

## State

All global state is in Pinia stores under `stores/`. Details in `frontend/doc/STORES.md`.

| File | What it holds |
|---|---|
| `auth.js` | current user, JWT token, module state |
| `household.js` | household list, active household |
| `recipes.js` | recipe lists, CRUD |
| `connection.js` | server online/offline |
| `api.js` | `api()` fetch helper (not a store) |

---

## API calls

Everything goes through `api()` in `stores/api.js`:

```js
import { api } from '@/stores/api'

const items = await api('/households/1/items')
const item  = await api('/households/1/items', 'POST', { name: 'Milk' })
await api('/items/5', 'DELETE')
```

It handles auth headers, locale headers, online/offline tracking, and throws on non-2xx responses.

---

## i18n

Locale is saved to `localStorage` and persists across logouts. On startup it falls back to the browser's language if no preference is saved.

```vue
<script setup>
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
</script>

<template>
  <p>{{ t('shopping.emptyState') }}</p>
  <p>{{ t('household.settings.kickConfirm', { name: member.username }) }}</p>
</template>
```

Named interpolation uses `{placeholder}` in the JSON files. Supported: `en-US`, `de-DE`.

**Never hardcode user-facing strings.** There's no build error if you do — they just silently stay in English forever.

---

## Design

### Tokens

CSS custom properties in `assets/tokens.css`:

```
--color-bg, --color-surface, --color-border
--color-text, --color-text-muted
--color-accent, --color-danger
--radius-*, --space-*
```

Dark only. No light mode.

### Fonts

Geist (sans) and Geist Mono — loaded from Google Fonts.

### Icons

All icons are inline SVG paths defined in `components/icons.js`. No icon library. To add one, export a new constant from that file and use it with `<AppIcon :icon="MyIcon" />`.

---

## PWA

Vite PWA plugin + Workbox:
- Network-first for `/api/*` (300s max, 50 entries)
- Precache for all static assets

Works offline with cached data. Updates silently in the background when a new version is deployed.

---

## Further reading

- `frontend/doc/VIEWS.md` — what each view does
- `frontend/doc/STORES.md` — store API reference
- `frontend/doc/COMPONENTS.md` — component props and usage
