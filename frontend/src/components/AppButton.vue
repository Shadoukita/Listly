<template>
  <button
    type="button"
    class="btn"
    :class="[variant, size, { full }]"
    :disabled="disabled"
    v-bind="$attrs"
  >
    <slot />
  </button>
</template>

<script setup>
defineProps({
  variant:  { type: String, default: 'primary' }, // primary | outline | ghost | danger
  size:     { type: String, default: 'md' },       // sm | md
  full:     { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
})
</script>

<style scoped>
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-family: var(--font-sans);
  font-weight: 600;
  letter-spacing: -0.1px;
  border-radius: 10px;
  cursor: pointer;
  transition: opacity 0.15s, filter 0.15s;
  white-space: nowrap;
  border: 1px solid transparent;
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn:not(:disabled):hover { filter: brightness(1.08); }
.btn:not(:disabled):active { filter: brightness(0.95); }

/* Sizes */
.sm { padding: 8px 14px; font-size: 13px; }
.md { padding: 12px 18px; font-size: 14px; }

/* Variants */
.primary { background: var(--accent); color: var(--accent-ink); box-shadow: 0 8px 24px -8px rgba(199,155,255,0.5); }
.outline  { background: transparent; color: var(--text); border-color: var(--border-hi); }
.ghost    { background: transparent; color: var(--text-dim); }
.danger   { background: var(--danger-bg); color: var(--danger); border-color: rgba(255,122,122,0.3); }

/* Full width */
.full { width: 100%; }
</style>
