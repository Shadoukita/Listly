<template>
  <div class="toggle-row">
    <div class="row-icon" :class="{ on }">
      <AppIcon :d="icon" :size="16" />
    </div>
    <div class="row-body" :class="{ centered }">
      <div class="row-label">{{ label }}</div>
      <div v-if="hint" class="row-hint">{{ hint }}</div>
    </div>
    <ToggleSwitch :model-value="on" @update:model-value="$emit('change', $event)" />
  </div>
</template>

<script setup>
import AppIcon from './AppIcon.vue'
import ToggleSwitch from './ToggleSwitch.vue'
defineProps({
  icon:     { type: [String, Array], required: true },
  label:    { type: String, required: true },
  hint:     { type: String, default: '' },
  on:       { type: Boolean, default: false },
  centered: { type: Boolean, default: false },
})
defineEmits(['change'])
</script>

<style scoped>
.toggle-row {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px 16px;
  display: flex;
  align-items: center;
  gap: 14px;
}
.row-icon {
  width: 32px; height: 32px; border-radius: 8px;
  background: var(--surface-hi);
  color: var(--text-dim);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  transition: color 0.15s;
}
.row-icon.on { color: var(--accent); }
.row-body { flex: 1; }
.row-body.centered { text-align: center; }
.row-label { font-size: 14px; font-weight: 500; }
.row-hint  { font-size: 12px; color: var(--text-dim); margin-top: 2px; }
</style>
