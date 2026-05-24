# Components

Shared UI components in `frontend/src/components/`. All `<script setup>`.

---

## Layout

### `AuthShell.vue`
Full-screen centred container for the login, setup, and invite pages. Just wrap your form in it.

### `Sidebar.vue`
Main nav. Module links, admin link (admins only), household switcher, user menu. On mobile it slides in from the left — the inner panel has `position: relative; z-index: 1` so the backdrop overlay doesn't eat your clicks. No props; reads from `useAuthStore()` and `useHouseholdStore()`.

---

## Typography & branding

### `Logo.vue`
The Listly logo mark + wordmark.

| Prop | Default | |
|---|---|---|
| `markSize` | `32` | SVG size in px |
| `textSize` | `20` | font size in px |

### `Pill.vue`
Small inline badge. Slot: text content.

| Prop | Default | Options |
|---|---|---|
| `tone` | `'neutral'` | `'amber'`, `'accent'`, `'neutral'` |

### `Chip.vue`
Compact tag for lists (methods, tags, categories). Slot: text content.

---

## Forms

### `Field.vue`
Labelled input with error state.

| Prop | Default | |
|---|---|---|
| `label` | `''` | |
| `modelValue` | `''` | v-model |
| `placeholder` | `''` | |
| `type` | `'text'` | |
| `error` | `''` | shown below the field when set |

Has a `trailing` slot for appending something inside the input (e.g. a password visibility toggle).

```vue
<Field v-model="username" label="Username" :error="errors.username" />
```

### `AppButton.vue`
The standard button.

| Prop | Default | Options |
|---|---|---|
| `variant` | `'primary'` | `'primary'`, `'outline'`, `'ghost'`, `'danger'` |
| `size` | `'md'` | `'sm'`, `'md'` |
| `full` | `false` | full-width block |
| `disabled` | `false` | |
| `loading` | `false` | shows spinner, disables interaction |

```vue
<AppButton variant="danger" size="sm" @click="deleteItem">Delete</AppButton>
```

### `ToggleSwitch.vue`
On/off toggle. v-model: `boolean`.

### `ToggleRow.vue`
A row with a label and hint on the left, toggle on the right.

| Prop | |
|---|---|
| `label` | row label |
| `hint` | secondary text |
| `modelValue` | v-model boolean |

---

## Avatars & images

### `Avatar.vue`
Circular avatar. Shows an image if `src` is set, otherwise shows the first character of `name`.

| Prop | Default | |
|---|---|---|
| `src` | `null` | image URL |
| `name` | `''` | fallback initial |
| `size` | `40` | diameter in px |
| `radius` | `'50%'` | CSS border-radius |

### `ImageSlot.vue`
Image with a placeholder shown when `src` is null/empty.

| Prop | |
|---|---|
| `src` | image URL |
| `alt` | alt text |

---

## Content rows

### `ItemRow.vue`
A shopping list item — checkbox, name, optional quantity/category, attribution (who added/checked it), timestamp.

| Prop | |
|---|---|
| `item` | item object from the API |

Emits: `toggle`, `delete`

### `RecipeCard.vue`
Recipe grid card — cover image (or placeholder), name, difficulty, servings, public badge.

| Prop | |
|---|---|
| `recipe` | recipe object |
| `selected` | whether it's selected in bulk mode |

Emits: `click`, `select`

---

## Misc

### `SectionHeader.vue`
Section title. Slot: text content.

### `AppIcon.vue`
Renders an SVG icon from `components/icons.js`.

| Prop | Default | |
|---|---|---|
| `icon` | required | icon object from `icons.js` |
| `size` | `20` | width/height in px |
| `strokeWidth` | `1.5` | SVG stroke width |

```vue
<script setup>
import AppIcon from '@/components/AppIcon.vue'
import { IconTrash } from '@/components/icons.js'
</script>
<template>
  <AppIcon :icon="IconTrash" :size="16" />
</template>
```

---

## Adding icons

Icons are plain objects with `viewBox` and `paths` (array of SVG `d` strings):

```js
export const IconTrash = { viewBox: '0 0 24 24', paths: ['M3 6h18...'] }
```

Add new ones to `components/icons.js`. Heroicons and Lucide are good sources for SVG paths.
