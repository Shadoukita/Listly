<template>
  <div class="settings-view">
    <div class="topbar">
      <div class="mono">Settings</div>
      <h1 class="page-title">Your preferences.</h1>
    </div>

    <div class="content">
      <!-- Appearance -->
      <section class="card">
        <h3 class="section-title">Appearance</h3>
        <ToggleRow :icon="I.moon" :label="$t('settings.darkMode')" hint="Synced across devices" :on="auth.user?.darkmode ?? true" @change="toggleDark" />
        <div class="select-row">
          <div class="row-icon"><AppIcon :d="I.globe" :size="16" /></div>
          <div class="row-body">
            <div class="row-label">{{ $t('settings.language') }}</div>
          </div>
          <div class="lang-btns">
            <button v-for="loc in SUPPORTED_LOCALES" :key="loc.code" class="lang-btn" :class="{ active: currentLocale === loc.code }" @click="changeLocale(loc.code)">
              {{ loc.name }}
            </button>
          </div>
        </div>
      </section>

      <!-- My modules -->
      <section class="card">
        <h3 class="section-title">{{ $t('settings.modules') }}</h3>
        <p class="section-hint">{{ $t('settings.modulesDesc') }}</p>
        <template v-for="mod in MODULES" :key="mod.id">
          <ToggleRow
            v-if="auth.globalModules[mod.id]"
            :icon="I[mod.icon]"
            :label="$t('modules.' + mod.id)"
            :on="auth.userModules[mod.id]"
            @change="toggleModule(mod.id, $event)"
          />
        </template>
        <p v-if="!MODULES.some(m => auth.globalModules[m.id])" class="no-modules">{{ $t('settings.noModules') }}</p>
      </section>

      <!-- Admin hint -->
      <div class="admin-hint">
        <AppIcon :d="I.shield" :size="16" />
        <div>
          Need a module that's not listed? Ask your instance admin to enable it under
          <span class="hint-highlight">Hosted modules</span>.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore, MODULES } from '../stores/auth'
import { setLocale, SUPPORTED_LOCALES } from '../plugins/i18n'
import AppIcon from '../components/AppIcon.vue'
import { I } from '../components/icons.js'
import ToggleRow from '../components/ToggleRow.vue'

const { locale } = useI18n()
const auth = useAuthStore()
const currentLocale = ref(locale.value)

async function toggleDark(val) { await auth.setDarkmode(val) }
async function toggleModule(id, val) { await auth.setModule(id, val) }

function changeLocale(code) { setLocale(code); currentLocale.value = code }
</script>

<style scoped>
.settings-view { display: flex; flex-direction: column; min-height: 100%; }
.topbar { padding: 18px 32px; border-bottom: 1px solid var(--border); }
.page-title { font-size: 22px; font-weight: 600; letter-spacing: -0.4px; margin-top: 4px; }
.content { padding: 28px 32px; max-width: 760px; width: 100%; margin: 0 auto; display: flex; flex-direction: column; gap: 28px; box-sizing: border-box; }
.mono { font-family: var(--font-mono); font-size: 10px; font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase; color: var(--text-mute); }

.card { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 20px; display: flex; flex-direction: column; gap: 8px; }
.section-title { font-size: 16px; font-weight: 600; letter-spacing: -0.2px; margin-bottom: 6px; }
.section-hint { font-size: 13px; color: var(--text-dim); margin-bottom: 4px; }
.no-modules { font-size: 13px; color: var(--text-mute); }

.select-row { background: var(--bg); border: 1px solid var(--border); border-radius: 12px; padding: 14px 16px; display: flex; align-items: center; gap: 14px; }
.row-icon { width: 32px; height: 32px; border-radius: 8px; background: var(--surface-hi); color: var(--text-dim); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.row-body { flex: 1; }
.row-label { font-size: 14px; font-weight: 500; }
.lang-btns { display: flex; gap: 6px; }
.lang-btn { padding: 5px 11px; border-radius: var(--r-pill); border: 1px solid var(--border); background: var(--surface); color: var(--text-dim); font-size: 12px; font-weight: 500; cursor: pointer; transition: all 0.15s; }
.lang-btn.active { background: var(--accent-dim); border-color: transparent; color: var(--accent); }

.admin-hint { padding: 16px 18px; border-radius: 12px; background: var(--surface); border: 1px dashed var(--border-hi); display: flex; align-items: center; gap: 12px; color: var(--text-dim); font-size: 13px; line-height: 1.5; }
.hint-highlight { color: var(--text); }

@media (max-width: 768px) { .topbar, .content { padding-left: 20px; padding-right: 20px; } }
</style>
