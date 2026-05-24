<template>
  <div class="avatar" :style="{ width: size + 'px', height: size + 'px', background: src ? 'transparent' : color, fontSize: Math.round(size * 0.42) + 'px', borderRadius: round ? '50%' : Math.round(size * 0.27) + 'px' }">
    <img v-if="src" :src="src" alt="" class="avatar-img" />
    <template v-else>{{ initials }}</template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({
  name:  { type: String,  default: '' },
  src:   { type: String,  default: '' },
  color: { type: String,  default: 'var(--surface-hi)' },
  size:  { type: Number,  default: 32 },
  round: { type: Boolean, default: true },
})
const initials = computed(() => (props.name || '?').slice(0, 1).toUpperCase())
</script>

<style scoped>
.avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent-ink);
  font-weight: 600;
  flex-shrink: 0;
  font-family: var(--font-sans);
  overflow: hidden;
}
.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
</style>
