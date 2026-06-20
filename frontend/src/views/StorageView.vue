<template>
  <div class="sv-view">

    <!-- ── Context bar ────────────────────────────────────────── -->
    <div class="context-bar">
      <Avatar :name="hh.current?.name || '?'" :color="hhColor" :size="30" :round="false" />
      <div class="hh-info">
        <div class="hh-name-row">
          <span class="hh-name">{{ hh.current?.name }}</span>
          <Pill v-if="isAdmin" tone="accent">{{ $t('household.roles.' + (hh.current?.role || 'member')) }}</Pill>
        </div>
        <span class="mono dim">{{ totalItems }} {{ $t('storage.units', { n: '' }).replace('{n}', '').trim() }}</span>
      </div>
    </div>

    <!-- ── Title row ──────────────────────────────────────────── -->
    <div class="title-row">
      <div>
        <div class="mono dim">{{ $t('storage.title') }} · {{ totalItems }} {{ $t('storage.items', { n: totalItems }) }}</div>
        <h1 class="page-heading">{{ $t('storage.heading') }}</h1>
      </div>
      <div class="title-actions">
        <button v-if="isAdmin" class="ghost-btn" @click="openLocMgr">
          <AppIcon :d="I.settings" :size="15" :sw="2" />
          {{ $t('storage.manageLocations') }}
        </button>
        <button v-if="!isRestricted" class="primary-btn" @click="openAddItem(null)">
          <AppIcon :d="I.plus" :size="16" :sw="2.2" />
          {{ $t('storage.addItem') }}
        </button>
      </div>
    </div>

    <!-- ── Running low banner ─────────────────────────────────── -->
    <div v-if="lowItems.length" class="low-banner">
      <AppIcon :d="I.bell" :size="16" :sw="2" />
      <span>{{ $t('storage.runningLow', { n: lowItems.length }) }}</span>
      <span class="flex1" />
      <button class="ghost-btn sm" @click="addLowToList">
        <AppIcon :d="I.cart" :size="14" :sw="2" />
        {{ $t('storage.addToList') }}
      </button>
    </div>

    <!-- ── Location filter chips ──────────────────────────────── -->
    <div class="loc-chips">
      <button
        class="loc-chip" :class="{ active: filterLocId === null }"
        @click="filterLocId = null"
      >
        <AppIcon :d="I.box" :size="14" :sw="2" />
        {{ $t('storage.all') }}
        <span class="chip-count">{{ storage.items.length }}</span>
      </button>
      <button
        v-for="loc in storage.locations" :key="loc.id"
        class="loc-chip" :class="{ active: filterLocId === loc.id }"
        :style="filterLocId === loc.id ? { '--lc': loc.tone } : {}"
        @click="filterLocId = loc.id"
      >
        <AppIcon :d="I[loc.icon] || I.shelf" :size="14" :sw="2" />
        {{ loc.name }}
        <span class="chip-count">{{ itemsForLoc(loc.id).length }}</span>
      </button>
    </div>

    <!-- ── Body ───────────────────────────────────────────────── -->
    <div class="body-scroll">

      <!-- No locations yet -->
      <div v-if="!storage.locations.length" class="empty-state">
        <div class="empty-icon"><AppIcon :d="I.box" :size="28" :sw="1.4" /></div>
        <p>{{ $t('storage.noLocations') }}</p>
        <button v-if="isAdmin" class="primary-btn" @click="openLocMgr">
          {{ $t('storage.createLocation') }}
        </button>
      </div>

      <template v-else>
        <div
          v-for="loc in visibleLocations" :key="loc.id"
          class="loc-section"
          :class="{ 'drag-over': dragOverLoc === loc.id && dragItemId !== null }"
          @dragover.prevent="dragOverLoc = loc.id"
          @drop.prevent="onDropLoc(loc.id)"
        >
          <!-- Location header -->
          <div class="loc-header">
            <span class="loc-icon-wrap" :style="{ background: loc.tone + '22', color: loc.tone }">
              <AppIcon :d="I[loc.icon] || I.shelf" :size="16" :sw="2" />
            </span>
            <span class="loc-name">{{ loc.name }}</span>
            <span class="mono dim loc-count">{{ itemsForLoc(loc.id).length }} {{ $t('storage.items', { n: itemsForLoc(loc.id).length }) }}</span>
          </div>

          <!-- Items -->
          <div v-if="itemsForLoc(loc.id).length === 0" class="loc-empty">
            {{ $t('storage.nothingHere') }}
          </div>
          <div v-else class="item-list">
            <div
              v-for="item in itemsForLoc(loc.id)" :key="item.id"
              class="item-row"
              :class="{ 'is-out': item.quantity === 0, 'is-low': item.quantity > 0 && item.is_low }"
              :draggable="!isRestricted"
              @dragstart="dragItemId = item.id"
              @dragend="dragItemId = null; dragOverLoc = null"
            >
              <!-- Status dot -->
              <span
                class="status-dot"
                :style="{ background: item.quantity === 0 ? 'var(--danger)' : item.is_low ? 'var(--amber)' : loc.tone }"
              />
              <!-- Qty + unit -->
              <span class="item-qty">{{ item.quantity }}<span v-if="item.unit" class="item-unit"> {{ item.unit }}</span></span>
              <!-- Name + meta -->
              <div class="item-body">
                <span class="item-name">{{ item.name }}</span>
                <span v-if="item.quantity === 0" class="badge out-badge">{{ $t('storage.out') }}</span>
                <span v-else-if="item.is_low" class="badge low-badge">{{ $t('storage.low') }}</span>
                <span v-if="item.added_by_name" class="item-meta">{{ $t('storage.addedBy', { name: item.added_by_name }) }}</span>
                <span v-if="item.low_threshold > 0" class="item-meta">{{ $t('storage.alertAt', { n: item.low_threshold }) }}</span>
              </div>
              <!-- Hover actions -->
              <div class="item-actions">
                <button class="icon-btn sm" :title="$t('storage.addToList')" @click.stop="pushItemToList(item)">
                  <AppIcon :d="I.cart" :size="14" :sw="2" />
                </button>
                <button class="icon-btn sm" :title="$t('global.edit')" @click.stop="openEditItem(item)">
                  <AppIcon :d="I.pencil" :size="14" :sw="2" />
                </button>
                <button class="icon-btn sm danger" :title="$t('global.delete')" @click.stop="deleteItem(item.id)">
                  <AppIcon :d="I.trash" :size="14" :sw="2" />
                </button>
              </div>
            </div>
          </div>

          <!-- Add item to this location shortcut -->
          <button v-if="!isRestricted" class="add-loc-btn" @click="openAddItem(loc.id)">
            <AppIcon :d="I.plus" :size="13" :sw="2.2" />
          </button>
        </div>
      </template>
    </div>

    <!-- ── Add / Edit Item modal ──────────────────────────────── -->
    <Teleport to="body">
      <div v-if="itemEditor.open" class="modal-bg" @click.self="itemEditor.open = false">
        <div class="modal">
          <div class="modal-header">
            <h2>{{ itemEditor.id ? $t('storage.editItem') : $t('storage.addItem') }}</h2>
            <button class="icon-btn" @click="itemEditor.open = false"><AppIcon :d="I.x" :size="18" :sw="2" /></button>
          </div>

          <!-- Name -->
          <label class="field-label">{{ $t('storage.itemName') }}</label>
          <input
            v-model="itemEditor.name"
            class="field"
            :placeholder="$t('storage.itemName')"
            autofocus
            @keydown.enter="saveItem"
          />

          <!-- Location -->
          <label class="field-label">{{ $t('storage.location') }}</label>
          <div class="loc-chips tight">
            <button
              v-for="loc in storage.locations" :key="loc.id"
              class="loc-chip sm" :class="{ active: itemEditor.location_id === loc.id }"
              :style="itemEditor.location_id === loc.id ? { '--lc': loc.tone } : {}"
              @click="itemEditor.location_id = loc.id"
            >
              <AppIcon :d="I[loc.icon] || I.shelf" :size="12" :sw="2" />
              {{ loc.name }}
            </button>
          </div>

          <!-- Qty + unit -->
          <div class="field-row">
            <div class="field-col">
              <label class="field-label">{{ $t('storage.quantity') }}</label>
              <input v-model.number="itemEditor.quantity" type="number" min="0" class="field" />
            </div>
            <div class="field-col">
              <label class="field-label">{{ $t('storage.unit') }}</label>
              <input v-model="itemEditor.unit" class="field" placeholder="kg / pcs / L…" />
            </div>
          </div>

          <!-- Low threshold -->
          <label class="field-label">{{ $t('storage.lowAt') }}</label>
          <input v-model.number="itemEditor.low_threshold" type="number" min="0" class="field" />

          <div v-if="itemEditor.error" class="field-error">{{ itemEditor.error }}</div>

          <div class="modal-footer">
            <button class="ghost-btn" @click="itemEditor.open = false">{{ $t('global.cancel') }}</button>
            <button class="primary-btn" :disabled="itemEditor.saving" @click="saveItem">
              {{ itemEditor.saving ? $t('global.loading') : $t('global.save') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ── Location manager modal (admin) ────────────────────── -->
    <Teleport to="body">
      <div v-if="locMgr.open" class="modal-bg" @click.self="locMgr.open = false">
        <div class="modal loc-mgr-modal">
          <div class="modal-header">
            <h2>{{ $t('storage.storageLocations') }}</h2>
            <button class="icon-btn" @click="locMgr.open = false"><AppIcon :d="I.x" :size="18" :sw="2" /></button>
          </div>

          <!-- Existing locations -->
          <div class="loc-mgr-list">
            <div
              v-for="(loc, idx) in locMgr.draft" :key="loc._key"
              class="loc-mgr-row"
              :class="{ deleted: loc._deleted }"
            >
              <template v-if="!loc._deleted">
                <!-- Icon picker -->
                <div class="icon-picker">
                  <button
                    v-for="icn in LOC_ICONS" :key="icn"
                    class="icon-opt" :class="{ active: loc.icon === icn }"
                    :title="icn"
                    @click="loc.icon = icn"
                  >
                    <AppIcon :d="I[icn]" :size="16" :sw="2" />
                  </button>
                </div>
                <!-- Name input -->
                <input v-model="loc.name" class="field sm" :placeholder="$t('storage.locationNamePlaceholder')" />
                <!-- Color swatches -->
                <div class="color-swatches">
                  <button
                    v-for="c in LOC_TONES" :key="c"
                    class="swatch" :class="{ active: loc.tone === c }"
                    :style="{ background: c }"
                    @click="loc.tone = c"
                  />
                </div>
                <!-- Delete -->
                <button class="icon-btn sm danger" :title="$t('global.delete')" @click="markLocDeleted(idx)">
                  <AppIcon :d="I.trash" :size="14" :sw="2" />
                </button>
              </template>
              <template v-else>
                <span class="deleted-label">{{ loc.name }} — <em>{{ $t('storage.deleteLocationHint') }}</em></span>
                <button class="ghost-btn sm" @click="loc._deleted = false">{{ $t('global.cancel') }}</button>
              </template>
            </div>
          </div>

          <!-- Add new location row -->
          <div class="loc-mgr-add">
            <div class="icon-picker">
              <button
                v-for="icn in LOC_ICONS" :key="icn"
                class="icon-opt" :class="{ active: locMgr.newIcon === icn }"
                :title="icn"
                @click="locMgr.newIcon = icn"
              >
                <AppIcon :d="I[icn]" :size="16" :sw="2" />
              </button>
            </div>
            <input
              v-model="locMgr.newName"
              class="field sm"
              :placeholder="$t('storage.newLocation')"
              @keydown.enter="addLocDraft"
            />
            <div class="color-swatches">
              <button
                v-for="c in LOC_TONES" :key="c"
                class="swatch" :class="{ active: locMgr.newTone === c }"
                :style="{ background: c }"
                @click="locMgr.newTone = c"
              />
            </div>
            <button class="ghost-btn sm" @click="addLocDraft">
              <AppIcon :d="I.plus" :size="14" :sw="2.2" />
            </button>
          </div>

          <div v-if="locMgr.error" class="field-error">{{ locMgr.error }}</div>

          <div class="modal-footer">
            <button class="ghost-btn" @click="locMgr.open = false">{{ $t('global.cancel') }}</button>
            <button class="primary-btn" :disabled="locMgr.saving" @click="saveLocations">
              {{ locMgr.saving ? $t('global.loading') : $t('storage.saveLocations') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ── Toast ──────────────────────────────────────────────── -->
    <Teleport to="body">
      <Transition name="toast">
        <div v-if="toastMsg" class="toast">{{ toastMsg }}</div>
      </Transition>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStorageStore }   from '../stores/storage'
import { useHouseholdStore } from '../stores/household'
import { useAuthStore }      from '../stores/auth'
import { avatarColor }       from '../stores/auth'
import { api }               from '../stores/api'
import AppIcon from '../components/AppIcon.vue'
import Avatar  from '../components/Avatar.vue'
import Pill    from '../components/Pill.vue'
import { I }   from '../components/icons.js'

const { t } = useI18n()
const storage = useStorageStore()
const hh      = useHouseholdStore()
const auth    = useAuthStore()

// ── Constants ──────────────────────────────────────────────────────────────
const LOC_ICONS = ['shelf', 'fridge', 'freezer', 'pantry', 'cooler', 'basket', 'box']
const LOC_TONES = ['#9bd9ff','#c79bff','#7cf2a0','#ffb86b','#ff9ec7','#ffd166','#9ca0a8']

// ── Computed permissions ───────────────────────────────────────────────────
const isAdmin      = computed(() => hh.myRank >= hh.ROLE_RANK.admin)
const isRestricted = computed(() => hh.myRank <= hh.ROLE_RANK.restricted)
const hhColor      = computed(() => avatarColor(hh.current?.id))

// ── Filter state ───────────────────────────────────────────────────────────
const filterLocId = ref(null)

// ── Drag & drop between locations ─────────────────────────────────────────
const dragItemId  = ref(null)
const dragOverLoc = ref(null)

async function onDropLoc(locId) {
  const id = dragItemId.value
  dragItemId.value  = null
  dragOverLoc.value = null
  if (!id) return
  const item = storage.items.find(i => i.id === id)
  if (!item || item.location_id === locId) return
  try {
    await storage.updateItem(id, { location_id: locId })
    toast(t('storage.itemUpdated'))
  } catch (e) { toast(e.message) }
}

// ── Derived item helpers ───────────────────────────────────────────────────
function itemsForLoc(locId) {
  return storage.items.filter(i => i.location_id === locId)
}

const visibleLocations = computed(() => {
  if (filterLocId.value === null) return storage.locations
  return storage.locations.filter(l => l.id === filterLocId.value)
})

const totalItems = computed(() => storage.items.length)

const lowItems = computed(() =>
  storage.items.filter(i => i.is_low || i.quantity === 0)
)

// ── Load ───────────────────────────────────────────────────────────────────
async function loadAll() {
  if (!hh.current) return
  try { await storage.load(hh.current.id) } catch (e) { /* silent */ }
}

watch(() => hh.current?.id, () => { filterLocId.value = null; loadAll() }, { immediate: true })

// ── Toast ──────────────────────────────────────────────────────────────────
const toastMsg = ref('')
let toastTimer = null
function toast(msg) {
  toastMsg.value = msg
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => { toastMsg.value = '' }, 2800)
}

// ── Add low items to shopping list ────────────────────────────────────────
async function addLowToList() {
  if (!hh.current) return
  try {
    for (const item of lowItems.value) {
      await api(`/households/${hh.current.id}/items`, 'POST', {
        name: `${item.name}${item.unit ? ' (' + item.unit + ')' : ''}`,
      })
    }
    toast(t('storage.itemAdded'))
  } catch (e) { /* silent */ }
}

async function pushItemToList(item) {
  if (!hh.current) return
  try {
    await api(`/households/${hh.current.id}/items`, 'POST', {
      name: `${item.name}${item.unit ? ' (' + item.unit + ')' : ''}`,
    })
    toast(t('storage.itemAdded'))
  } catch (e) { /* silent */ }
}

// ── Item editor ────────────────────────────────────────────────────────────
const itemEditor = ref({
  open: false, id: null, saving: false, error: '',
  name: '', location_id: null, quantity: 0, unit: '', low_threshold: 0,
})

function openAddItem(locId) {
  itemEditor.value = {
    open: true, id: null, saving: false, error: '',
    name: '', location_id: locId ?? (storage.locations[0]?.id ?? null),
    quantity: 0, unit: '', low_threshold: 0,
  }
}

function openEditItem(item) {
  itemEditor.value = {
    open: true, id: item.id, saving: false, error: '',
    name: item.name,
    location_id: item.location_id,
    quantity: item.quantity,
    unit: item.unit || '',
    low_threshold: item.low_threshold || 0,
  }
}

async function saveItem() {
  const ed = itemEditor.value
  if (!ed.name.trim()) { ed.error = t('storage.itemName'); return }
  if (!ed.location_id) { ed.error = t('storage.location'); return }
  ed.saving = true; ed.error = ''
  try {
    const payload = {
      name: ed.name.trim(),
      location_id: ed.location_id,
      quantity: ed.quantity,
      unit: ed.unit,
      low_threshold: ed.low_threshold,
    }
    if (ed.id) {
      await storage.updateItem(ed.id, payload)
      toast(t('storage.itemUpdated'))
    } else {
      await storage.createItem(hh.current.id, payload)
      toast(t('storage.itemAdded'))
    }
    itemEditor.value.open = false
  } catch (e) {
    ed.error = e.message || 'Error'
  } finally {
    ed.saving = false
  }
}

async function deleteItem(id) {
  try {
    await storage.removeItem(id)
    toast(t('storage.itemRemoved'))
  } catch (e) { /* silent */ }
}

// ── Location manager ───────────────────────────────────────────────────────
let _draftKey = 0

const locMgr = ref({
  open: false, saving: false, error: '',
  draft: [],
  newName: '', newIcon: 'shelf', newTone: '#9bd9ff',
})

function openLocMgr() {
  locMgr.value = {
    open: true, saving: false, error: '',
    draft: storage.locations.map(l => ({ ...l, _key: ++_draftKey, _deleted: false })),
    newName: '', newIcon: 'shelf', newTone: '#9bd9ff',
  }
}

function addLocDraft() {
  const name = locMgr.value.newName.trim()
  if (!name) return
  locMgr.value.draft.push({
    _key: ++_draftKey, _deleted: false,
    id: null, name,
    icon: locMgr.value.newIcon,
    tone: locMgr.value.newTone,
  })
  locMgr.value.newName = ''
}

function markLocDeleted(idx) {
  const loc = locMgr.value.draft[idx]
  if (loc.id === null) {
    // unsaved draft — just remove
    locMgr.value.draft.splice(idx, 1)
  } else {
    loc._deleted = true
  }
}

async function saveLocations() {
  const mgr = locMgr.value
  // Auto-flush whatever is still typed in the "new location" row
  if (mgr.newName.trim()) addLocDraft()
  mgr.saving = true; mgr.error = ''
  try {
    const origMap = Object.fromEntries(storage.locations.map(l => [l.id, l]))

    for (const loc of mgr.draft) {
      if (loc.id === null && !loc._deleted) {
        // CREATE
        await storage.createLocation(hh.current.id, {
          name: loc.name, icon: loc.icon, tone: loc.tone,
        })
      } else if (loc.id !== null && loc._deleted) {
        // DELETE
        await storage.removeLocation(loc.id)
      } else if (loc.id !== null && !loc._deleted) {
        // PATCH if changed
        const orig = origMap[loc.id]
        if (!orig) continue
        if (orig.name !== loc.name || orig.icon !== loc.icon || orig.tone !== loc.tone) {
          await storage.updateLocation(loc.id, {
            name: loc.name, icon: loc.icon, tone: loc.tone,
          })
        }
      }
    }
    toast(t('storage.locationsUpdated'))
    mgr.open = false
    filterLocId.value = null
    await loadAll()
  } catch (e) {
    mgr.error = e.message || 'Error'
  } finally {
    mgr.saving = false
  }
}
</script>

<style scoped>
.sv-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 22px 24px 0;
  gap: 0;
  overflow: hidden;
}

/* ── Context bar ──────────────────────────────────────────────────────────── */
.context-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
}
.hh-info { flex: 1; min-width: 0; }
.hh-name-row { display: flex; align-items: center; gap: 8px; }
.hh-name { font-size: 15px; font-weight: 600; }
.mono { font-family: var(--font-mono); font-size: 11px; }
.dim  { color: var(--text-dim); }

/* ── Title row ────────────────────────────────────────────────────────────── */
.title-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 16px;
}
.title-actions { display: flex; align-items: center; gap: 8px; }
.page-heading { margin: 2px 0 0; font-size: 26px; font-weight: 700; letter-spacing: -0.5px; }

/* ── Running low banner ───────────────────────────────────────────────────── */
.low-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 14px;
  background: var(--amber-bg);
  border: 1px solid rgba(255,194,107,0.2);
  border-radius: 10px;
  color: var(--amber);
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 14px;
}

/* ── Location filter chips ────────────────────────────────────────────────── */
.loc-chips {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
.loc-chips.tight { margin-bottom: 0; }
.loc-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 11px 5px 9px;
  border-radius: var(--r-chip);
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text-dim);
  font-size: 12.5px;
  font-weight: 500;
  cursor: pointer;
  transition: border-color 120ms, color 120ms, background 120ms;
}
.loc-chip:hover { border-color: var(--border-hi); color: var(--text); }
.loc-chip.active {
  border-color: var(--lc, var(--accent));
  color: var(--lc, var(--accent));
  background: color-mix(in srgb, var(--lc, var(--accent)) 12%, transparent);
}
.loc-chip.sm { font-size: 11.5px; padding: 4px 9px 4px 7px; }
.chip-count {
  font-family: var(--font-mono);
  font-size: 10px;
  color: inherit;
  opacity: 0.7;
  margin-left: 2px;
}

/* ── Body ─────────────────────────────────────────────────────────────────── */
.body-scroll {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 32px;
}
.body-scroll::-webkit-scrollbar { width: 4px; }
.body-scroll::-webkit-scrollbar-thumb { background: var(--border-hi); border-radius: 4px; }

/* ── Empty ────────────────────────────────────────────────────────────────── */
.empty-state {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; gap: 12px; padding: 60px 20px;
  color: var(--text-dim); text-align: center;
}
.empty-icon { opacity: 0.35; }

/* ── Location section ─────────────────────────────────────────────────────── */
.loc-section { margin-bottom: 24px; border-radius: 14px; padding: 6px; margin: -6px -6px 18px; }
.loc-section.drag-over {
  background: color-mix(in srgb, var(--accent) 7%, transparent);
  outline: 2px dashed rgba(199,155,255,0.45);
  outline-offset: 0;
}
.loc-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}
.loc-icon-wrap {
  width: 28px; height: 28px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.loc-name  { font-size: 14px; font-weight: 600; }
.loc-count { font-size: 11px; margin-left: 2px; }
.loc-empty { font-size: 12px; color: var(--text-mute); padding: 6px 0 6px 38px; }

/* ── Item rows ────────────────────────────────────────────────────────────── */
.item-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 6px;
}
.item-row {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  transition: border-color 120ms;
}
.item-row:hover { border-color: var(--border-hi); }
.item-row:hover .item-actions { opacity: 1; pointer-events: auto; }
.item-row[draggable="true"] { cursor: grab; }
.item-row[draggable="true"]:active { cursor: grabbing; }

.status-dot {
  flex-shrink: 0;
  width: 8px; height: 8px;
  border-radius: 50%;
}
.item-qty {
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 600;
  min-width: 36px;
  color: var(--text);
}
.item-unit { font-weight: 400; color: var(--text); }
.item-body {
  flex: 1; min-width: 0;
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
}
.item-name {
  font-size: 13.5px;
  font-weight: 500;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.item-meta { font-size: 11px; color: var(--text-mute); }

.badge {
  font-size: 10px; font-weight: 700;
  padding: 2px 6px; border-radius: var(--r-pill);
  letter-spacing: 0.3px; text-transform: uppercase;
  flex-shrink: 0;
}
.low-badge { background: var(--amber-bg); color: var(--amber); }
.out-badge { background: var(--danger-bg); color: var(--danger); }

.item-actions {
  display: flex; align-items: center; gap: 4px;
  opacity: 0; pointer-events: none;
  transition: opacity 120ms;
}

/* ── Add to loc shortcut ──────────────────────────────────────────────────── */
.add-loc-btn {
  display: flex; align-items: center; justify-content: center;
  width: 28px; height: 28px;
  border-radius: 8px;
  border: 1.5px dashed var(--border-hi);
  color: var(--text-mute);
  cursor: pointer;
  margin-top: 4px;
  transition: border-color 120ms, color 120ms;
}
.add-loc-btn:hover { border-color: var(--accent); color: var(--accent); }

/* ── Buttons ──────────────────────────────────────────────────────────────── */
.primary-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 7px 14px;
  background: var(--accent); color: var(--accent-ink);
  border-radius: var(--r-pill); font-size: 13px; font-weight: 600;
  cursor: pointer; border: none;
  transition: opacity 120ms;
}
.primary-btn:hover:not(:disabled) { opacity: 0.88; }
.primary-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.ghost-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 7px 14px;
  border: 1px solid var(--border-hi);
  border-radius: var(--r-pill); font-size: 13px; font-weight: 500;
  color: var(--text); background: transparent;
  cursor: pointer;
  transition: border-color 120ms, background 120ms;
}
.ghost-btn:hover { border-color: var(--accent); background: var(--accent-dim); }
.ghost-btn.sm { padding: 5px 10px; font-size: 12px; }

.icon-btn {
  display: inline-flex; align-items: center; justify-content: center;
  width: 32px; height: 32px; border-radius: 8px;
  border: 1px solid transparent; color: var(--text-dim);
  cursor: pointer; background: transparent;
  transition: background 120ms, color 120ms;
}
.icon-btn:hover { background: var(--surface-hi); color: var(--text); }
.icon-btn.sm { width: 26px; height: 26px; border-radius: 6px; }
.icon-btn.danger:hover { background: var(--danger-bg); color: var(--danger); }

.flex1 { flex: 1; }

/* ── Modal ────────────────────────────────────────────────────────────────── */
.modal-bg {
  position: fixed; inset: 0; z-index: 200;
  background: rgba(0,0,0,0.55); backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
  padding: 20px;
}
.modal {
  background: var(--surface);
  border: 1px solid var(--border-hi);
  border-radius: 16px;
  padding: 24px;
  width: 100%; max-width: 440px;
  display: flex; flex-direction: column; gap: 12px;
  max-height: 90vh; overflow-y: auto;
}
.loc-mgr-modal { max-width: 540px; }
.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 4px;
}
.modal-header h2 { font-size: 17px; font-weight: 700; margin: 0; }
.modal-footer {
  display: flex; justify-content: flex-end; gap: 8px;
  margin-top: 4px;
}

.field-label { font-size: 12px; color: var(--text-dim); margin-bottom: 2px; }
.field {
  width: 100%; padding: 8px 11px;
  background: var(--bg2); border: 1px solid var(--border-hi);
  border-radius: var(--r-field); color: var(--text); font-size: 13.5px;
  outline: none; font-family: var(--font-sans);
  transition: border-color 120ms;
}
.field:focus { border-color: var(--accent); }
.field.sm { padding: 6px 10px; font-size: 13px; }
.field-row { display: flex; gap: 10px; }
.field-col { flex: 1; display: flex; flex-direction: column; gap: 4px; }
.field-error { font-size: 12px; color: var(--danger); }

/* ── Location manager ─────────────────────────────────────────────────────── */
.loc-mgr-list { display: flex; flex-direction: column; gap: 8px; }
.loc-mgr-row {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  padding: 8px; background: var(--bg2); border-radius: 10px;
  border: 1px solid var(--border);
}
.loc-mgr-row.deleted { opacity: 0.4; }
.deleted-label { flex: 1; font-size: 12px; color: var(--text-dim); font-style: italic; }

.loc-mgr-add {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  padding: 8px; background: var(--bg2); border-radius: 10px;
  border: 1.5px dashed var(--border-hi);
}

.icon-picker { display: flex; gap: 4px; }
.icon-opt {
  display: flex; align-items: center; justify-content: center;
  width: 28px; height: 28px; border-radius: 7px;
  border: 1px solid var(--border);
  color: var(--text-dim); cursor: pointer; background: transparent;
  transition: border-color 120ms, color 120ms;
}
.icon-opt:hover { border-color: var(--border-hi); color: var(--text); }
.icon-opt.active { border-color: var(--accent); color: var(--accent); background: var(--accent-dim); }

.color-swatches { display: flex; gap: 5px; align-items: center; }
.swatch {
  width: 16px; height: 16px; border-radius: 50%;
  cursor: pointer; border: 2px solid transparent;
  transition: border-color 100ms, transform 100ms;
}
.swatch:hover { transform: scale(1.15); }
.swatch.active { border-color: var(--text); transform: scale(1.15); }

/* ── Toast ────────────────────────────────────────────────────────────────── */
.toast {
  position: fixed; bottom: 28px; left: 50%; transform: translateX(-50%);
  background: var(--surface-hi); border: 1px solid var(--border-hi);
  padding: 9px 20px; border-radius: var(--r-pill);
  font-size: 13px; font-weight: 500; color: var(--text);
  box-shadow: 0 4px 16px rgba(0,0,0,0.4); z-index: 300; white-space: nowrap;
}
.toast-enter-active, .toast-leave-active { transition: opacity 220ms, transform 220ms; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(8px); }
</style>
