<template>
  <div class="section-header">
    <span class="label">{{ label }}</span>
    <span class="line" />
    <button v-if="action" class="action" :class="{ danger }" @click="$emit('action')">{{ action }}</button>
  </div>
</template>

<script setup>
defineProps({
  label:  { type: String,  required: true },
  action: { type: String,  default: '' },
  danger: { type: Boolean, default: false },
})
defineEmits(['action'])
</script>

<style scoped>
.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.label {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  color: var(--text-dim);
  white-space: nowrap;
}
.line {
  flex: 1;
  height: 1px;
  background: var(--border);
}
.action {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  color: var(--accent);
  white-space: nowrap;
  cursor: pointer;
}
.action.danger { color: var(--danger); }
</style>
