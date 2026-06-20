<template>
  <div
    class="plan-card"
    :class="{ compact, selected, selecting }"
    :style="{ '--tone': tone }"
    :draggable="!compact && !selecting && !readOnly"
    @dragstart.stop="onDragStart"
    @dragend="$emit('drag-end')"
    @dragover.prevent
    @drop.prevent="$emit('drop-on')"
    @click.stop="handleClick"
    @contextmenu.prevent="onContextMenu"
    @pointerdown="startLongPress"
    @pointerup="cancelLongPress"
    @pointerleave="cancelLongPress"
  >
    <!-- left tone rail -->
    <span class="tone-rail" />

    <!-- select checkbox -->
    <span v-if="selecting" class="checkbox" :class="{ checked: selected }">
      <AppIcon v-if="selected" :d="I.check" :size="compact ? 10 : 12" :sw="3" />
    </span>

    <!-- glyph avatar (full mode) -->
    <span v-if="!compact" class="glyph" :style="{ background: glyphBg, color: tone }">
      <template v-if="plan.kind === 'recipe'">{{ glyph }}</template>
      <AppIcon v-else :d="I.note" :size="15" :sw="1.8" />
    </span>

    <!-- body -->
    <div class="body">
      <div class="title">{{ displayTitle }}</div>
      <template v-if="!compact">
        <p v-if="noteText" class="desc">{{ noteText }}</p>
        <div class="meta">
          <span class="user-dot" :style="{ background: userColor }">{{ userInitial }}</span>
          <span class="user-label">{{ plan.user_name }}</span>
          <span class="flex1" />
          <Pill :tone="plan.kind === 'recipe' ? 'accent' : 'neutral'">
            {{ plan.kind === 'recipe' ? t('mealplanner.recipe') : t('mealplanner.note') }}
          </Pill>
        </div>
      </template>
    </div>

    <!-- compact user dot -->
    <span v-if="compact" class="user-dot-sm" :style="{ background: userColor }">{{ userInitial }}</span>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import AppIcon from './AppIcon.vue'
import Pill from './Pill.vue'
import { I } from './icons.js'
import { avatarColor } from '../stores/auth'

const { t } = useI18n()

const props = defineProps({
  plan:      { type: Object,  required: true },
  compact:   { type: Boolean, default: false },
  selecting: { type: Boolean, default: false },
  selected:  { type: Boolean, default: false },
  readOnly:  { type: Boolean, default: false },
})

const emit = defineEmits(['click', 'long-press', 'drag-start', 'drag-end', 'drop-on'])

// ── Tone palette (derived from recipe_id since recipes have no tone in DB) ──
const TONES = ['#c79bff','#ffb86b','#7cf2a0','#9bd9ff','#ff9ec7','#ff9466','#ffd166']
const tone = computed(() => {
  if (props.plan.kind === 'recipe' && props.plan.recipe_id != null) {
    return TONES[props.plan.recipe_id % TONES.length]
  }
  return '#9ca0a8'
})
const glyphBg = computed(() => `${tone.value}22`)

// ── Display fields ────────────────────────────────────────────────────────────
const displayTitle = computed(() =>
  props.plan.kind === 'recipe'
    ? (props.plan.recipe_name || t('mealplanner.recipe'))
    : (props.plan.title || 'Untitled')
)
const displayDesc = computed(() =>
  props.plan.kind === 'recipe'
    ? (props.plan.recipe_description || '')
    : (props.plan.description || '')
)
const noteText = computed(() => props.plan.notes || displayDesc.value)
const glyph    = computed(() => (displayTitle.value[0] || '?').toUpperCase())

const userColor   = computed(() => avatarColor(props.plan.user_id))
const userInitial = computed(() => ((props.plan.user_name || '?')[0] || '?').toUpperCase())

// ── Long-press (500 ms) ───────────────────────────────────────────────────────
let pressTimer = null
let longFired  = false

function startLongPress() {
  if (props.readOnly || props.selecting) return
  longFired = false
  pressTimer = setTimeout(() => {
    longFired = true
    emit('long-press')
  }, 500)
}
function cancelLongPress() {
  if (pressTimer) { clearTimeout(pressTimer); pressTimer = null }
}
function handleClick() {
  if (longFired) { longFired = false; return }
  emit('click')
}
function onDragStart(e) {
  e.dataTransfer.effectAllowed = 'move'
  emit('drag-start')
}
function onContextMenu() {
  if (!props.readOnly && !props.selecting) emit('long-press')
}
</script>

<style scoped>
.plan-card {
  position: relative;
  overflow: hidden;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--surface);
  padding: 11px 12px;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  cursor: pointer;
  user-select: none;
  transition: border-color 140ms ease, background 140ms ease;
}
.plan-card.compact {
  border-radius: 8px;
  padding: 6px 8px;
  align-items: center;
  gap: 7px;
}
.plan-card.selected {
  background: var(--accent-dim);
  border-color: var(--accent);
}
.plan-card:hover { border-color: var(--border-hi); }

.tone-rail {
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 3px;
  background: var(--tone);
}

.checkbox {
  flex-shrink: 0;
  width: 18px; height: 18px;
  border-radius: 5px;
  background: transparent;
  border: 1.5px solid var(--border-hi);
  display: flex; align-items: center; justify-content: center;
  color: var(--accent-ink);
  margin-left: 2px;
}
.checkbox.checked {
  background: var(--accent);
  border-color: var(--accent);
}
.plan-card.compact .checkbox { width: 15px; height: 15px; }

.glyph {
  flex-shrink: 0;
  width: 30px; height: 30px;
  border-radius: 8px;
  margin-left: 2px;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 13px;
}

.body { flex: 1; min-width: 0; }
.title {
  font-size: 14px;
  font-weight: 600;
  letter-spacing: -0.1px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.plan-card.compact .title { font-size: 11.5px; }

.desc {
  margin: 3px 0 0;
  font-size: 12px;
  color: var(--text-dim);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.meta {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-top: 7px;
}
.user-dot {
  width: 16px; height: 16px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 9px; font-weight: 700;
  color: var(--accent-ink);
  flex-shrink: 0;
}
.user-label { font-size: 11px; color: var(--text-dim); }
.flex1 { flex: 1; }

.user-dot-sm {
  flex-shrink: 0;
  width: 14px; height: 14px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 8px; font-weight: 700;
  color: var(--accent-ink);
}
</style>
