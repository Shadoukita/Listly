import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from './api'

export const MODULES = [
  { id: 'shopping',    label: 'Shopping list', icon: 'cart'     },
  { id: 'recipes',     label: 'Recipes',       icon: 'chef'     },
  { id: 'mealplanner', label: 'Meal planner',  icon: 'calendar' },
  { id: 'storage',     label: 'Storage',       icon: 'box'      },
]

function defaultModuleData() {
  return Object.fromEntries(MODULES.map(m => [m.id, { global: true, user: true, effective: true }]))
}

export function avatarColor(userId) {
  const colors = ['#c79bff','#ffb86b','#7cf2a0','#9bd9ff','#ff9ec7','#ffd166']
  return colors[((userId || 0) - 1) % colors.length]
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const _moduleData = ref(JSON.parse(localStorage.getItem('moduleData') || 'null') || defaultModuleData())

  const isLoggedIn = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  const modules = computed(() =>
    Object.fromEntries(MODULES.map(m => [m.id, _moduleData.value[m.id]?.effective ?? true]))
  )
  const userModules = computed(() =>
    Object.fromEntries(MODULES.map(m => [m.id, _moduleData.value[m.id]?.user ?? true]))
  )
  const globalModules = computed(() =>
    Object.fromEntries(MODULES.map(m => [m.id, _moduleData.value[m.id]?.global ?? true]))
  )

  function _saveModuleData(data) {
    _moduleData.value = data
    localStorage.setItem('moduleData', JSON.stringify(data))
  }

  function setAuth(t, u) {
    token.value = t; user.value = u
    localStorage.setItem('token', t)
    localStorage.setItem('user', JSON.stringify(u))
  }

  function logout() {
    token.value = null; user.value = null
    _moduleData.value = defaultModuleData()
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('moduleData')
  }

  async function fetchMe() {
    const me = await api('/me')
    user.value = me
    localStorage.setItem('user', JSON.stringify(me))
  }

  async function fetchModules() {
    const data = await api('/me/modules')
    _saveModuleData(data)
  }

  async function setModule(id, enabled) {
    const data = await api('/me/modules', 'PUT', { [id]: enabled })
    _saveModuleData(data)
  }

  async function setGlobalModule(id, enabled) {
    const data = await api('/modules', 'PUT', { [id]: enabled })
    _saveModuleData(data)
  }

  async function setDarkmode(dm) {
    await api('/me/darkmode', 'PUT', { darkmode: dm })
    user.value = { ...user.value, darkmode: dm }
    localStorage.setItem('user', JSON.stringify(user.value))
  }

  async function updateProfile(data) {
    const updated = await api('/me/profile', 'PUT', data)
    user.value = updated
    localStorage.setItem('user', JSON.stringify(updated))
    return updated
  }

  return {
    token, user, isLoggedIn, isAdmin,
    modules, userModules, globalModules,
    setAuth, logout, fetchMe, fetchModules,
    setModule, setGlobalModule, setDarkmode, updateProfile,
  }
})
