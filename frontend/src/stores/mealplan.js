import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from './api'

export const useMealPlanStore = defineStore('mealplan', () => {
  const plans = ref([])

  async function load(hid, from, to, scope = 'mine') {
    plans.value = await api(`/households/${hid}/meal-plans?from=${from}&to=${to}&scope=${scope}`)
  }

  async function create(hid, plan) {
    const p = await api(`/households/${hid}/meal-plans`, 'POST', plan)
    plans.value.push(p)
    return p
  }

  async function update(id, patch) {
    const p = await api(`/meal-plans/${id}`, 'PATCH', patch)
    const i = plans.value.findIndex(x => x.id === id)
    if (i !== -1) plans.value[i] = p
    return p
  }

  async function remove(id) {
    await api(`/meal-plans/${id}`, 'DELETE')
    plans.value = plans.value.filter(x => x.id !== id)
  }

  async function bulkRemove(ids) {
    const res = await api('/meal-plans/bulk', 'DELETE', { ids })
    const s = new Set(res.deleted)
    plans.value = plans.value.filter(x => !s.has(x.id))
    return res
  }

  async function reorder(hid, plan_date, ids) {
    await api(`/households/${hid}/meal-plans/reorder`, 'PATCH', { plan_date, ids })
    // Update sort_order locally to avoid a reload
    ids.forEach((id, idx) => {
      const p = plans.value.find(x => x.id === id)
      if (p) p.sort_order = idx
    })
  }

  return { plans, load, create, update, remove, bulkRemove, reorder }
})
