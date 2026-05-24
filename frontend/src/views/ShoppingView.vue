<template>
  <div class="shopping-view">
    <!-- Top bar: household context -->
    <div class="topbar">
      <div v-if="hh.current" class="hh-context">
        <Avatar :name="hh.current.name" :color="hhColor" :size="30" :round="false" />
        <div class="hh-context-info">
          <div class="hh-context-row">
            <span class="hh-name">{{ hh.current.name }}</span>
            <Pill v-if="hh.current.role === 'owner'" tone="amber">{{ $t('household.roles.owner') }}</Pill>
            <Pill v-else-if="hh.current.role === 'admin'" tone="accent">{{ $t('household.roles.admin') }}</Pill>
          </div>
          <div class="hh-meta">{{ hh.current.member_count }} members</div>
        </div>
      </div>
      <div v-else class="hh-context-empty">
        <span class="hh-meta">{{ $t('shopping.noHousehold') }}</span>
      </div>
      <div class="topbar-actions">
        <router-link v-if="hh.current" :to="'/households/' + hh.current.id + '/settings'" class="topbar-btn">
          <AppIcon :d="I.settings" :size="14" /> Settings
        </router-link>
      </div>
    </div>

    <!-- Content -->
    <div class="content">
      <!-- Title -->
      <div class="view-title">
        <div class="view-mono">{{ $t('shopping.title') }}</div>
        <h1>What's on the list.</h1>
      </div>

      <!-- No household state -->
      <div v-if="!hh.current" class="empty-state">
        <AppIcon :d="I.home" :size="32" />
        <p>{{ $t('shopping.noHouseholdDesc') }}</p>
      </div>

      <template v-else>
        <!-- Add bar -->
        <div class="add-bar" :class="{ focused: addFocused }">
          <AppIcon :d="I.plus" :size="20" :sw="2.2" class="add-icon" />
          <input
            ref="addInput"
            v-model="newItem"
            class="add-input"
            :placeholder="$t('shopping.addPlaceholder')"
            @keydown.enter="addItem"
            @focus="addFocused = true"
            @blur="addFocused = false"
          />
          <Pill v-if="parsedQty" tone="accent">qty {{ parsedQty }}</Pill>
          <button class="add-btn" @click="addItem">{{ $t('global.create') || 'Add' }}</button>
        </div>

        <!-- Sort & filter -->
        <div v-if="items.length" class="filter-bar">
          <div class="filter-group">
            <AppIcon :d="I.sort" :size="14" class="filter-icon" />
            <span class="filter-mono">Sort</span>
            <Chip :active="sortMode === 'default'" @click="sortMode = 'default'">{{ $t('shopping.sortDefault') }}</Chip>
            <Chip :active="sortMode === 'az'" @click="sortMode = 'az'">A → Z</Chip>
            <Chip :active="sortMode === 'za'" @click="sortMode = 'za'">Z → A</Chip>
          </div>
          <div v-if="uniqueUsers.length > 1" class="filter-divider" />
          <div v-if="uniqueUsers.length > 1" class="filter-group">
            <AppIcon :d="I.filter" :size="14" class="filter-icon" />
            <span class="filter-mono">By</span>
            <Chip :active="filterUser === null" @click="filterUser = null">{{ $t('shopping.filterAll') }}</Chip>
            <Chip
              v-for="u in uniqueUsers" :key="u.name"
              :active="filterUser === u.name"
              :color="u.color"
              @click="filterUser = u.name"
            >{{ u.name }}</Chip>
          </div>
        </div>

        <!-- Empty state -->
        <div v-if="items.length === 0" class="empty-state">
          <AppIcon :d="I.spark" :size="32" />
          <p>{{ $t('shopping.empty') }}</p>
        </div>

        <!-- No results -->
        <div v-else-if="displayedUnchecked.length === 0 && displayedChecked.length === 0" class="empty-state">
          <AppIcon :d="I.search" :size="32" />
          <p>{{ $t('shopping.noResults') }}</p>
        </div>

        <!-- To buy -->
        <div v-if="displayedUnchecked.length">
          <SectionHeader :label="`To buy · ${displayedUnchecked.length}`" />
          <div class="item-list">
            <div
              v-for="(item, i) in displayedUnchecked" :key="item.id"
              class="item-row"
              :class="{ divide: i > 0 }"
            >
              <ItemRow :item="item" @toggle="toggle" @remove="remove" />
            </div>
          </div>
        </div>

        <!-- Done -->
        <div v-if="displayedChecked.length" style="margin-top: 24px;">
          <SectionHeader
            :label="`Done · ${displayedChecked.length}`"
            action="Clear all"
            danger
            @action="clearChecked"
          />
          <div class="item-list">
            <div
              v-for="(item, i) in displayedChecked" :key="item.id"
              class="item-row"
              :class="{ divide: i > 0 }"
            >
              <ItemRow :item="item" @toggle="toggle" @remove="remove" />
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useHouseholdStore } from '../stores/household'
import { useAuthStore, avatarColor } from '../stores/auth'
import { api } from '../stores/api'
import AppIcon from '../components/AppIcon.vue'
import Avatar from '../components/Avatar.vue'
import Pill from '../components/Pill.vue'
import Chip from '../components/Chip.vue'
import SectionHeader from '../components/SectionHeader.vue'
import { I } from '../components/icons.js'
import ItemRow from '../components/ItemRow.vue'

const { t } = useI18n()
const hh   = useHouseholdStore()
const auth = useAuthStore()

const items      = ref([])
const newItem    = ref('')
const addFocused = ref(false)
const sortMode   = ref('default')
const filterUser = ref(null)

const hhColor = computed(() => {
  if (!hh.current) return 'var(--surface-hi)'
  const colors = ['#c79bff','#ffb86b','#7cf2a0','#9bd9ff','#ff9ec7','#ffd166']
  return colors[(hh.current.id - 1) % colors.length]
})

const parsedQty = computed(() => {
  if (!newItem.value.trim()) return null
  const { quantity } = parseQuantity(newItem.value.trim())
  return quantity !== '1' ? quantity : null
})

const unchecked = computed(() => items.value.filter(i => !i.checked))
const checked   = computed(() => items.value.filter(i => i.checked))

const uniqueUsers = computed(() => {
  const map = {}
  items.value.forEach(i => {
    if (i.added_by_name && !map[i.added_by_name]) {
      map[i.added_by_name] = { name: i.added_by_name, color: avatarColor(i.added_by) }
    }
  })
  return Object.values(map).sort((a, b) => a.name.localeCompare(b.name))
})

function applySort(list) {
  if (sortMode.value === 'az') return [...list].sort((a, b) => a.name.localeCompare(b.name))
  if (sortMode.value === 'za') return [...list].sort((a, b) => b.name.localeCompare(a.name))
  return list
}

const displayedUnchecked = computed(() => {
  const base = filterUser.value ? unchecked.value.filter(i => i.added_by_name === filterUser.value) : unchecked.value
  return applySort(base)
})
const displayedChecked = computed(() => {
  const base = filterUser.value ? checked.value.filter(i => i.added_by_name === filterUser.value) : checked.value
  return applySort(base)
})

async function loadItems() {
  if (!hh.current) { items.value = []; return }
  try { items.value = await api(`/households/${hh.current.id}/items`) } catch(e) {}
}

let pollTimer = null
function startPolling() { stopPolling(); if (hh.current) pollTimer = setInterval(loadItems, 4000) }
function stopPolling() { if (pollTimer) { clearInterval(pollTimer); pollTimer = null } }

watch(() => hh.current?.id, () => { filterUser.value = null; loadItems(); startPolling() }, { immediate: true })
onUnmounted(stopPolling)

function parseQuantity(text) {
  const m = text.match(/^(\d+)\s*[xX×]\s*(.+)/) || text.match(/^(.+?)\s*[xX×]\s*(\d+)$/)
  if (m) {
    const first = m[1].trim(), second = m[2].trim()
    if (/^\d+$/.test(first))  return { name: second, quantity: first }
    if (/^\d+$/.test(second)) return { name: first,  quantity: second }
  }
  return { name: text, quantity: '1' }
}

async function addItem() {
  const text = newItem.value.trim()
  if (!text || !hh.current) return
  const { name, quantity } = parseQuantity(text)
  try {
    const item = await api(`/households/${hh.current.id}/items`, 'POST', { name, quantity })
    items.value.unshift(item)
    newItem.value = ''
  } catch(e) {}
}

async function toggle(item) {
  try {
    const res = await api(`/items/${item.id}/toggle`, 'PATCH')
    const idx = items.value.findIndex(i => i.id === item.id)
    if (idx !== -1) items.value[idx] = { ...items.value[idx], checked: res.checked }
    await loadItems()
  } catch(e) {}
}

async function remove(item) {
  try {
    await api(`/items/${item.id}`, 'DELETE')
    items.value = items.value.filter(i => i.id !== item.id)
  } catch(e) {}
}

async function clearChecked() {
  if (!hh.current) return
  try {
    await api(`/households/${hh.current.id}/items/clear-checked`, 'DELETE')
    items.value = items.value.filter(i => !i.checked)
  } catch(e) {}
}
</script>

<style scoped>
.shopping-view { display: flex; flex-direction: column; min-height: 100%; }

/* Topbar */
.topbar {
  padding: 18px 32px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 14px;
}
.hh-context { display: flex; align-items: center; gap: 12px; flex: 1; min-width: 0; }
.hh-context-info { flex: 1; min-width: 0; }
.hh-context-row { display: flex; align-items: center; gap: 8px; }
.hh-name { font-size: 16px; font-weight: 600; letter-spacing: -0.2px; }
.hh-meta { font-family: var(--font-mono); font-size: 10px; font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase; color: var(--text-mute); }
.hh-context-empty { flex: 1; }
.topbar-actions { display: flex; gap: 8px; }
.topbar-btn {
  padding: 7px 12px; border-radius: 8px;
  background: var(--surface); border: 1px solid var(--border);
  color: var(--text-dim); font-size: 12px; font-family: var(--font-sans); font-weight: 500;
  display: flex; align-items: center; gap: 6px;
  text-decoration: none; cursor: pointer;
  transition: border-color 0.15s;
}
.topbar-btn:hover { border-color: var(--border-hi); color: var(--text); }

/* Content */
.content {
  flex: 1;
  padding: 28px 32px;
  max-width: 920px;
  width: 100%;
  margin: 0 auto;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.view-mono { font-family: var(--font-mono); font-size: 10px; font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase; color: var(--text-dim); margin-bottom: 6px; }
.view-title h1 { font-size: 32px; font-weight: 600; letter-spacing: -0.8px; line-height: 1.1; }

/* Add bar */
.add-bar {
  background: var(--surface);
  border: 1.5px solid var(--border-hi);
  border-radius: 14px;
  padding: 6px 6px 6px 18px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: border-color 0.15s;
}
.add-bar.focused { border-color: var(--accent); }
.add-icon { color: var(--text-mute); flex-shrink: 0; }
.add-input { flex: 1; font-size: 16px; color: var(--text); min-width: 0; background: none; border: none; outline: none; }
.add-btn {
  padding: 10px 18px; border-radius: 10px;
  background: var(--accent); color: var(--accent-ink);
  font-size: 13px; font-weight: 600; font-family: var(--font-sans);
  cursor: pointer; flex-shrink: 0;
  transition: filter 0.15s;
}
.add-btn:hover { filter: brightness(1.08); }

/* Filter bar */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}
.filter-group { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.filter-icon { color: var(--text-mute); }
.filter-mono { font-family: var(--font-mono); font-size: 10px; font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase; color: var(--text-mute); }
.filter-divider { width: 1px; height: 20px; background: var(--border); flex-shrink: 0; }

/* Item list */
.item-list {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  overflow: hidden;
}
.item-row.divide { border-top: 1px solid var(--border); }

/* Empty state */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 48px 24px;
  color: var(--text-mute);
  text-align: center;
}
.empty-state p { font-size: 14px; }

@media (max-width: 768px) {
  .topbar { padding: 14px 20px; }
  .content { padding: 20px; }
  .view-title h1 { font-size: 24px; }
}
</style>
