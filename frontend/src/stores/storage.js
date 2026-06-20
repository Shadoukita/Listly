import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from './api'

export const useStorageStore = defineStore('storage', () => {
  const locations = ref([])
  const items     = ref([])

  async function load(hid) {
    ;[locations.value, items.value] = await Promise.all([
      api(`/households/${hid}/storage/locations`),
      api(`/households/${hid}/storage/items`),
    ])
  }

  // ── Locations (admin only on the backend) ──────────────────────
  async function createLocation(hid, payload) {
    const loc = await api(`/households/${hid}/storage/locations`, 'POST', payload)
    locations.value.push(loc)
    return loc
  }

  async function updateLocation(id, patch) {
    const loc = await api(`/storage/locations/${id}`, 'PATCH', patch)
    const i = locations.value.findIndex(x => x.id === id)
    if (i !== -1) locations.value[i] = loc
    return loc
  }

  async function removeLocation(id) {
    await api(`/storage/locations/${id}`, 'DELETE')
    locations.value = locations.value.filter(x => x.id !== id)
    // Items with this location are cascade-deleted on the server
    items.value = items.value.filter(x => x.location_id !== id)
  }

  // ── Items ──────────────────────────────────────────────────────
  async function createItem(hid, payload) {
    const item = await api(`/households/${hid}/storage/items`, 'POST', payload)
    items.value.push(item)
    return item
  }

  async function updateItem(id, patch) {
    const item = await api(`/storage/items/${id}`, 'PATCH', patch)
    const i = items.value.findIndex(x => x.id === id)
    if (i !== -1) items.value[i] = item
    return item
  }

  async function removeItem(id) {
    await api(`/storage/items/${id}`, 'DELETE')
    items.value = items.value.filter(x => x.id !== id)
  }

  return {
    locations, items, load,
    createLocation, updateLocation, removeLocation,
    createItem, updateItem, removeItem,
  }
})
