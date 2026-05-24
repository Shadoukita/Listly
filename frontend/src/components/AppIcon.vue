<!-- Inline SVG icon wrapper. Pass d as string path or array of paths. -->
<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    :stroke-width="sw"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <path v-if="typeof d === 'string'" :d="d" />
    <template v-else>
      <path v-for="(p, i) in d" :key="i" :d="p" />
    </template>
    <slot />
  </svg>
</template>

<script setup>
defineProps({
  d:    { type: [String, Array], default: '' },
  size: { type: Number, default: 20 },
  sw:   { type: Number, default: 1.8 },
})
</script>
