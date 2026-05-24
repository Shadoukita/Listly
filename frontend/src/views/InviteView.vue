<template>
  <AuthShell>
    <div class="invite-form">
      <Pill tone="accent">{{ $t('invite.title') }}</Pill>
      <h2 class="invite-title">{{ $t('invite.subtitle') }}</h2>

      <div v-if="checking" class="invite-loading">{{ $t('global.loading') }}</div>
      <div v-else-if="!valid" class="error-msg">{{ $t('auth.errors.invalidCode') }}</div>
      <template v-else>
        <div class="token-valid">
          <AppIcon :d="I.check" :size="14" :sw="3" /> Valid invite
        </div>
        <div v-if="error" class="error-msg">{{ error }}</div>
        <div class="fields">
          <Field v-model="regUsername" :label="$t('auth.username')" :placeholder="$t('auth.username')" autocomplete="username" @keydown.enter="register" />
          <Field v-model="regPassword" :label="$t('auth.password')" :placeholder="$t('auth.passwordMin')" type="password" autocomplete="new-password" @keydown.enter="register" />
          <Field v-model="regPassword2" :label="$t('auth.confirmPassword')" :placeholder="$t('auth.passwordRepeat')" type="password" autocomplete="new-password" @keydown.enter="register" />
        </div>
        <AppButton :full="true" :disabled="loading" @click="register">{{ $t('auth.createAccount') }}</AppButton>
      </template>
    </div>
  </AuthShell>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'
import { api } from '../stores/api'
import AuthShell from '../components/AuthShell.vue'
import Pill from '../components/Pill.vue'
import Field from '../components/Field.vue'
import AppButton from '../components/AppButton.vue'
import AppIcon from '../components/AppIcon.vue'
import { I } from '../components/icons.js'

const { t } = useI18n()
const router = useRouter()
const route  = useRoute()
const auth   = useAuthStore()

const checking    = ref(true)
const valid       = ref(false)
const loading     = ref(false)
const error       = ref('')
const regUsername = ref('')
const regPassword = ref('')
const regPassword2 = ref('')

const token = route.query.token || new URLSearchParams(window.location.search).get('invite') || ''

onMounted(async () => {
  if (!token) { valid.value = false; checking.value = false; return }
  try {
    const res = await api(`/invite/${token}`)
    valid.value = res.valid
  } catch(e) { valid.value = false }
  finally { checking.value = false }
})

async function register() {
  error.value = ''
  if (!regUsername.value.trim()) { error.value = t('auth.errors.usernameRequired'); return }
  if (!regPassword.value)        { error.value = t('auth.errors.passwordRequired'); return }
  if (regPassword.value.length < 6) { error.value = t('auth.errors.passwordTooShort'); return }
  if (regPassword.value !== regPassword2.value) { error.value = t('auth.errors.passwordMismatch'); return }
  loading.value = true
  try {
    const data = await api(`/invite/${token}/register`, 'POST', {
      username: regUsername.value.trim(), password: regPassword.value,
    })
    auth.setAuth(data.token, data.user)
    router.push('/')
  } catch(e) { error.value = e.message }
  finally { loading.value = false }
}
</script>

<style scoped>
.invite-form { width: 100%; max-width: 420px; display: flex; flex-direction: column; gap: 20px; }
.invite-title { font-size: 26px; font-weight: 600; letter-spacing: -0.6px; }
.invite-loading { color: var(--text-dim); font-size: 14px; }
.fields { display: flex; flex-direction: column; gap: 10px; }
.token-valid {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 14px; border-radius: 10px;
  background: var(--accent-dim); color: var(--accent); font-size: 13px;
}
.error-msg {
  padding: 10px 14px; border-radius: 10px;
  background: var(--danger-bg); border: 1px solid rgba(255,122,122,0.25);
  color: var(--danger); font-size: 13px;
}
</style>
