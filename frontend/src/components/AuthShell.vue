<template>
  <div class="auth-shell">
    <!-- Left rail: branding -->
    <div class="left-rail">
      <div class="left-top">
        <Logo :mark-size="42" :text-size="28" />
      </div>
      <div class="left-body">
        <h1 class="tagline">
          Shop together,<br>
          <span class="tagline-dim">forget nothing.</span>
        </h1>
        <p class="tagline-sub">
          A self-hosted shopping list for households. Lives on your server, syncs across web and Android.
        </p>
        <div class="feature-list">
          <div v-for="f in features" :key="f" class="feature-row">
            <div class="feature-check">
              <AppIcon :d="I.check" :size="11" :sw="3" />
            </div>
            <span>{{ f }}</span>
          </div>
        </div>
      </div>
      <div class="left-footer">
        <span class="mono">Listly · Host it yourself</span>
      </div>
    </div>

    <!-- Right rail: form -->
    <div class="right-rail">
      <slot />
    </div>
  </div>
</template>

<script setup>
import Logo from './Logo.vue'
import AppIcon from './AppIcon.vue'
import { I } from './icons.js'

const features = [
  'Real-time sync across devices',
  'Per-household invite codes',
  'Built-in dark mode, modular by design',
]
</script>

<style scoped>
.auth-shell {
  width: 100%;
  height: 100%;
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-sans);
  display: flex;
  overflow: hidden;
}

/* Left rail */
.left-rail {
  width: 460px;
  flex-shrink: 0;
  padding: 60px 56px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  background: radial-gradient(at 0% 100%, rgba(199,155,255,0.08) 0%, transparent 50%);
  border-right: 1px solid var(--border);
}
.left-top { display: flex; }
.left-body { margin-top: auto; }
.left-footer { margin-top: 24px; }

.tagline {
  font-size: 42px;
  font-weight: 600;
  letter-spacing: -1.2px;
  line-height: 1.05;
}
.tagline-dim { color: var(--text-dim); }
.tagline-sub {
  margin-top: 16px;
  font-size: 15px;
  line-height: 1.6;
  color: var(--text-dim);
  max-width: 320px;
}
.feature-list { margin-top: 28px; display: flex; flex-direction: column; gap: 10px; }
.feature-row { display: flex; align-items: center; gap: 10px; font-size: 13px; color: var(--text-dim); }
.feature-check {
  width: 18px; height: 18px; border-radius: 5px;
  background: var(--accent-dim); color: var(--accent);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.mono {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  color: var(--text-mute);
}

/* Right rail */
.right-rail {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px;
  background: var(--bg2);
  overflow-y: auto;
}

/* Mobile: stack vertically */
@media (max-width: 768px) {
  .auth-shell { flex-direction: column; }
  .left-rail { display: none; }
  .right-rail { padding: 32px 24px; align-items: flex-start; }
}
</style>
