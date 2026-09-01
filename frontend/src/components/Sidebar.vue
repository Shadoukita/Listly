<template>
  <aside class="sidebar" :class="{ open }">
    <div class="sidebar-inner">
      <!-- Brand -->
      <div class="brand">
        <Logo :mark-size="32" :text-size="18" />
      </div>

      <!-- Modules nav -->
      <nav class="nav-section">
        <div class="nav-label">Modules</div>
        <template v-for="mod in MODULES" :key="mod.id">
          <router-link
            v-if="auth.modules[mod.id]"
            :to="'/' + mod.id"
            class="nav-item"
            :class="{ active: route.path.startsWith('/' + mod.id) }"
            @click="$emit('close')"
          >
            <AppIcon :d="I[mod.icon]" :size="18" />
            <span class="nav-item-label">{{ $t('modules.' + mod.id) }}</span>
          </router-link>
        </template>

        <template v-if="auth.isAdmin">
          <div class="nav-divider" />
          <router-link to="/admin" class="nav-item" :class="{ active: route.path === '/admin' }" @click="$emit('close')">
            <AppIcon :d="I.shield" :size="18" />
            <span class="nav-item-label">Admin</span>
            <Pill tone="amber">Admin</Pill>
          </router-link>
        </template>
      </nav>

      <!-- Household switcher -->
      <div class="hh-section">
        <div class="nav-label-row">
          <span class="nav-label">Households</span>
          <span class="nav-label accent">{{ hh.households.length }}</span>
        </div>

        <div class="hh-list">
          <button
            v-for="h in visibleHouseholds"
            :key="h.id"
            class="hh-item"
            :class="{ active: hh.current?.id === h.id }"
            @click="selectHH(h)"
          >
            <Avatar :name="h.name" :color="hhColor(h)" :size="26" :round="false" />
            <div class="hh-info">
              <div class="hh-name">{{ h.name }}</div>
              <div class="hh-meta">{{ $t('household.memberCount', { count: h.member_count }) }}</div>
            </div>
            <div v-if="hh.current?.id === h.id" class="hh-dot" />
            <button v-if="h.role === 'admin' || h.role === 'owner'" class="hh-settings-btn" @click.stop="openSettings(h)" :title="$t('sidebar.householdSettings')">
              <AppIcon :d="I.settings" :size="13" />
            </button>
          </button>
        </div>

        <button v-if="hh.households.length > MAX_VISIBLE && !showAll" class="show-more" @click="showAll = true">
          {{ $t('sidebar.showMore', { count: hh.households.length - MAX_VISIBLE }) }}
        </button>
        <button v-else-if="showAll && hh.households.length > MAX_VISIBLE" class="show-more" @click="showAll = false">
          {{ $t('sidebar.showLess') }}
        </button>

        <div class="hh-actions">
          <button class="hh-action-btn" @click="showCreate = true">
            <AppIcon :d="I.plus" :size="13" :sw="2.4" /> {{ $t('sidebar.new') }}
          </button>
          <button class="hh-action-btn" @click="openJoin">
            <AppIcon :d="I.link" :size="13" /> {{ $t('sidebar.joinHousehold') }}
          </button>
        </div>
      </div>

      <!-- Footer -->
      <div class="sidebar-footer">
        <router-link to="/profile" class="user-btn" :class="{ active: route.path === '/profile' }" @click="$emit('close')">
          <Avatar :name="displayName" :src="auth.user?.profile_image || ''" :color="userColor" :size="28" />
          <div class="user-info">
            <div class="user-name">{{ displayName }}</div>
            <div class="user-handle">@{{ auth.user?.username }}</div>
          </div>
        </router-link>
        <router-link to="/settings" class="icon-btn" :class="{ active: route.path === '/settings' }" @click="$emit('close')" :aria-label="$t('settings.title')">
          <AppIcon :d="I.settings" :size="16" />
        </router-link>
        <button class="icon-btn" @click="doLogout" :aria-label="$t('auth.signIn')">
          <AppIcon :d="I.logout" :size="16" />
        </button>
      </div>
    </div>

    <!-- Overlay for mobile -->
    <div class="sidebar-overlay" @click="$emit('close')" />

    <!-- Modals -->
    <teleport to="body">
      <!-- Create household -->
      <div v-if="showCreate" class="modal-overlay" @click.self="showCreate = false">
        <div class="modal">
          <h3>{{ $t('household.newTitle') }}</h3>
          <Field v-model="newName" :label="$t('household.nameLabel')" :placeholder="$t('household.namePlaceholder')" @keydown.enter="createHH" />
          <div class="modal-actions">
            <AppButton variant="outline" size="sm" @click="showCreate = false" :disabled="creating">{{ $t('global.cancel') }}</AppButton>
            <AppButton size="sm" @click="createHH" :disabled="creating">{{ creating ? $t('global.loading') : $t('global.create') }}</AppButton>
          </div>
        </div>
      </div>

      <!-- Join household -->
      <div v-if="showJoin" class="modal-overlay" @click.self="closeJoin">
        <div class="modal">
          <template v-if="joinMode === 'choice'">
            <h3>{{ $t('household.joinTitle') }}</h3>
            <div class="join-choice">
              <button class="join-choice-btn" @click="joinMode = 'private'">
                <AppIcon :d="I.lock" :size="20" />
                <div>
                  <div class="join-choice-label">{{ $t('household.joinPrivate') }}</div>
                  <div class="join-choice-sub">{{ $t('household.joinPrivateDesc') }}</div>
                </div>
              </button>
              <button class="join-choice-btn" @click="loadPublicAndSwitch">
                <AppIcon :d="I.globe" :size="20" />
                <div>
                  <div class="join-choice-label">{{ $t('household.joinPublic') }}</div>
                  <div class="join-choice-sub">{{ $t('household.joinPublicDesc') }}</div>
                </div>
              </button>
            </div>
            <div class="modal-actions">
              <AppButton variant="outline" size="sm" @click="closeJoin">{{ $t('global.cancel') }}</AppButton>
            </div>
          </template>

          <template v-else-if="joinMode === 'private'">
            <h3>{{ $t('household.privateTitle') }}</h3>
            <Field v-model="joinCode" :label="$t('household.inviteCodeLabel')" :placeholder="$t('household.inviteCodePlaceholder')" :mono="true" @keydown.enter="joinByCode" />
            <div class="modal-actions">
              <AppButton variant="outline" size="sm" @click="joinMode = 'choice'">{{ $t('global.back') }}</AppButton>
              <AppButton size="sm" @click="joinByCode">{{ $t('global.join') }}</AppButton>
            </div>
          </template>

          <template v-else>
            <h3>{{ $t('household.publicTitle') }}</h3>
            <div v-if="loadingPublic" class="modal-loading">{{ $t('global.loading') }}</div>
            <div v-else-if="publicHH.length === 0" class="modal-empty">{{ $t('household.noPublicFound') }}</div>
            <div v-else class="public-list">
              <div v-for="h in publicHH" :key="h.id" class="public-row">
                <div>
                  <div class="public-name">{{ h.name }}</div>
                  <div class="public-meta">{{ $t('household.memberCount', { count: h.member_count }) }}</div>
                </div>
                <AppButton size="sm" @click="joinPublicHH(h)">{{ $t('global.join') }}</AppButton>
              </div>
            </div>
            <div class="modal-actions">
              <AppButton variant="outline" size="sm" @click="joinMode = 'choice'">{{ $t('global.back') }}</AppButton>
            </div>
          </template>
        </div>
      </div>
    </teleport>
  </aside>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore, MODULES, avatarColor } from '../stores/auth'
import { useHouseholdStore } from '../stores/household'
import Logo from './Logo.vue'
import AppIcon from './AppIcon.vue'
import Avatar from './Avatar.vue'
import Pill from './Pill.vue'
import Field from './Field.vue'
import AppButton from './AppButton.vue'
import { I } from './icons.js'

defineProps({ open: { type: Boolean, default: false } })
defineEmits(['close'])

const MAX_VISIBLE = 3
const router = useRouter()
const route  = useRoute()
const auth   = useAuthStore()
const hh     = useHouseholdStore()

const showAll      = ref(false)
const showCreate   = ref(false)
const showJoin     = ref(false)
const joinMode     = ref('choice')
const newName      = ref('')
const joinCode     = ref('')
const creating     = ref(false)
const publicHH     = ref([])
const loadingPublic = ref(false)

const displayName  = computed(() => auth.user?.display_name || auth.user?.username || '')
const userColor    = computed(() => avatarColor(auth.user?.id))
const visibleHouseholds = computed(() =>
  showAll.value ? hh.households : hh.households.slice(0, MAX_VISIBLE)
)

function hhColor(h) {
  const colors = ['#c79bff','#ffb86b','#7cf2a0','#9bd9ff','#ff9ec7','#ffd166']
  return colors[(h.id - 1) % colors.length]
}

async function selectHH(h) { await hh.select(h) }

async function createHH() {
  if (!newName.value.trim() || creating.value) return
  creating.value = true
  try {
    await hh.create(newName.value.trim())
    newName.value = ''; showCreate.value = false
  } finally {
    creating.value = false
  }
}

function openJoin() { joinMode.value = 'choice'; joinCode.value = ''; publicHH.value = []; showJoin.value = true }
function closeJoin() { showJoin.value = false; joinMode.value = 'choice'; joinCode.value = '' }

async function joinByCode() {
  if (!joinCode.value.trim()) return
  try { await hh.join(joinCode.value.trim()); closeJoin() } catch(e) {}
}

async function loadPublicAndSwitch() {
  joinMode.value = 'public'; loadingPublic.value = true
  try { publicHH.value = await hh.loadPublic() } catch(e) { publicHH.value = [] }
  finally { loadingPublic.value = false }
}

async function joinPublicHH(h) {
  try { await hh.joinPublic(h.id); publicHH.value = publicHH.value.filter(p => p.id !== h.id); closeJoin() } catch(e) {}
}

function openSettings(h) { router.push(`/households/${h.id}/settings`) }

function doLogout() {
  auth.logout()
  hh.current = null; hh.households = []
  router.push('/login')
}
</script>

<style scoped>
.sidebar {
  width: 272px;
  flex-shrink: 0;
  position: relative;
  z-index: 100;
}
.sidebar-inner {
  width: 272px;
  height: 100%;
  background: var(--bg);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.sidebar-overlay { display: none; }

/* Brand */
.brand {
  padding: 20px 20px 18px;
  border-bottom: 1px solid var(--border);
}

/* Nav */
.nav-section { padding: 8px 12px 0; }
.nav-label {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  color: var(--text-mute);
  padding: 8px 8px 6px;
  display: block;
}
.nav-label.accent { color: var(--accent); }
.nav-label-row { display: flex; align-items: center; justify-content: space-between; padding: 0 8px 10px; }
.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 9px 12px;
  border-radius: 10px;
  color: var(--text);
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
  cursor: pointer;
}
.nav-item:hover { background: var(--surface); }
.nav-item.active { background: var(--accent-dim); color: var(--accent); }
.nav-item-label { flex: 1; }
.nav-divider { height: 1px; background: var(--border); margin: 10px 8px; }

/* Households */
.hh-section { padding: 20px 12px 0; flex: 1; overflow-y: auto; min-height: 0; }
.hh-list { display: flex; flex-direction: column; gap: 2px; }
.hh-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 10px;
  border: 1px solid transparent;
  cursor: pointer;
  width: 100%;
  text-align: left;
  transition: background 0.15s, border-color 0.15s;
  color: var(--text);
}
.hh-item:hover { background: var(--surface); }
.hh-item.active { background: var(--surface); border-color: var(--border); }
.hh-info { flex: 1; min-width: 0; }
.hh-name { font-size: 13px; font-weight: 500; color: var(--text); }
.hh-meta { font-size: 11px; color: var(--text-mute); font-family: var(--font-mono); }
.hh-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--accent); flex-shrink: 0; }
.hh-settings-btn {
  width: 24px; height: 24px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  color: var(--text); opacity: 1;
  transition: background 0.15s;
}
.hh-settings-btn:hover { background: var(--surface-hi); }

.show-more {
  font-size: 12px; color: var(--text-dim); padding: 6px 12px;
  cursor: pointer; text-align: left;
}
.show-more:hover { color: var(--accent); }

.hh-actions { display: flex; gap: 6px; padding: 12px 8px 0; }
.hh-action-btn {
  flex: 1; padding: 7px; border-radius: 8px;
  background: var(--surface); border: 1px solid var(--border);
  color: var(--text); font-size: 12px; font-family: var(--font-sans); font-weight: 500;
  display: flex; align-items: center; justify-content: center; gap: 6px;
  cursor: pointer; transition: border-color 0.15s;
}
.hh-action-btn:hover { border-color: var(--border-hi); }

/* Footer */
.sidebar-footer {
  margin-top: auto;
  padding: 14px 12px;
  border-top: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 4px;
}
.user-btn {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 10px;
  text-decoration: none;
  color: var(--text);
  transition: background 0.15s;
  min-width: 0;
}
.user-btn:hover, .user-btn.active { background: var(--accent-dim); color: var(--accent); }
.user-info { flex: 1; min-width: 0; overflow: hidden; }
.user-name { font-size: 13px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.user-handle { font-size: 11px; color: var(--text-mute); font-family: var(--font-mono); }
.icon-btn {
  width: 32px; height: 32px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  color: var(--text); cursor: pointer;
  transition: background 0.15s, color 0.15s;
  text-decoration: none;
  flex-shrink: 0;
}
.icon-btn:hover { background: var(--surface-hi); color: var(--text); }
.icon-btn.active { background: var(--accent-dim); color: var(--accent); }

/* Modal styles */
.modal-overlay {
  position: fixed; inset: 0; z-index: 1000;
  background: rgba(0,0,0,0.6);
  display: flex; align-items: center; justify-content: center;
  padding: 20px;
}
.modal {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-card);
  padding: 24px;
  width: 100%;
  max-width: 420px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.modal h3 { font-size: 18px; font-weight: 600; letter-spacing: -0.3px; }
.modal-actions { display: flex; gap: 10px; justify-content: flex-end; }
.modal-loading, .modal-empty { font-size: 14px; color: var(--text-dim); padding: 8px 0; }

.join-choice { display: flex; flex-direction: column; gap: 10px; }
.join-choice-btn {
  display: flex; align-items: center; gap: 14px;
  padding: 14px 16px; border-radius: 12px;
  background: var(--bg); border: 1px solid var(--border);
  color: var(--text); text-align: left; cursor: pointer;
  transition: border-color 0.15s;
}
.join-choice-btn:hover { border-color: var(--border-hi); }
.join-choice-label { font-size: 14px; font-weight: 600; }
.join-choice-sub { font-size: 12px; color: var(--text-dim); margin-top: 2px; }

.public-list { display: flex; flex-direction: column; gap: 10px; max-height: 280px; overflow-y: auto; }
.public-row { display: flex; align-items: center; gap: 12px; padding: 10px; background: var(--bg); border-radius: 10px; }
.public-name { font-size: 14px; font-weight: 600; }
.public-meta { font-size: 12px; color: var(--text-dim); }

/* Mobile */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    inset: 0;
    pointer-events: none;
    width: 100%;
  }
  .sidebar.open { pointer-events: all; }
  .sidebar-inner {
    transform: translateX(-100%);
    transition: transform 0.25s ease;
    box-shadow: none;
    position: relative;
    z-index: 1;
  }
  .sidebar.open .sidebar-inner { transform: translateX(0); box-shadow: 4px 0 32px rgba(0,0,0,0.4); }
  .sidebar-overlay {
    display: block;
    position: absolute;
    inset: 0;
    background: rgba(0,0,0,0.5);
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.25s;
  }
  .sidebar.open .sidebar-overlay { opacity: 1; pointer-events: all; }
}
</style>
