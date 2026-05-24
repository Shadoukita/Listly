<template>
  <AuthShell>
    <div class="setup-form">
      <Pill tone="amber">{{ $t('setup.firstSetup') || 'First-time setup' }}</Pill>
      <h2 class="setup-title">{{ $t('setup.title') || 'Set up your Listly instance.' }}</h2>
      <p class="setup-sub">{{ $t('setup.titleDesc') || "You're the first user. Create the admin account, then optionally set an endpoint for invite links." }}</p>

      <!-- Step indicator -->
      <div class="steps">
        <div class="step-dot" :class="{ active: step === 0, done: step > 0 }">
          <span>1</span>
        </div>
        <div class="step-line" />
        <div class="step-dot" :class="{ active: step === 1 }">
          <span>2</span>
        </div>
      </div>

      <div v-if="error" class="error-msg">{{ error }}</div>

      <!-- Step 0: Admin account -->
      <div v-if="step === 0" class="step-fields">
        <Field v-model="username" :label="$t('setup.adminAccount')" placeholder="admin" @keydown.enter="next" />
        <Field v-model="password" :label="$t('auth.password')" :placeholder="$t('auth.passwordMin')" type="password" @keydown.enter="next" />
        <Field v-model="password2" :label="$t('auth.confirmPassword')" :placeholder="$t('auth.passwordRepeat')" type="password" @keydown.enter="next" />

        <div class="setup-notice">
          <AppIcon :d="I.shield" :size="14" />
          <span>This account becomes the instance administrator. It can manage users, modules, and the endpoint URL.</span>
        </div>
      </div>

      <!-- Step 1: Endpoint URL -->
      <div v-if="step === 1" class="step-fields">
        <Field v-model="endpointUrl" :label="$t('setup.endpointUrl')" :placeholder="$t('setup.endpointPlaceholder')" type="url" :mono="true" @keydown.enter="next" />
        <p class="field-hint">{{ $t('setup.endpointHint') }}</p>
      </div>

      <div class="setup-actions">
        <AppButton v-if="step === 1" variant="outline" @click="next">{{ $t('setup.skip') || 'Skip endpoint' }}</AppButton>
        <div style="flex:1" />
        <AppButton v-if="step > 0" variant="outline" @click="step--">{{ $t('global.back') }}</AppButton>
        <AppButton @click="next" :disabled="loading">
          <AppIcon :d="I.chevR" :size="16" :sw="2" />
          {{ step === 1 ? $t('global.finish') : $t('global.next') }}
        </AppButton>
      </div>
    </div>
  </AuthShell>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
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
const auth   = useAuthStore()

const step       = ref(0)
const username   = ref('')
const password   = ref('')
const password2  = ref('')
const endpointUrl = ref('')
const error      = ref('')
const loading    = ref(false)

async function next() {
  error.value = ''
  if (step.value === 0) {
    if (!username.value || !password.value) { error.value = t('setup.errors.credentialsRequired'); return }
    if (password.value.length < 6)          { error.value = t('setup.errors.passwordTooShort'); return }
    if (password.value !== password2.value)  { error.value = t('setup.errors.passwordMismatch'); return }
    step.value = 1
  } else {
    loading.value = true
    try {
      const data = await api('/setup', 'POST', {
        username: username.value,
        password: password.value,
        endpoint_url: endpointUrl.value,
      })
      auth.setAuth(data.token, data.user)
      window.location.replace('/')
    } catch(e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }
}
</script>

<style scoped>
.setup-form {
  width: 100%;
  max-width: 460px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.setup-title {
  font-size: 28px;
  font-weight: 600;
  letter-spacing: -0.6px;
  line-height: 1.15;
  margin-top: 4px;
}
.setup-sub { font-size: 14px; color: var(--text-dim); line-height: 1.5; }

.steps {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}
.step-dot {
  width: 22px; height: 22px; border-radius: 50%;
  background: var(--surface-hi);
  border: 1px solid var(--border);
  color: var(--text-dim);
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 600; font-family: var(--font-mono);
  transition: background 0.2s, border-color 0.2s, color 0.2s;
}
.step-dot.active { background: var(--accent); border-color: var(--accent); color: var(--accent-ink); }
.step-dot.done   { background: var(--accent-dim); border-color: transparent; color: var(--accent); }
.step-line { flex: 1; height: 1px; background: var(--border); }

.step-fields { display: flex; flex-direction: column; gap: 10px; }

.setup-notice {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 14px;
  border-radius: 10px;
  background: rgba(255,194,107,0.05);
  border: 1px solid rgba(255,194,107,0.18);
  color: var(--amber);
  font-size: 12px;
  line-height: 1.5;
}
.setup-notice svg { flex-shrink: 0; margin-top: 1px; }

.field-hint { font-size: 12px; color: var(--text-mute); font-family: var(--font-mono); }

.setup-actions { display: flex; gap: 10px; align-items: center; margin-top: 6px; }

.error-msg {
  padding: 10px 14px;
  border-radius: 10px;
  background: var(--danger-bg);
  border: 1px solid rgba(255,122,122,0.25);
  color: var(--danger);
  font-size: 13px;
}
</style>
