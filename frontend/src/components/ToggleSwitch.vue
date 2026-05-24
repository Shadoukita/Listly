<template>
  <label class="toggle" :class="{ on: modelValue }">
    <input type="checkbox" :checked="modelValue" @change="$emit('update:modelValue', $event.target.checked)" />
    <span class="track">
      <span class="knob" />
    </span>
  </label>
</template>

<script setup>
defineProps({ modelValue: { type: Boolean, default: false } })
defineEmits(['update:modelValue'])
</script>

<style scoped>
.toggle { display: inline-flex; align-items: center; cursor: pointer; }
.toggle input { position: absolute; opacity: 0; width: 0; height: 0; }
.track {
  width: 40px; height: 22px; border-radius: 11px;
  background: var(--surface-hi);
  border: 1px solid var(--border);
  display: flex; align-items: center;
  padding: 0 3px;
  transition: background 0.2s, border-color 0.2s;
  position: relative;
}
.on .track {
  background: var(--accent);
  border-color: transparent;
}
.knob {
  width: 16px; height: 16px; border-radius: 50%;
  background: var(--text-mute);
  transition: transform 0.2s, background 0.2s;
}
.on .knob {
  background: var(--bg);
  transform: translateX(18px);
}
</style>
