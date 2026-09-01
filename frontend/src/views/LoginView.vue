<template>
  <AuthShell>
    <div class="login-form">
      <!-- Tabs -->
      <div class="tabs">
        <button class="tab" :class="{ active: tab === 'login' }" @click="switchTab('login')">{{ $t('auth.signIn') }}</button>
        <button class="tab" :class="{ active: tab === 'register' }" @click="switchTab('register')">{{ $t('auth.register') }}</button>
      </div>

      <h2 class="form-title">{{ tab === 'login' ? 'Welcome back.' : 'Create your account.' }}</h2>
      <p class="form-sub">
        {{ tab === 'login'
          ? 'Sign in to sync lists across your households.'
          : "You'll need an invite link from your admin to register." }}
      </p>

      <div v-if="error" class="error-msg">{{ error }}</div>

      <!-- Login -->
      <template v-if="tab === 'login'">
        <div class="fields">
          <Field v-model="username" :label="$t('auth.username')" :placeholder="$t('auth.username')" autocomplete="username" @keydown.enter="login" />
          <Field v-model="password" :label="$t('auth.password')" placeholder="••••••••" type="password" autocomplete="current-password" @keydown.enter="login" />
          <label class="remember">
            <div class="check-box" :class="{ checked: remember }">
              <AppIcon v-if="remember" :d="I.check" :size="11" :sw="3.5" />
            </div>
            <input type="checkbox" v-model="remember" hidden />
            {{ $t('auth.stayLoggedIn') }} (30 days)
          </label>
        </div>
        <AppButton :full="true" :disabled="loading" @click="login">{{ $t('auth.signIn') }}</AppButton>
      </template>

      <!-- Register — step 0: invite token -->
      <template v-else-if="regStep === 0">
        <div class="fields">
          <Field v-model="inviteToken" :label="$t('auth.inviteCode')" :placeholder="$t('auth.enterInviteCodePlaceholder')" :mono="true" @keydown.enter="validateToken" />
          <div v-if="tokenValid" class="token-valid">
            <AppIcon :d="I.check" :size="14" :sw="3" /> Valid invite
          </div>
        </div>
        <AppButton :full="true" :disabled="validating" @click="validateToken">
          {{ validating ? $t('auth.validating') : $t('global.next') }}
        </AppButton>
      </template>

      <!-- Register — step 1: account details -->
      <template v-else>
        <div class="fields">
          <Field v-model="inviteToken" :label="$t('auth.inviteCode')" :mono="true" disabled />
          <div class="token-valid">
            <AppIcon :d="I.check" :size="14" :sw="3" /> Valid invite
          </div>
          <Field v-model="regUsername" :label="$t('auth.username')" :placeholder="$t('auth.username')" autocomplete="username" @keydown.enter="register" />
          <Field v-model="regPassword" :label="$t('auth.password')" :placeholder="$t('auth.passwordMin')" type="password" autocomplete="new-password" @keydown.enter="register" />
          <Field v-model="regPassword2" :label="$t('auth.confirmPassword')" :placeholder="$t('auth.passwordRepeat')" type="password" autocomplete="new-password" @keydown.enter="register" />
        </div>
        <div class="register-actions">
          <AppButton variant="outline" @click="regStep = 0">{{ $t('global.back') }}</AppButton>
          <AppButton :full="true" :disabled="loading" @click="register">{{ $t('auth.createAccount') }}</AppButton>
        </div>
      </template>
    </div>
  </AuthShell>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { api } from '../stores/api'
import AuthShell from '../components/AuthShell.vue'
import Field from '../components/Field.vue'
import AppButton from '../components/AppButton.vue'
import AppIcon from '../components/AppIcon.vue'
import { I } from '../components/icons.js'

const { t } = useI18n()
const router = useRouter()
const auth   = useAuthStore()

const tab      = ref('login')
const error    = ref('')
const loading  = ref(false)

const username = ref('')
const password = ref('')
const remember = ref(false)

const regStep     = ref(0)
const inviteToken = ref('')
const regUsername = ref('')
const regPassword = ref('')
const regPassword2 = ref('')
const validating  = ref(false)
const tokenValid  = ref(false)

function switchTab(t) {
  tab.value = t; error.value = ''
  regStep.value = 0; inviteToken.value = ''; tokenValid.value = false
  regUsername.value = ''; regPassword.value = ''; regPassword2.value = ''
}

async function login() {
  error.value = ''; loading.value = true
  try {
    const data = await api('/login', 'POST', { username: username.value, password: password.value, remember: remember.value })
    auth.setAuth(data.token, data.user)
    router.push('/')
  } catch(e) { error.value = e.message }
  finally { loading.value = false }
}

async function validateToken() {
  error.value = ''
  const tok = inviteToken.value.trim()
  if (!tok) { error.value = t('auth.errors.enterCode'); return }
  validating.value = true
  try {
    const res = await api(`/invite/${tok}`)
    if (res.valid) { tokenValid.value = true; regStep.value = 1 }
    else error.value = t('auth.errors.invalidCode')
  } catch(e) { error.value = t('auth.errors.invalidCode') }
  finally { validating.value = false }
}

async function register() {
  error.value = ''
  if (!regUsername.value.trim()) { error.value = t('auth.errors.usernameRequired'); return }
  if (!regPassword.value)        { error.value = t('auth.errors.passwordRequired'); return }
  if (regPassword.value.length < 6) { error.value = t('auth.errors.passwordTooShort'); return }
  if (regPassword.value !== regPassword2.value) { error.value = t('auth.errors.passwordMismatch'); return }
  loading.value = true
  try {
    const data = await api(`/invite/${inviteToken.value.trim()}/register`, 'POST', {
      username: regUsername.value.trim(), password: regPassword.value,
    })
    auth.setAuth(data.token, data.user)
    router.push('/')
  } catch(e) { error.value = e.message }
  finally { loading.value = false }
}
</script>

<style scoped>
.login-form { width: 100%; max-width: 420px; display: flex; flex-direction: column; gap: 20px; }

.tabs {
  display: flex; gap: 4px; padding: 4px;
  background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
}
.tab {
  flex: 1; padding: 8px 12px; text-align: center; border-radius: 8px;
  color: var(--text-dim); font-size: 13px; font-weight: 600;
  cursor: pointer; transition: background 0.15s, color 0.15s;
}
.tab.active { background: var(--surface-hi); color: var(--text); }

.form-title { font-size: 26px; font-weight: 600; letter-spacing: -0.6px; }
.form-sub   { font-size: 14px; color: var(--text-dim); margin-top: -10px; }

.fields { display: flex; flex-direction: column; gap: 10px; }

.remember {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; color: var(--text-dim); cursor: pointer;
  margin-top: 6px;
}
.check-box {
  width: 16px; height: 16px; border-radius: 4px;
  background: var(--surface-hi); border: 1px solid var(--border-hi);
  display: inline-flex; align-items: center; justify-content: center;
  color: var(--accent-ink); transition: background 0.15s;
  flex-shrink: 0;
}
.check-box.checked { background: var(--accent); border-color: var(--accent); }

.token-valid {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 14px; border-radius: 10px;
  background: var(--accent-dim); color: var(--accent); font-size: 13px;
}

.register-actions { display: flex; gap: 10px; }
.register-actions .btn { flex: 1; }

.error-msg {
  padding: 10px 14px; border-radius: 10px;
  background: var(--danger-bg); border: 1px solid rgba(255,122,122,0.25);
  color: var(--danger); font-size: 13px;
}
</style>
