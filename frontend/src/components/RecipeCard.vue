<template>
  <div
    class="recipe-card"
    :class="{ 'is-selecting': selecting, 'is-selected': selected, 'is-pressing': pressing }"
    @pointerdown="onPointerDown"
    @pointerup="onPointerUp"
    @pointerleave="onPointerLeave"
    @pointermove="onPointerMove"
    @click="onClick"
    @dragstart.prevent
  >
    <!-- Image / placeholder -->
    <div class="recipe-img" :style="imgStyle">
      <div class="img-glow" :style="{ background: cardColor }" />
      <div v-if="!recipe.image_url" class="img-placeholder">
        <div class="img-plate">{{ initials }}</div>
      </div>
      <img v-else :src="recipe.image_url" class="img-photo" alt="" draggable="false" />
      <div class="img-badge">
        <AppIcon :d="I.chef" :size="10" :sw="2.2" /> {{ $t('recipes.badge') }}
      </div>
    </div>

    <!-- Body -->
    <div class="card-body">
      <h3 class="recipe-name">{{ recipe.name }}</h3>
      <p v-if="recipe.description" class="recipe-desc">{{ recipe.description }}</p>

      <div class="meta-row">
        <span class="meta-item">
          <AppIcon :d="I.clock" :size="12" />
          <span class="mono">{{ timeLabel }}</span>
        </span>
        <span class="dot" />
        <span class="mono">{{ recipe.servings || '?' }} {{ $t('recipes.perServingShort') }}</span>
        <template v-if="recipe.calories != null">
          <span class="dot" />
          <span class="mono">{{ recipe.calories }} kcal / {{ recipe.calories_unit === '100g' ? $t('recipes.per100g') : $t('recipes.perServingShort') }}</span>
        </template>
        <span class="spacer" />
        <Avatar :name="recipe.created_by_name || '?'" :src="recipe.created_by_profile_image || ''" :color="byColor" :size="18" />
      </div>

      <div class="bottom-row">
        <div v-if="tags.length" class="tags-row">
          <Chip v-for="tag in tags.slice(0, 3)" :key="tag">{{ tag }}</Chip>
        </div>
        <span v-if="recipe.household_name && currentHouseholdId && recipe.household_id !== currentHouseholdId"
              class="hh-badge">
          {{ recipe.household_name }}
        </span>
      </div>
    </div>

    <!-- Selection indicator -->
    <div v-if="selecting" class="sel-indicator" :class="{ checked: selected }">
      <svg v-if="selected" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="20 6 9 17 4 12"/>
      </svg>
    </div>

    <!-- Long-press progress ring -->
    <svg v-if="pressing" class="press-ring" viewBox="0 0 36 36">
      <circle cx="18" cy="18" r="14" fill="none" stroke="rgba(255,255,255,0.18)" stroke-width="2.5"/>
      <circle cx="18" cy="18" r="14" fill="none" stroke="var(--accent)" stroke-width="2.5"
              stroke-dasharray="88" :stroke-dashoffset="88 - (88 * pressProgress)"
              stroke-linecap="round" transform="rotate(-90 18 18)"/>
    </svg>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { avatarColor } from '../stores/auth'
import Avatar from './Avatar.vue'
import Chip from './Chip.vue'
import AppIcon from './AppIcon.vue'
import { I } from './icons.js'

const { t } = useI18n()

const props = defineProps({
  recipe:             { type: Object,  required: true },
  currentHouseholdId: { type: Number,  default: null  },
  selecting:          { type: Boolean, default: false },
  selected:           { type: Boolean, default: false },
})
const emit = defineEmits(['open', 'long-press', 'select-toggle'])

const PALETTE   = ['#c79bff','#ffb86b','#7cf2a0','#9bd9ff','#ff9ec7','#ffd166']
const cardColor = computed(() => PALETTE[(((props.recipe.id || 1) - 1) % PALETTE.length)])

const imgStyle = computed(() => ({
  background: `linear-gradient(135deg, ${cardColor.value}33 0%, ${cardColor.value}11 60%, var(--surface-hi) 100%)`,
}))

const initials  = computed(() => (props.recipe.name || '?')[0].toUpperCase())
const tags      = computed(() => { try { return JSON.parse(props.recipe.tags_json || '[]') } catch { return [] } })
const byColor   = computed(() => avatarColor(props.recipe.created_by))
const timeLabel = computed(() => {
  const prep = props.recipe.prep_time
  const cook = props.recipe.cook_time
  if (prep && cook) return `${prep} · ${cook}`
  return prep || cook || '–'
})

// ── Long-press ──────────────────────────────────────────────────────────────
const LONG_PRESS_MS = 1000
const pressing     = ref(false)
const pressProgress = ref(0)

let pressTimer    = null
let rafId         = null
let pressStart    = 0
let didLongPress  = false
let startX        = 0
let startY        = 0

function onPointerDown(e) {
  if (e.button !== undefined && e.button !== 0) return
  e.preventDefault()
  // Capture pointer so mouse events keep firing even if cursor leaves the element
  e.currentTarget.setPointerCapture(e.pointerId)

  didLongPress = false
  startX = e.clientX
  startY = e.clientY
  pressing.value = true
  pressStart = Date.now()
  pressProgress.value = 0

  function tick() {
    const elapsed = Date.now() - pressStart
    pressProgress.value = Math.min(elapsed / LONG_PRESS_MS, 1)
    if (elapsed < LONG_PRESS_MS) {
      rafId = requestAnimationFrame(tick)
    }
  }
  rafId = requestAnimationFrame(tick)

  pressTimer = setTimeout(() => {
    didLongPress = true
    cancelPress()
    emit('long-press', props.recipe)
  }, LONG_PRESS_MS)
}

function onPointerUp() { cancelPress() }
// pointerleave only fires for non-captured pointers; with capture active it won't
// cancel the press — pointermove's distance check handles cancellation instead
function onPointerLeave() { if (!pressing.value) return; cancelPress() }

function onPointerMove(e) {
  const dx = e.clientX - startX
  const dy = e.clientY - startY
  if (Math.abs(dx) > 6 || Math.abs(dy) > 6) cancelPress()
}

function cancelPress() {
  clearTimeout(pressTimer)
  cancelAnimationFrame(rafId)
  pressing.value = false
  pressProgress.value = 0
  pressTimer = null
  rafId = null
}

function onClick() {
  if (didLongPress) { didLongPress = false; return }
  if (props.selecting) {
    emit('select-toggle', props.recipe.id)
  } else {
    emit('open')
  }
}
</script>

<style scoped>
.recipe-card {
  background: var(--surface);
  border: 2px solid transparent;
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: border-color 0.15s, filter 0.15s, transform 0.15s;
  position: relative;
  user-select: none;
  touch-action: none;
}
.recipe-card:not(.is-selecting):hover { border-color: var(--border-hi); transform: translateY(-1px); }
.recipe-card.is-selecting { cursor: default; }
.recipe-card.is-selecting:hover { border-color: rgba(255,255,255,0.15); }
.recipe-card.is-selected {
  border-color: rgba(255,255,255,0.75);
  filter: brightness(1.14);
}

.recipe-img {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 10;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.img-glow {
  position: absolute; width: 70%; height: 70%; border-radius: 50%;
  opacity: 0.18; filter: blur(40px);
}
.img-placeholder {
  position: relative;
  width: 88px; height: 88px; border-radius: 50%;
  background: var(--bg2); border: 1px solid rgba(199,155,255,0.33);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 8px 24px rgba(0,0,0,0.4);
}
.img-plate { font-size: 32px; font-weight: 700; color: v-bind(cardColor); letter-spacing: -1px; }
.img-photo { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.img-badge {
  position: absolute; top: 12px; left: 12px;
  display: inline-flex; align-items: center; gap: 5px;
  padding: 3px 8px; border-radius: 999px;
  background: rgba(0,0,0,0.4); color: #f0f1f3;
  font-family: var(--font-mono); font-size: 10px; letter-spacing: 0.4px;
  text-transform: uppercase; backdrop-filter: blur(8px);
}

.card-body { padding: 16px; display: flex; flex-direction: column; gap: 8px; }
.recipe-name { margin: 0; font-size: 16px; font-weight: 600; letter-spacing: -0.2px; }
.recipe-desc {
  margin: 0; font-size: 12.5px; color: var(--text-dim); line-height: 1.4;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.meta-row { display: flex; align-items: center; gap: 10px; margin-top: 4px; }
.meta-item { display: inline-flex; align-items: center; gap: 4px; }
.mono { font-family: var(--font-mono); font-size: 10px; font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase; color: var(--text-mute); }
.dot { width: 3px; height: 3px; border-radius: 50%; background: var(--text-mute); }
.spacer { flex: 1; }
.bottom-row { display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; margin-top: 2px; }
.tags-row { display: flex; gap: 5px; flex-wrap: wrap; flex: 1; }
.hh-badge {
  flex-shrink: 0;
  padding: 2px 7px; border-radius: 6px;
  background: var(--accent-dim); color: var(--accent);
  font-family: var(--font-mono); font-size: 9px; font-weight: 600;
  letter-spacing: 0.3px; text-transform: uppercase; white-space: nowrap;
}

/* Selection indicator — top-right circle */
.sel-indicator {
  position: absolute; top: 10px; right: 10px;
  width: 22px; height: 22px; border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.55);
  background: rgba(0,0,0,0.35);
  backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
  color: #fff;
  transition: background 0.15s, border-color 0.15s;
}
.sel-indicator.checked {
  background: var(--accent);
  border-color: var(--accent);
}

/* Long-press progress ring */
.press-ring {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 36px; height: 36px;
  pointer-events: none;
}
.press-ring circle { transition: stroke-dashoffset 0.05s linear; }
</style>
