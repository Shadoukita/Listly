import { createI18n } from 'vue-i18n'
import enUS from '../lang/en-US.json'
import deDE from '../lang/de-DE.json'

export const SUPPORTED_LOCALES = [
  { code: 'en-US', name: 'English' },
  { code: 'de-DE', name: 'Deutsch' },
]

const SUPPORTED_CODES = SUPPORTED_LOCALES.map(l => l.code)

function detectLocale() {
  // 1. User's explicit choice persisted in localStorage
  const saved = localStorage.getItem('locale')
  if (saved && SUPPORTED_CODES.includes(saved)) return saved

  // 2. Browser language (e.g. "de-DE", "de", "en-US")
  for (const lang of navigator.languages ?? [navigator.language]) {
    if (SUPPORTED_CODES.includes(lang)) return lang
    // Try matching just the base language (e.g. "de" → "de-DE")
    const base = lang.split('-')[0]
    const match = SUPPORTED_CODES.find(c => c.startsWith(base + '-'))
    if (match) return match
  }

  return 'en-US'
}

const initialLocale = detectLocale()

export const i18n = createI18n({
  legacy: false,
  locale: initialLocale,
  fallbackLocale: 'en-US',
  messages: { 'en-US': enUS, 'de-DE': deDE },
})

export function setLocale(code) {
  i18n.global.locale.value = code
  localStorage.setItem('locale', code)
  document.documentElement.setAttribute('lang', code.split('-')[0])
}

// Apply lang attribute immediately on load
document.documentElement.setAttribute('lang', initialLocale.split('-')[0])
