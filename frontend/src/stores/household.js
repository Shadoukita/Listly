import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from './api'

export const useHouseholdStore = defineStore('household', () => {
  const households = ref([])
  const current = ref(null)

  async function load() {
    households.value = await api('/households')
  }

  async function select(h, save = true) {
    current.value = h
    if (save && h) {
      try { await api('/me/household', 'PUT', { household_id: h.id }) } catch(e) {}
    }
  }

  async function restore(lastId) {
    if (!current.value && households.value.length > 0) {
      const found = lastId ? households.value.find(h => h.id === lastId) : null
      await select(found || households.value[0], false)
    }
  }

  async function create(name) {
    const h = await api('/households', 'POST', { name })
    await load()
    const full = households.value.find(x => x.id === h.id)
    if (full) await select(full)
    return h
  }

  async function join(code) {
    const res = await api('/households/join', 'POST', { invite_code: code })
    await load()
    const found = households.value.find(h => h.id === res.household_id)
    if (found) await select(found)
    return res
  }

  async function updateHousehold(hid, data) {
    const res = await api(`/households/${hid}`, 'PATCH', data)
    await load()
    if (current.value?.id === hid) {
      const found = households.value.find(h => h.id === hid)
      if (found) current.value = found
    }
    return res
  }

  async function deleteHousehold(hid) {
    await api(`/households/${hid}`, 'DELETE')
    await load()
    if (current.value?.id === hid) {
      current.value = households.value[0] || null
    }
  }

  async function removeMember(hid, uid) {
    await api(`/households/${hid}/members/${uid}`, 'DELETE')
  }

  async function setMemberRole(hid, uid, role) {
    await api(`/households/${hid}/members/${uid}/role`, 'PUT', { role })
  }

  async function loadPublic() {
    return await api('/households/public')
  }

  async function joinPublic(hid) {
    const res = await api(`/households/${hid}/join-public`, 'POST')
    await load()
    const found = households.value.find(h => h.id === hid)
    if (found) await select(found)
    return res
  }

  // Role helpers — read from hh.current which already carries the user's role
  const ROLE_RANK = { owner: 4, admin: 3, member: 2, restricted: 1 }
  const myRole    = computed(() => current.value?.role || null)
  const myRank    = computed(() => ROLE_RANK[myRole.value] || 0)

  return {
    households, current, myRole, myRank, ROLE_RANK,
    load, select, restore, create, join,
    updateHousehold, deleteHousehold, removeMember, setMemberRole, loadPublic, joinPublic,
  }
})
