import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from './api'

export const useRecipeStore = defineStore('recipes', () => {
  const items    = ref([])   // current household's recipes
  const allItems = ref([])   // all visible recipes (own households + public)
  const current  = ref(null)

  async function load(householdId) {
    items.value = await api(`/households/${householdId}/recipes`)
  }

  async function loadAll() {
    allItems.value = await api('/recipes/all')
  }

  async function get(id) {
    current.value = await api(`/recipes/${id}`)
    return current.value
  }

  async function create(householdId, recipe) {
    const r = await api(`/households/${householdId}/recipes`, 'POST', recipe)
    items.value.unshift(r)
    return r
  }

  async function importFromUrl(url) {
    return await api('/recipes/import', 'POST', { url })
  }

  async function update(id, patch) {
    const r = await api(`/recipes/${id}`, 'PATCH', patch)
    const idx = items.value.findIndex(x => x.id === id)
    if (idx !== -1) items.value[idx] = r
    if (current.value?.id === id) current.value = r
    return r
  }

  async function remove(id) {
    await api(`/recipes/${id}`, 'DELETE')
    items.value    = items.value.filter(x => x.id !== id)
    allItems.value = allItems.value.filter(x => x.id !== id)
    if (current.value?.id === id) current.value = null
  }

  async function bulkRemove(ids) {
    const result = await api('/recipes/bulk', 'DELETE', { ids })
    const deletedSet = new Set(result.deleted)
    items.value    = items.value.filter(x => !deletedSet.has(x.id))
    allItems.value = allItems.value.filter(x => !deletedSet.has(x.id))
    if (current.value && deletedSet.has(current.value.id)) current.value = null
    return result
  }

  async function pushToList(id, items = null) {
    return await api(`/recipes/${id}/push-to-list`, 'POST', items ? { items } : {})
  }

  async function toggleFavorite(id) {
    const recipe = allItems.value.find(r => r.id === id) || current.value
    const wasFav = recipe?.is_favorited ?? false
    const method = wasFav ? 'DELETE' : 'POST'
    const result = await api(`/recipes/${id}/favorite`, method)
    // Update in-place everywhere
    const patch = r => r.id === id ? { ...r, is_favorited: result.is_favorited } : r
    allItems.value = allItems.value.map(patch)
    items.value    = items.value.map(patch)
    if (current.value?.id === id) current.value = { ...current.value, is_favorited: result.is_favorited }
    return result.is_favorited
  }

  return { items, allItems, current, load, loadAll, get, create, importFromUrl, update, remove, bulkRemove, pushToList, toggleFavorite }
})
