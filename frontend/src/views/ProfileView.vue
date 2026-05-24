<template>
  <div class="profile-view">
    <div class="topbar">
      <div class="mono">Profile</div>
      <h1 class="page-title">Your account.</h1>
    </div>

    <div class="content">
      <!-- Header card -->
      <div class="profile-card">
        <label
          class="avatar-upload"
          @mouseenter="avatarHover = true"
          @mouseleave="avatarHover = false"
          title="Change photo"
        >
          <Avatar :name="auth.user?.display_name || auth.user?.username" :src="profileImage || ''" :color="userColor" :size="68" />
          <div v-if="avatarUploading" class="avatar-dim">
            <svg class="spin" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>
          </div>
          <div v-else-if="avatarHover" class="avatar-dim">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/>
              <line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
          </div>
          <input type="file" accept="image/*" @change="onAvatarChange" hidden />
        </label>
        <div class="profile-info">
          <div class="profile-name-row">
            <h2 class="profile-name">{{ auth.user?.display_name || auth.user?.username }}</h2>
            <Pill v-if="auth.isAdmin" tone="accent">Admin</Pill>
          </div>
          <div class="mono">@{{ auth.user?.username }} · joined {{ joinDate }}</div>
        </div>
      </div>

      <!-- Display name -->
      <section class="card">
        <div class="card-header">
          <h3>Display name</h3>
          <p class="card-hint">{{ $t('profile.displayNameDesc') }}</p>
        </div>
        <div v-if="nameError" class="error-msg">{{ nameError }}</div>
        <Field v-model="displayName" :label="$t('profile.displayNameLabel')" :placeholder="auth.user?.username" @keydown.enter="saveName" />
        <div class="card-actions">
          <span v-if="nameSaved" class="saved-msg">{{ $t('profile.changed') }}</span>
          <AppButton variant="outline" size="sm" @click="saveName">{{ $t('global.save') }}</AppButton>
        </div>
      </section>

      <!-- Change password -->
      <section class="card">
        <div class="card-header">
          <h3>{{ $t('profile.changePassword') }}</h3>
        </div>
        <div v-if="pwError" class="error-msg">{{ pwError }}</div>
        <div class="fields">
          <Field v-model="currentPw" :label="$t('profile.currentPassword')" placeholder="••••••••" type="password" @keydown.enter="changePassword" />
          <Field v-model="newPw" :label="$t('profile.newPassword')" :placeholder="$t('auth.passwordMin')" type="password" @keydown.enter="changePassword" />
          <Field v-model="newPw2" :label="$t('profile.confirmNewPassword')" :placeholder="$t('auth.passwordRepeat')" type="password" @keydown.enter="changePassword" />
        </div>
        <div class="card-actions">
          <span v-if="pwSaved" class="saved-msg">{{ $t('profile.changed') }}</span>
          <AppButton size="sm" @click="changePassword">{{ $t('profile.changePasswordBtn') }}</AppButton>
        </div>
      </section>

      <!-- Account info -->
      <section class="card">
        <div class="card-header"><h3>{{ $t('profile.accountInfo') }}</h3></div>
        <div class="info-table">
          <div class="info-row">
            <span class="mono">{{ $t('profile.username') }}</span>
            <span class="info-value mono-val">{{ auth.user?.username }}</span>
          </div>
          <div class="info-row">
            <span class="mono">{{ $t('profile.role') }}</span>
            <Pill :tone="auth.isAdmin ? 'accent' : 'neutral'">{{ auth.user?.role }}</Pill>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore, avatarColor } from '../stores/auth'
import Avatar from '../components/Avatar.vue'
import Pill from '../components/Pill.vue'
import Field from '../components/Field.vue'
import AppButton from '../components/AppButton.vue'

const { t } = useI18n()
const auth  = useAuthStore()

const profileImage    = ref('')
const avatarUploading = ref(false)
const avatarHover     = ref(false)
const displayName = ref('')
const nameError   = ref('')
const nameSaved   = ref(false)
const currentPw   = ref('')
const newPw       = ref('')
const newPw2      = ref('')
const pwError     = ref('')
const pwSaved     = ref(false)

const userColor = computed(() => avatarColor(auth.user?.id))
const joinDate  = computed(() => {
  if (!auth.user?.created_at) return ''
  return new Date(auth.user.created_at).toLocaleDateString(undefined, { month: 'long', day: 'numeric', year: 'numeric' })
})

onMounted(() => {
  displayName.value  = auth.user?.display_name || ''
  profileImage.value = auth.user?.profile_image || ''
})

async function onAvatarChange(e) {
  const file = e.target.files[0]
  if (!file) return
  avatarUploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)
    fd.append('type', 'user')
    fd.append('id', String(auth.user.id))
    const token = localStorage.getItem('token')
    const res = await fetch('/api/upload', {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: fd,
    })
    const data = await res.json()
    if (data.url) {
      profileImage.value = data.url
      await auth.updateProfile({ profile_image: data.url })
    }
  } catch(err) {
    console.error('Avatar upload failed', err)
  } finally {
    avatarUploading.value = false
    e.target.value = ''
  }
}

async function saveName() {
  nameError.value = ''
  const name = displayName.value.trim()
  if (!name) { nameError.value = t('profile.errors.displayNameEmpty'); return }
  try {
    await auth.updateProfile({ display_name: name })
    nameSaved.value = true
    setTimeout(() => nameSaved.value = false, 2000)
  } catch(e) { nameError.value = e.message }
}

async function changePassword() {
  pwError.value = ''
  if (!currentPw.value)         { pwError.value = t('profile.errors.currentPasswordRequired'); return }
  if (!newPw.value)             { pwError.value = t('profile.errors.newPasswordRequired'); return }
  if (newPw.value.length < 6)   { pwError.value = t('profile.errors.passwordTooShort'); return }
  if (newPw.value !== newPw2.value) { pwError.value = t('profile.errors.passwordMismatch'); return }
  try {
    await auth.updateProfile({ current_password: currentPw.value, new_password: newPw.value })
    currentPw.value = ''; newPw.value = ''; newPw2.value = ''
    pwSaved.value = true
    setTimeout(() => pwSaved.value = false, 2000)
  } catch(e) { pwError.value = e.message }
}
</script>

<style scoped>
.profile-view { display: flex; flex-direction: column; min-height: 100%; }
.topbar { padding: 18px 32px; border-bottom: 1px solid var(--border); }
.page-title { font-size: 22px; font-weight: 600; letter-spacing: -0.4px; margin-top: 4px; }
.content { padding: 28px 32px; max-width: 720px; width: 100%; margin: 0 auto; display: flex; flex-direction: column; gap: 28px; box-sizing: border-box; }
.mono { font-family: var(--font-mono); font-size: 10px; font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase; color: var(--text-mute); }

.profile-card { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 22px; display: flex; align-items: center; gap: 18px; }

.avatar-upload {
  position: relative;
  width: 68px;
  height: 68px;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
  flex-shrink: 0;
  display: block;
}
.avatar-dim {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.48);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  pointer-events: none;
}
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.profile-info { flex: 1; min-width: 0; }
.profile-name-row { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
.profile-name { font-size: 22px; font-weight: 600; letter-spacing: -0.4px; }

.card { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 20px; display: flex; flex-direction: column; gap: 14px; }
.card-header h3 { font-size: 16px; font-weight: 600; letter-spacing: -0.2px; }
.card-hint { font-size: 13px; color: var(--text-dim); margin-top: 4px; }
.card-actions { display: flex; align-items: center; justify-content: flex-end; gap: 12px; }
.saved-msg { font-size: 13px; color: var(--success); }
.fields { display: flex; flex-direction: column; gap: 10px; }

.info-table { background: var(--bg); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
.info-row { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; border-bottom: 1px solid var(--border); }
.info-row:last-child { border-bottom: none; }
.info-value { font-size: 14px; color: var(--text); }
.mono-val { font-family: var(--font-mono); font-size: 13px; text-transform: none; letter-spacing: 0; color: var(--text); }

.error-msg { padding: 10px 14px; border-radius: 10px; background: var(--danger-bg); border: 1px solid rgba(255,122,122,0.25); color: var(--danger); font-size: 13px; }

@media (max-width: 768px) { .topbar, .content { padding-left: 20px; padding-right: 20px; } }
</style>
