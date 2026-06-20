<template>
  <div class="admin-view">
    <div class="topbar">
      <div>
        <div class="topbar-mono amber">{{ $t('admin.title') }} · {{ $t('admin.instanceWide') }}</div>
        <div class="topbar-title-row">
          <h1 class="page-title">{{ $t('admin.instanceTitle') }}</h1>
          <Pill tone="amber">Admin</Pill>
        </div>
      </div>
    </div>

    <div class="content">
      <!-- Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-value">{{ stats.users }}</div>
          <div class="mono">{{ $t('admin.usersLabel') }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.households }}</div>
          <div class="mono">{{ $t('admin.households') }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.recipes }}</div>
          <div class="mono">{{ $t('admin.recipesCount') }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-value accent">{{ stats.openInvites }}</div>
          <div class="mono">{{ $t('admin.openInvites') }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.modulesOn }} / {{ MODULES.length }}</div>
          <div class="mono">{{ $t('admin.modulesOn') }}</div>
        </div>
      </div>

      <!-- Hosted modules -->
      <section class="card">
        <h3 class="section-title">{{ $t('admin.hostedModules') }}</h3>
        <p class="section-hint">{{ $t('admin.hostedModulesDesc') }}</p>
        <ToggleRow
          v-for="mod in MODULES" :key="mod.id"
          :icon="I[mod.icon]"
          :label="$t('modules.' + mod.id)"
          :on="auth.globalModules[mod.id]"
          @change="toggleGlobalModule(mod.id, $event)"
        />
      </section>

      <!-- Endpoint URL -->
      <section class="card">
        <h3 class="section-title">{{ $t('admin.endpointUrl') }}</h3>
        <p class="section-hint">{{ $t('admin.endpointDesc') }}</p>
        <Field v-model="endpointUrl" :label="$t('admin.endpointUrl')" :placeholder="$t('setup.endpointPlaceholder')" :mono="true" @keydown.enter="saveEndpoint" />
        <div class="card-row">
          <span class="endpoint-hint">{{ $t('admin.endpointInviteHint') }}</span>
          <AppButton variant="outline" size="sm" @click="saveEndpoint">{{ $t('global.save') }}</AppButton>
        </div>
        <span v-if="epSaved" class="saved-msg">{{ $t('global.saved') }}</span>
      </section>

      <!-- Invite links -->
      <section class="card">
        <h3 class="section-title">{{ $t('admin.inviteLinks') }}</h3>
        <p class="section-hint">{{ $t('admin.inviteLinksDesc') }}</p>

        <div v-if="newInviteUrl" class="invite-box">
          <div class="invite-url">{{ newInviteUrl }}</div>
          <AppButton variant="ghost" size="sm" @click="copyInvite">
            <AppIcon :d="I.copy" :size="14" /> {{ $t('global.copy') }}
          </AppButton>
        </div>
        <div v-if="newToken" class="token-display">
          <span class="mono">{{ $t('admin.token') }}</span>
          <button class="token-val" @click="copyToken">{{ newToken }}</button>
          <span v-if="tokenCopied" class="saved-msg">✓</span>
        </div>

        <AppButton size="sm" @click="createInvite">
          <AppIcon :d="I.plus" :size="14" :sw="2.2" /> {{ $t('admin.newLink') }}
        </AppButton>

        <div v-if="invites.length" class="invite-list">
          <div v-for="(inv, i) in invites" :key="inv.id" class="invite-row" :class="{ divide: i > 0 }">
            <span class="invite-token">{{ inv.token.substring(0, 20) }}…</span>
            <span style="flex:1" />
            <Pill v-if="inv.used" tone="neutral">{{ $t('admin.usedBy', { name: inv.used_by_name }) }}</Pill>
            <Pill v-else tone="success">{{ $t('admin.open') }}</Pill>
            <div class="mono" style="margin-left:8px;">{{ formatDate(inv.created_at) }}</div>
            <button v-if="!inv.used" class="del-btn" @click="deleteInvite(inv)" :aria-label="$t('global.delete')">
              <AppIcon :d="I.trash" :size="14" />
            </button>
          </div>
        </div>
      </section>

      <!-- Users -->
      <section class="card">
        <h3 class="section-title">{{ $t('admin.users') }}</h3>
        <div class="user-list">
          <div v-for="(u, i) in users" :key="u.id" class="user-row" :class="{ divide: i > 0 }">
            <Avatar :name="u.display_name || u.username" :src="u.profile_image || ''" :color="avatarColor(u.id)" :size="32" />
            <div class="user-info">
              <div class="user-name-row">
                <span class="user-mono">@{{ u.username }}</span>
                <span v-if="u.id === auth.user?.id" class="self-label">{{ $t('admin.you') }}</span>
              </div>
              <div class="user-meta-row">
                <Pill :tone="u.role === 'admin' ? 'accent' : 'neutral'">{{ u.role }}</Pill>
                <span class="mono">{{ $t('admin.joined') }} {{ formatDate(u.created_at) }}</span>
              </div>
            </div>
            <button v-if="u.id !== auth.user?.id" class="del-btn" @click="deleteUser(u)" :aria-label="$t('global.delete')">
              <AppIcon :d="I.trash" :size="14" />
            </button>
          </div>
        </div>
      </section>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore, MODULES, avatarColor } from '../stores/auth'
import { api } from '../stores/api'
import Pill from '../components/Pill.vue'
import Field from '../components/Field.vue'
import AppButton from '../components/AppButton.vue'
import AppIcon from '../components/AppIcon.vue'
import Avatar from '../components/Avatar.vue'
import ToggleRow from '../components/ToggleRow.vue'
import { I } from '../components/icons.js'

const { t } = useI18n()
const auth = useAuthStore()

const endpointUrl  = ref('')
const epSaved      = ref(false)
const invites      = ref([])
const users        = ref([])
const newInviteUrl = ref('')
const newToken     = ref('')
const tokenCopied  = ref(false)
const adminStats   = ref({ households: 0, recipes: 0 })


const stats = computed(() => ({
  users:       users.value.length,
  households:  adminStats.value.households,
  recipes:     adminStats.value.recipes,
  openInvites: invites.value.filter(i => !i.used).length,
  modulesOn:   MODULES.filter(m => auth.globalModules[m.id]).length,
}))

onMounted(async () => {
  try { const s = await api('/settings'); endpointUrl.value = s.endpoint_url || '' } catch(e) {}
  try { invites.value = await api('/invites') } catch(e) {}
  try { users.value = await api('/users') } catch(e) {}
  try { adminStats.value = await api('/admin/stats') } catch(e) {}
})

async function toggleGlobalModule(id, val) { await auth.setGlobalModule(id, val) }

async function saveEndpoint() {
  try {
    await api('/settings', 'PUT', { endpoint_url: endpointUrl.value })
    epSaved.value = true; setTimeout(() => epSaved.value = false, 2000)
  } catch(e) {}
}

async function createInvite() {
  try {
    const res = await api('/invites', 'POST')
    const base = endpointUrl.value || window.location.origin
    newInviteUrl.value = `${base}/?invite=${res.token}`
    newToken.value = res.token
    invites.value = await api('/invites')
  } catch(e) {}
}

function copyInvite() { navigator.clipboard.writeText(newInviteUrl.value) }
function copyToken() { navigator.clipboard.writeText(newToken.value); tokenCopied.value = true; setTimeout(() => tokenCopied.value = false, 2000) }

async function deleteInvite(inv) {
  if (!confirm(t('admin.deleteInviteConfirm'))) return
  try { await api(`/invites/${inv.id}`, 'DELETE'); invites.value = invites.value.filter(i => i.id !== inv.id) } catch(e) {}
}

async function deleteUser(u) {
  if (!confirm(t('admin.deleteUserConfirm', { name: u.username }))) return
  try { await api(`/users/${u.id}`, 'DELETE'); users.value = users.value.filter(x => x.id !== u.id) } catch(e) {}
}

function formatDate(ts) {
  if (!ts) return ''
  return new Date(ts).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}
</script>

<style scoped>
.admin-view { display: flex; flex-direction: column; min-height: 100%; }
.topbar { padding: 18px 32px; border-bottom: 1px solid var(--border); }
.topbar-mono { font-family: var(--font-mono); font-size: 10px; font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase; color: var(--text-mute); }
.topbar-mono.amber { color: var(--amber); }
.topbar-title-row { display: flex; align-items: center; gap: 10px; margin-top: 4px; }
.page-title { font-size: 22px; font-weight: 600; letter-spacing: -0.4px; }
.content { padding: 28px 32px; max-width: 820px; width: 100%; margin: 0 auto; display: flex; flex-direction: column; gap: 28px; box-sizing: border-box; }
.mono { font-family: var(--font-mono); font-size: 10px; font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase; color: var(--text-mute); }

.stats-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; }
.stat-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 14px 16px; }
.stat-value { font-size: 24px; font-weight: 600; letter-spacing: -0.4px; color: var(--text); margin-bottom: 2px; font-feature-settings: "tnum"; }
.stat-value.accent { color: var(--accent); }

.card { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 20px; display: flex; flex-direction: column; gap: 10px; }
.section-title { font-size: 16px; font-weight: 600; letter-spacing: -0.2px; }
.section-hint { font-size: 13px; color: var(--text-dim); }
.card-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.endpoint-hint { font-size: 12px; color: var(--text-mute); font-family: var(--font-mono); }
.endpoint-hint-accent { color: var(--text-dim); }
.saved-msg { font-size: 13px; color: var(--success); }

.invite-box { background: var(--bg); border: 1px solid var(--border); border-radius: 12px; padding: 12px; display: flex; align-items: center; gap: 10px; }
.invite-url { background: var(--accent-dim); color: var(--accent); padding: 4px 10px; border-radius: 6px; font-family: var(--font-mono); font-size: 12px; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.token-display { display: flex; align-items: center; gap: 10px; }
.token-val { font-family: var(--font-mono); font-size: 12px; color: var(--text-dim); cursor: pointer; }
.token-val:hover { color: var(--accent); }

.invite-list { background: var(--bg); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
.invite-row { display: flex; align-items: center; gap: 10px; padding: 11px 16px; }
.invite-row.divide { border-top: 1px solid var(--border); }
.invite-token { font-family: var(--font-mono); font-size: 12px; color: var(--text); letter-spacing: 0.3px; }

.user-list { background: var(--bg); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
.user-row { display: flex; align-items: center; gap: 12px; padding: 11px 16px; }
.user-row.divide { border-top: 1px solid var(--border); }
.user-info { flex: 1; min-width: 0; }
.user-name-row { display: flex; align-items: center; gap: 8px; }
.user-mono { font-family: var(--font-mono); font-size: 13px; color: var(--text); }
.self-label { font-size: 12px; color: var(--text-dim); }
.user-meta-row { display: flex; align-items: center; gap: 8px; margin-top: 4px; }

.del-btn { width: 28px; height: 28px; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: var(--text-mute); cursor: pointer; transition: all 0.15s; }
.del-btn:hover { background: var(--danger-bg); color: var(--danger); }

@media (max-width: 900px) { .stats-grid { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 768px) { .stats-grid { grid-template-columns: repeat(2, 1fr); } .topbar, .content { padding-left: 20px; padding-right: 20px; } }

</style>
