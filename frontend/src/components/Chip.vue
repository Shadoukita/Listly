<template>
  <button class="chip" :class="{ active }" @click="$emit('click')">
    <span v-if="color" class="chip-dot" :style="{ background: color }" />
    <slot />
  </button>
</template>

<script setup>
defineProps({
  active: { type: Boolean, default: false },
  color:  { type: String,  default: '' },
})
defineEmits(['click'])
</script>

<style scoped>
.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 11px;
  border-radius: var(--r-pill);
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--text);
  font-size: 12px;
  font-weight: 500;
  font-family: var(--font-sans);
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
}
.chip:hover:not(.active) { border-color: var(--border-hi); }
.chip.active {
  background: var(--accent-dim);
  border-color: transparent;
  color: var(--accent);
}
.chip-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}
</style>
