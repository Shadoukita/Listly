<template>
  <span class="pill" :class="tone">
    <slot />
  </span>
</template>

<script setup>
defineProps({
  tone: { type: String, default: 'neutral' }, // neutral | accent | amber | danger | success
})
</script>

<style scoped>
.pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 9px;
  border-radius: var(--r-pill);
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  white-space: nowrap;
}
.neutral { background: rgba(255,255,255,0.06); color: var(--text-dim); border: 1px solid var(--border); }
.accent  { background: var(--accent-dim); color: var(--accent); border: 1px solid transparent; }
.amber   { background: var(--amber-bg); color: var(--amber); border: 1px solid transparent; }
.danger  { background: var(--danger-bg); color: var(--danger); border: 1px solid transparent; }
.success { background: var(--success-bg); color: var(--success); border: 1px solid transparent; }
</style>
