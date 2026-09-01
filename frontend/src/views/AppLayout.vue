<template>
  <div class="app-layout">
    <!-- Mobile topbar -->
    <div class="mobile-topbar">
      <button class="mobile-menu-btn" @click="sidebarOpen = !sidebarOpen" aria-label="Menu">
        <AppIcon :d="I.grid" :size="20" />
      </button>
      <Logo :mark-size="28" :text-size="16" />
    </div>

    <Sidebar :open="sidebarOpen" @close="sidebarOpen = false" />

    <main class="main-area">
      <router-view :key="hh.current?.id" />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useHouseholdStore } from '../stores/household'
import Sidebar from '../components/Sidebar.vue'
import Logo from '../components/Logo.vue'
import AppIcon from '../components/AppIcon.vue'
import { I } from '../components/icons.js'

const auth   = useAuthStore()
const hh     = useHouseholdStore()
const sidebarOpen = ref(false)

onMounted(async () => {
  await Promise.all([hh.load(), auth.fetchModules()])
  await hh.restore(auth.user?.last_household_id)
})
</script>

<style scoped>
.app-layout {
  display: flex;
  height: 100%;
  overflow: hidden;
}
.main-area {
  flex: 1;
  overflow-y: auto;
  min-width: 0;
  background: var(--bg);
}

.mobile-topbar {
  display: none;
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 56px;
  background: var(--bg);
  border-bottom: 1px solid var(--border);
  align-items: center;
  padding: 0 16px;
  gap: 12px;
  z-index: 90;
}
.mobile-menu-btn {
  color: var(--text-dim);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  /* The icon is 20px, but the hit area must clear the 44px minimum touch
     target (WCAG 2.5.5 / iOS HIG) — the bare icon was easy to miss. */
  width: 44px; height: 44px;
  margin-left: -10px;   /* keep the icon optically aligned with the 16px gutter */
  background: transparent; border: 0; padding: 0;
  border-radius: 10px;
  flex-shrink: 0;
}
.mobile-menu-btn:active { background: var(--surface); }

@media (max-width: 768px) {
  .mobile-topbar { display: flex; }
  .main-area { padding-top: 56px; }
}
</style>
