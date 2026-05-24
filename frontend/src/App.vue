<template>
  <router-view />

  <!-- Connection loss overlay -->
  <Transition name="conn-fade">
    <div v-if="!serverOnline" class="conn-overlay">
      <div class="conn-box">
        <div class="conn-spinner" />
        <div class="conn-title">Connection lost</div>
        <div class="conn-sub">Trying to reconnect to the server…</div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { setLocale } from './plugins/i18n'
import { api } from './stores/api'
import { serverOnline, setupAllowed } from './stores/connection'

const router = useRouter()
const route  = useRoute()
const auth   = useAuthStore()

setLocale('en-US')

onMounted(async () => {
  // Invite link intercept
  const invite = new URLSearchParams(window.location.search).get('invite')
  if (invite) {
    try {
      const check = await api(`/invite/${invite}`)
      if (check.valid) {
        router.push({ path: '/invite', query: { token: invite } })
        return
      }
    } catch(e) {}
  }

  // Setup check — only redirect to /setup when server EXPLICITLY says setup_done=false.
  // Never redirect on network error (that would be confusing with the connection overlay).
  try {
    const status = await api('/status')
    if (status.setup_done === false) {
      setupAllowed.value = true
      router.push('/setup')
      return
    }
  } catch(e) {
    // Network error: connection overlay will show, stay on current page
    return
  }

  // Auto-login
  if (auth.isLoggedIn) {
    if (route.path === '/login' || route.path === '/setup') router.push('/')
    auth.fetchMe().catch(() => auth.logout())
  } else {
    if (route.path !== '/invite') router.push('/login')
  }
})
</script>

<style>
.conn-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(10, 10, 15, 0.72);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
}
.conn-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  padding: 36px 48px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 20px;
  box-shadow: 0 24px 64px rgba(0,0,0,0.5);
  text-align: center;
}
.conn-spinner {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 3px solid var(--border);
  border-top-color: var(--accent);
  animation: conn-spin 0.8s linear infinite;
}
@keyframes conn-spin {
  to { transform: rotate(360deg); }
}
.conn-title {
  font-size: 17px;
  font-weight: 600;
  letter-spacing: -0.2px;
  color: var(--text);
}
.conn-sub {
  font-size: 13px;
  color: var(--text-dim);
  max-width: 240px;
  line-height: 1.5;
}

.conn-fade-enter-active, .conn-fade-leave-active {
  transition: opacity 0.25s ease;
}
.conn-fade-enter-from, .conn-fade-leave-to {
  opacity: 0;
}
</style>
