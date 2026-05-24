<template>
  <div class="logo-lockup">
    <div class="logo-mark" :style="{ width: markSize + 'px', height: markSize + 'px', borderRadius: Math.round(markSize * 0.27) + 'px' }">
      <svg :width="markSize * 0.55" :height="markSize * 0.55" viewBox="0 0 24 24" fill="none"
           stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M4 7h12M4 12h12M4 17h7"/>
        <path d="M15 17l2.4 2.4L22 14.8" stroke-width="2.6"/>
      </svg>
    </div>
    <span class="logo-wordmark" :style="{ fontSize: textSize + 'px' }">
      Listly<span class="logo-dot">.</span>
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({
  markSize: { type: Number, default: 32 },
  textSize: { type: Number, default: 18 },
})
</script>

<style scoped>
.logo-lockup {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}
.logo-mark {
  background: var(--accent);
  color: var(--accent-ink);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.logo-wordmark {
  font-weight: 600;
  letter-spacing: -0.4px;
  color: var(--text);
}
.logo-dot {
  color: var(--accent);
}
</style>
