<template>
  <div class="hh-settings-view">
    <div class="topbar">
      <div>
        <div class="topbar-mono">{{ $t('household.settings.changeName') }} · settings</div>
        <div class="topbar-title-row">
          <Avatar :name="hh.current?.name || ''" :color="hhColor" :size="32" :round="false" />
          <h1 class="page-title">{{ hh.current?.name || 'Household settings.' }}</h1>
          <Pill v-if="auth.isAdmin" tone="accent">Admin</Pill>
        </div>
      </div>
      <router-link to="/shopping" class="close-btn" aria-label="Back">
        <AppIcon :d="I.x" :size="18" />
      </router-link>
    </div>

    <div class="content">
      <div v-if="error" class="error-msg">{{ error }}</div>

      <!-- General — owner + admin only -->
      <section v-if="hh.myRank >= hh.ROLE_RANK.admin" class="card">
        <h3 class="section-title">General</h3>

        <div class="field-row">
          <Field v-model="name" :label="$t('household.settings.changeName')" :placeholder="hh.current?.name" @keydown.enter="saveName" />
          <AppButton variant="outline" size="sm" @click="saveName">{{ $t('global.save') }}</AppButton>
        </div>
        <span v-if="nameSaved" class="saved-msg">{{ $t('global.saved') }}</span>

        <ToggleRow
          :icon="I.globe"
          :label="$t('household.settings.isPublic')"
          :hint="$t('household.settings.isPublicDesc')"
          :on="isPublic"
          @change="togglePublic"
        />
      </section>

      <!-- Invite code — owner + admin only -->
      <section v-if="hh.myRank >= hh.ROLE_RANK.admin" class="card">
        <h3 class="section-title">{{ $t('household.settings.inviteCode') }}</h3>
        <p class="section-hint">Share this code with people you want to invite.</p>

        <div class="code-display">
          <span class="code-val">{{ inviteCode }}</span>
          <span v-if="codeCopied" class="saved-msg">✓ Copied</span>
          <AppButton variant="ghost" size="sm" @click="copyCode">
            <AppIcon :d="I.copy" :size="14" /> {{ $t('global.copy') }}
          </AppButton>
        </div>

        <div class="card-row">
          <span class="section-hint">{{ $t('household.settings.regenerateDesc') }}</span>
          <AppButton variant="outline" size="sm" :disabled="regenLoading" @click="regenCode">
            <AppIcon :d="I.refresh" :size="14" />
            {{ regenLoading ? $t('global.loading') : $t('household.settings.regenerateCode') }}
          </AppButton>
        </div>
      </section>

      <!-- Members — visible to all -->
      <section class="card">
        <h3 class="section-title">{{ $t('household.settings.membersTitle', { count: members.length }) }}</h3>

        <div v-if="loadingMembers" class="loading-hint">{{ $t('global.loading') }}</div>
        <div v-else class="member-list">
          <div v-for="(m, i) in members" :key="m.id" class="member-row" :class="{ divide: i > 0 }">
            <Avatar :name="m.display_name || m.username" :src="m.profile_image || ''" :color="avatarColor(m.id)" :size="34" />
            <div class="member-info">
              <div class="member-name-row">
                <span class="member-name">{{ m.display_name || m.username }}</span>
                <span v-if="m.id === auth.user?.id" class="self-label">({{ $t('admin.you') }})</span>
              </div>
              <div class="member-meta">
                <span class="mono">@{{ m.username }}</span>
                <!-- Role pill: clickable for owner (not for yourself) -->
                <button
                  v-if="hh.myRole === 'owner' && m.id !== auth.user?.id"
                  class="role-pill role-pill-btn"
                  :class="'role-' + m.role"
                  @click="openRolePicker(m)"
                >
                  {{ $t('household.roles.' + m.role) }}
                  <AppIcon :d="I.chevD" :size="9" :sw="2.5" />
                </button>
                <span v-else class="role-pill" :class="'role-' + m.role">
                  {{ $t('household.roles.' + m.role) }}
                </span>
              </div>
            </div>
            <!-- Kick: admin can kick member/restricted; owner can kick all except self -->
            <button
              v-if="m.id !== auth.user?.id && hh.myRank > (hh.ROLE_RANK[m.role] || 0) && hh.myRank >= hh.ROLE_RANK.admin"
              class="del-btn"
              @click="kickMember(m)"
              :aria-label="$t('global.delete')"
            >
              <AppIcon :d="I.trash" :size="14" />
            </button>
          </div>
        </div>
      </section>

      <!-- Danger zone — owner only -->
      <section v-if="hh.myRole === 'owner'" class="card danger-card">
        <h3 class="section-title danger-title">{{ $t('household.settings.dangerZone') }}</h3>
        <p class="section-hint">{{ $t('household.settings.dangerDesc') }}</p>
        <div class="danger-row">
          <div>
            <div class="danger-label">{{ $t('household.settings.deleteHousehold') }}</div>
            <div class="danger-hint">This action cannot be undone.</div>
          </div>
          <AppButton variant="danger" size="sm" @click="confirmDelete">
            <AppIcon :d="I.trash" :size="14" /> {{ $t('household.settings.deleteHousehold') }}
          </AppButton>
        </div>
      </section>
    </div>

    <!-- Role picker modal -->
    <teleport to="body">
      <div v-if="rolePickerMember" class="modal-overlay" @click.self="rolePickerMember = null">
        <div class="modal">
          <h3>{{ $t('household.settings.changeRole') }}</h3>
          <p class="modal-sub">{{ rolePickerMember.display_name || rolePickerMember.username }}</p>
          <div class="role-options">
            <button
              v-for="role in ALL_ROLES"
              :key="role"
              class="role-option"
              :class="{ active: rolePickerMember.role === role }"
              @click="applyRole(rolePickerMember, role)"
            >
              <span class="role-pill" :class="'role-' + role">{{ $t('household.roles.' + role) }}</span>
              <span class="role-desc">{{ roleDesc(role) }}</span>
              <AppIcon v-if="rolePickerMember.role === role" :d="I.check" :size="14" class="role-check" />
            </button>
          </div>
          <div class="modal-actions">
            <AppButton variant="outline" size="sm" @click="rolePickerMember = null">{{ $t('global.cancel') }}</AppButton>
          </div>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useAuthStore, avatarColor } from '../stores/auth'
import { useHouseholdStore } from '../stores/household'
import { api } from '../stores/api'
import Avatar from '../components/Avatar.vue'
import Pill from '../components/Pill.vue'
import Field from '../components/Field.vue'
import AppButton from '../components/AppButton.vue'
import AppIcon from '../components/AppIcon.vue'
import ToggleRow from '../components/ToggleRow.vue'
import { I } from '../components/icons.js'

const { t } = useI18n()
const router = useRouter()
const auth = useAuthStore()
const hh   = useHouseholdStore()

const ALL_ROLES = ['admin', 'member', 'restricted']

const name           = ref('')
const isPublic       = ref(false)
const inviteCode     = ref('')
const members        = ref([])
const loadingMembers = ref(true)
const error          = ref('')
const nameSaved      = ref(false)
const codeCopied     = ref(false)
const regenLoading   = ref(false)
const rolePickerMember = ref(null)

const PALETTE = ['#c79bff','#ffb86b','#7cf2a0','#9bd9ff','#ff9ec7','#ffd166']
const hhColor = computed(() => {
  const id = hh.current?.id || 1
  return PALETTE[(id - 1) % PALETTE.length]
})

function roleDesc(role) {
  const map = {
    owner:      t('household.roles.ownerDesc', 'Full control — rename, delete, manage roles'),
    admin:      t('household.roles.adminDesc', 'Kick members, edit & delete recipes'),
    member:     t('household.roles.memberDesc', 'Edit recipes'),
    restricted: t('household.roles.restrictedDesc', 'View only'),
  }
  return map[role] || ''
}

onMounted(async () => {
  if (!hh.current) { router.replace('/shopping'); return }
  name.value       = hh.current.name
  isPublic.value   = hh.current.is_public
  inviteCode.value = hh.current.invite_code || ''
  try {
    members.value = await api(`/households/${hh.current.id}/members`)
  } catch(e) { error.value = e.message }
  finally { loadingMembers.value = false }
})

async function saveName() {
  const n = name.value.trim()
  if (!n) return
  try {
    await hh.updateHousehold(hh.current.id, { name: n })
    nameSaved.value = true
    setTimeout(() => nameSaved.value = false, 2000)
  } catch(e) { error.value = e.message }
}

async function togglePublic(val) {
  isPublic.value = val
  try {
    await hh.updateHousehold(hh.current.id, { is_public: val })
  } catch(e) { error.value = e.message; isPublic.value = !val }
}

function copyCode() {
  navigator.clipboard.writeText(inviteCode.value)
  codeCopied.value = true
  setTimeout(() => codeCopied.value = false, 2000)
}

async function regenCode() {
  if (!confirm(t('household.settings.regenerateConfirm'))) return
  regenLoading.value = true
  try {
    const res = await api(`/households/${hh.current.id}/regenerate-code`, 'POST')
    inviteCode.value = res.invite_code
    await hh.load()
  } catch(e) { error.value = e.message }
  finally { regenLoading.value = false }
}

async function kickMember(member) {
  if (!confirm(t('household.settings.kickConfirm', { name: member.username }))) return
  try {
    await hh.removeMember(hh.current.id, member.id)
    members.value = members.value.filter(m => m.id !== member.id)
  } catch(e) { error.value = e.message }
}

function openRolePicker(member) {
  rolePickerMember.value = { ...member }
}

async function applyRole(member, role) {
  if (member.role === role) { rolePickerMember.value = null; return }
  try {
    await hh.setMemberRole(hh.current.id, member.id, role)
    const m = members.value.find(x => x.id === member.id)
    if (m) m.role = role
    rolePickerMember.value = null
  } catch(e) { error.value = e.message }
}

async function confirmDelete() {
  if (!confirm(t('household.settings.deleteConfirm', { name: hh.current.name }))) return
  try {
    await hh.deleteHousehold(hh.current.id)
    router.replace('/shopping')
  } catch(e) { error.value = e.message }
}
</script>

<style scoped>
.hh-settings-view { display: flex; flex-direction: column; min-height: 100%; }

.topbar {
  padding: 18px 32px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.topbar-mono { font-family: var(--font-mono); font-size: 10px; font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase; color: var(--text-mute); }
.topbar-title-row { display: flex; align-items: center; gap: 10px; margin-top: 6px; }
.page-title { font-size: 22px; font-weight: 600; letter-spacing: -0.4px; }

.close-btn {
  width: 36px; height: 36px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  color: var(--text-dim); transition: background 0.15s, color 0.15s;
  flex-shrink: 0;
}
.close-btn:hover { background: var(--surface-hi); color: var(--text); }

.content { padding: 28px 32px; max-width: 760px; width: 100%; margin: 0 auto; display: flex; flex-direction: column; gap: 24px; box-sizing: border-box; }
.mono { font-family: var(--font-mono); font-size: 10px; font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase; color: var(--text-mute); }

.card { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 20px; display: flex; flex-direction: column; gap: 12px; }
.section-title { font-size: 16px; font-weight: 600; letter-spacing: -0.2px; }
.section-hint { font-size: 13px; color: var(--text-dim); }
.card-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.saved-msg { font-size: 13px; color: var(--success); }
.loading-hint { font-size: 13px; color: var(--text-mute); }

.field-row { display: flex; align-items: flex-end; gap: 12px; }
.field-row > :first-child { flex: 1; }

.code-display {
  background: var(--bg); border: 1px solid var(--border); border-radius: 12px;
  padding: 12px 16px; display: flex; align-items: center; gap: 12px;
}
.code-val {
  font-family: var(--font-mono); font-size: 15px; font-weight: 600;
  letter-spacing: 2px; color: var(--accent); flex: 1;
}

.member-list { background: var(--bg); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
.member-row { display: flex; align-items: center; gap: 12px; padding: 12px 16px; }
.member-row.divide { border-top: 1px solid var(--border); }
.member-info { flex: 1; min-width: 0; }
.member-name-row { display: flex; align-items: center; gap: 8px; }
.member-name { font-size: 14px; font-weight: 500; color: var(--text); }
.self-label { font-size: 12px; color: var(--text-dim); }
.member-meta { display: flex; align-items: center; gap: 8px; margin-top: 3px; }

/* Role pills */
.role-pill {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 2px 8px; border-radius: 999px;
  font-family: var(--font-mono); font-size: 10px; font-weight: 600;
  letter-spacing: 0.3px; text-transform: uppercase;
}
.role-owner     { background: rgba(255, 184, 107, 0.15); color: var(--amber); }
.role-admin     { background: var(--accent-dim); color: var(--accent); }
.role-member    { background: var(--surface-hi); color: var(--text-dim); }
.role-restricted{ background: var(--danger-bg); color: var(--danger); }

.role-pill-btn {
  cursor: pointer; border: 1px solid transparent;
  transition: border-color 0.15s, opacity 0.15s;
}
.role-pill-btn:hover { opacity: 0.8; border-color: currentColor; }

.del-btn { width: 28px; height: 28px; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: var(--text-mute); cursor: pointer; transition: all 0.15s; }
.del-btn:hover { background: var(--danger-bg); color: var(--danger); }

.danger-card { border-color: rgba(255, 122, 122, 0.2); }
.danger-title { color: var(--danger); }
.danger-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; background: var(--bg); border: 1px solid var(--border); border-radius: 12px; padding: 14px 16px; }
.danger-label { font-size: 14px; font-weight: 500; color: var(--text); }
.danger-hint { font-size: 12px; color: var(--text-mute); margin-top: 2px; }

.error-msg { padding: 10px 14px; border-radius: 10px; background: var(--danger-bg); border: 1px solid rgba(255,122,122,0.25); color: var(--danger); font-size: 13px; }

/* Role picker modal */
.modal-overlay {
  position: fixed; inset: 0; z-index: 1000;
  background: rgba(0,0,0,0.6);
  display: flex; align-items: center; justify-content: center;
  padding: 20px;
}
.modal {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 16px; padding: 24px; width: 100%; max-width: 380px;
  display: flex; flex-direction: column; gap: 16px;
}
.modal h3 { font-size: 18px; font-weight: 600; letter-spacing: -0.3px; }
.modal-sub { font-size: 13px; color: var(--text-dim); margin-top: -8px; }
.modal-actions { display: flex; gap: 10px; justify-content: flex-end; }

.role-options { display: flex; flex-direction: column; gap: 6px; }
.role-option {
  display: flex; align-items: center; gap: 12px;
  padding: 11px 14px; border-radius: 10px;
  background: var(--bg); border: 1.5px solid var(--border);
  cursor: pointer; text-align: left;
  transition: border-color 0.15s;
}
.role-option:hover { border-color: var(--border-hi); }
.role-option.active { border-color: var(--accent); background: var(--accent-dim); }
.role-desc { flex: 1; font-size: 12px; color: var(--text-dim); }
.role-check { color: var(--accent); flex-shrink: 0; }

@media (max-width: 768px) { .topbar, .content { padding-left: 20px; padding-right: 20px; } .field-row { flex-direction: column; align-items: stretch; } }


</style>
