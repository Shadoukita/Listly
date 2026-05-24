<template>
  <div class="recipes-view">
    <!-- Topbar -->
    <div class="topbar">
      <div class="topbar-left">
        <div class="hh-avatar" :style="{ background: hhColor }">
          {{ (hh.current?.name || '?')[0].toUpperCase() }}
        </div>
        <div class="hh-info">
          <div class="hh-name-row">
            <span class="hh-name">{{ hh.current?.name || 'Household' }}</span>
            <Pill v-if="auth.isAdmin" tone="accent">Admin</Pill>
          </div>
          <div class="mono">{{ memberCount }} members</div>
        </div>
      </div>
      <button
        v-if="recipes.allItems.length"
        class="random-btn"
        @click="openRandom"
        :title="$t('recipes.random')"
      >
        <AppIcon :d="I.shuffle" :size="14" :sw="2" /> {{ $t('recipes.random') }}
      </button>
      <router-link v-if="hh.current" to="/recipes/new" class="new-btn">
        <AppIcon :d="I.plus" :size="14" :sw="2.2" /> {{ $t('recipes.newRecipe') }}
      </router-link>
    </div>

    <!-- Selection bar -->
    <Transition name="sel-bar">
      <div v-if="selecting" class="selection-bar">
        <button class="sel-close" @click="exitSelection" :title="$t('global.cancel')">
          <AppIcon :d="I.x" :size="15" />
        </button>
        <span class="sel-count">{{ $t('recipes.selected', { n: selectedIds.size }) }}</span>
        <span class="sel-spacer" />
        <button class="sel-btn" @click="selectAll">{{ $t('recipes.selectAll', { n: filtered.length }) }}</button>
        <button class="sel-delete" :disabled="!selectedIds.size || deleting" @click="deleteSelected">
          <AppIcon :d="I.trash" :size="14" />
          {{ deleting ? $t('recipes.deleting') : $t('global.delete') }}
        </button>
      </div>
    </Transition>

    <!-- Content -->
    <div class="content">
      <!-- Title row -->
      <div class="title-row">
        <div>
          <div class="mono">{{ $t('recipes.title') }} · {{ filtered.length }}{{ activeTab !== 'all' ? ' · ' + recipes.allItems.length + ' total' : '' }}</div>
          <h1 class="page-title">{{ $t('recipes.cookbook') }}</h1>
          <p class="page-sub">{{ $t('recipes.cookbookDesc') }}</p>
        </div>
      </div>

      <!-- Filters -->
      <div class="filter-bar">
        <div class="filter-group">
          <Chip :active="activeTab === 'all'"        @click="activeTab = 'all'">{{ $t('recipes.filterAll') }}</Chip>
          <Chip :active="activeTab === 'households'" @click="activeTab = 'households'">{{ $t('recipes.filterHouseholds') }}</Chip>
          <Chip :active="activeTab === 'mine'"       @click="activeTab = 'mine'">{{ $t('recipes.filterMine') }}</Chip>
        </div>
        <div class="divider" />
        <div class="filter-group tag-group" v-if="allTags.length">
          <AppIcon :d="I.filter" :size="14" class="filter-icon" />
          <div class="mono">{{ $t('recipes.filterTag') }}</div>
          <Chip
            v-for="tag in allTags" :key="tag"
            :active="activeTag === tag"
            @click="activeTag = activeTag === tag ? '' : tag"
          >{{ tag }}</Chip>
        </div>
        <span class="spacer" />
        <div class="sort-toggle" v-if="hasCalories">
          <div class="mono">{{ $t('recipes.sortCalories') }}</div>
          <div class="view-btns">
            <button
              class="view-btn" :class="{ active: sortBy === 'cal-asc' }"
              @click="sortBy = sortBy === 'cal-asc' ? '' : 'cal-asc'"
              title="Lowest first"
            >↑</button>
            <button
              class="view-btn" :class="{ active: sortBy === 'cal-desc' }"
              @click="sortBy = sortBy === 'cal-desc' ? '' : 'cal-desc'"
              title="Highest first"
            >↓</button>
          </div>
        </div>
        <div class="view-toggle">
          <div class="mono">{{ $t('recipes.view') }}</div>
          <div class="view-btns">
            <button class="view-btn" :class="{ active: viewMode === 'grid' }" @click="viewMode = 'grid'">
              <AppIcon :d="I.grid" :size="14" />
            </button>
            <button class="view-btn" :class="{ active: viewMode === 'list' }" @click="viewMode = 'list'">
              <AppIcon :d="I.list" :size="14" />
            </button>
          </div>
        </div>
      </div>

      <!-- Loading / Empty -->
      <div v-if="loading" class="empty-state">
        <div class="mono">{{ $t('global.loading') }}</div>
      </div>
      <div v-else-if="!hh.current" class="empty-state">
        <div class="empty-icon">
          <AppIcon :d="I.chef" :size="28" />
        </div>
        <div class="empty-title">{{ $t('recipes.noHousehold') }}</div>
        <p class="empty-sub">{{ $t('recipes.noHouseholdDesc') }}</p>
      </div>
      <div v-else-if="!filtered.length" class="empty-state">
        <div class="empty-icon">
          <AppIcon :d="I.chef" :size="28" />
        </div>
        <div class="empty-title">{{ $t('recipes.noRecipesTitle') }}</div>
        <p class="empty-sub">{{ $t('recipes.noRecipesDesc') }}</p>
        <router-link to="/recipes/new">
          <AppButton size="sm">
            <AppIcon :d="I.plus" :size="14" :sw="2.2" /> {{ $t('recipes.newRecipe') }}
          </AppButton>
        </router-link>
      </div>

        <!-- Grid -->
      <div v-else :class="viewMode === 'grid' ? 'recipe-grid' : 'recipe-list'">
        <RecipeCard
          v-for="recipe in filtered"
          :key="recipe.id"
          :recipe="recipe"
          :current-household-id="hh.current?.id"
          :selecting="selecting"
          :selected="selectedIds.has(recipe.id)"
          @open="router.push(`/recipes/${recipe.id}`)"
          @long-press="onLongPress"
          @select-toggle="toggleSelect"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore, avatarColor } from '../stores/auth'
import { useHouseholdStore } from '../stores/household'
import { useRecipeStore } from '../stores/recipes'
import Pill from '../components/Pill.vue'
import Chip from '../components/Chip.vue'
import AppIcon from '../components/AppIcon.vue'
import AppButton from '../components/AppButton.vue'
import { I } from '../components/icons.js'
import RecipeCard from '../components/RecipeCard.vue'

const router  = useRouter()
const auth    = useAuthStore()
const hh      = useHouseholdStore()
const recipes = useRecipeStore()

const loading    = ref(true)
const activeTab  = ref('all')
const activeTag  = ref('')
const viewMode   = ref('grid')
const sortBy     = ref('')   // '' | 'cal-asc' | 'cal-desc'
const selecting  = ref(false)
const selectedIds = ref(new Set())
const deleting   = ref(false)

const PALETTE = ['#c79bff','#ffb86b','#7cf2a0','#9bd9ff','#ff9ec7','#ffd166']
const hhColor = computed(() => {
  const id = hh.current?.id || 1
  return PALETTE[(id - 1) % PALETTE.length]
})

const memberCount = computed(() => hh.current?.member_count || hh.current?.members?.length || 0)

const myHouseholdIds = computed(() => new Set(hh.households.map(h => h.id)))

const allTags = computed(() => {
  const set = new Set()
  recipes.allItems.forEach(r => {
    const tags = r.tags_json ? JSON.parse(r.tags_json) : []
    tags.forEach(t => set.add(t))
  })
  return [...set]
})

const hasCalories = computed(() => recipes.allItems.some(r => r.calories != null))

const filtered = computed(() => {
  let list = recipes.allItems
  if (activeTab.value === 'households') {
    list = list.filter(r => myHouseholdIds.value.has(r.household_id))
  } else if (activeTab.value === 'mine') {
    list = list.filter(r => r.created_by === auth.user?.id)
  }
  if (activeTag.value) list = list.filter(r => {
    const tags = r.tags_json ? JSON.parse(r.tags_json) : []
    return tags.includes(activeTag.value)
  })
  if (sortBy.value === 'cal-asc') {
    list = [...list].sort((a, b) => (a.calories ?? Infinity) - (b.calories ?? Infinity))
  } else if (sortBy.value === 'cal-desc') {
    list = [...list].sort((a, b) => (b.calories ?? -Infinity) - (a.calories ?? -Infinity))
  }
  return list
})

function onLongPress(recipe) {
  selecting.value = true
  selectedIds.value = new Set([recipe.id])
}

function toggleSelect(id) {
  const s = new Set(selectedIds.value)
  if (s.has(id)) s.delete(id)
  else s.add(id)
  selectedIds.value = s
}

function selectAll() {
  selectedIds.value = new Set(filtered.value.map(r => r.id))
}

function exitSelection() {
  selecting.value = false
  selectedIds.value = new Set()
}

async function deleteSelected() {
  if (!selectedIds.value.size || deleting.value) return
  deleting.value = true
  try {
    await recipes.bulkRemove([...selectedIds.value])
    exitSelection()
  } finally {
    deleting.value = false
  }
}

function openRandom() {
  const pool = recipes.allItems
  if (!pool.length) return
  const pick = pool[Math.floor(Math.random() * pool.length)]
  router.push(`/recipes/${pick.id}`)
}

onMounted(async () => {
  try { await recipes.loadAll() } catch(e) {}
  loading.value = false
})
</script>

<style scoped>
.recipes-view { display: flex; flex-direction: column; min-height: 100%; }

.topbar {
  padding: 18px 32px; border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 14;
}
.topbar-left { display: flex; align-items: center; gap: 12; flex: 1; }
.hh-avatar {
  width: 30px; height: 30px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  color: #0a0a0f; font-size: 14px; font-weight: 700;
  flex-shrink: 0;
}
.hh-info { flex: 1; }
.hh-name-row { display: flex; align-items: center; gap: 8; }
.hh-name { font-size: 16px; font-weight: 600; letter-spacing: -0.2px; }

.random-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 14px; border-radius: 10px;
  background: var(--surface); border: 1px solid var(--border);
  color: var(--text-dim); font-size: 13px; font-weight: 500; cursor: pointer;
  transition: border-color 0.15s, color 0.15s;
}
.random-btn:hover { border-color: var(--border-hi); color: var(--text); }

.new-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 14px; border-radius: 10px;
  background: var(--accent); color: var(--accent-ink);
  font-size: 13px; font-weight: 600; cursor: pointer;
  transition: opacity 0.15s;
  box-shadow: 0 8px 24px -8px rgba(199,155,255,0.5);
}
.new-btn:hover { opacity: 0.88; }

/* Selection bar */
.selection-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 24px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
}
.sel-close {
  width: 30px; height: 30px; border-radius: 8px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  color: var(--text-dim); cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.sel-close:hover { background: var(--surface-hi); color: var(--text); }
.sel-count {
  font-size: 14px; font-weight: 600; color: var(--text);
}
.sel-spacer { flex: 1; }
.sel-btn {
  padding: 6px 14px; border-radius: 8px;
  background: var(--surface-hi); border: 1px solid var(--border);
  color: var(--text-dim); font-size: 13px; font-weight: 500; cursor: pointer;
  transition: color 0.15s, border-color 0.15s;
}
.sel-btn:hover { color: var(--text); border-color: var(--border-hi); }
.sel-delete {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 6px 16px; border-radius: 8px;
  background: var(--danger-bg); border: 1px solid rgba(255,122,122,0.3);
  color: var(--danger); font-size: 13px; font-weight: 600; cursor: pointer;
  transition: opacity 0.15s;
}
.sel-delete:disabled { opacity: 0.4; cursor: default; }
.sel-delete:not(:disabled):hover { opacity: 0.8; }

/* Bar slide-in transition */
.sel-bar-enter-active, .sel-bar-leave-active { transition: all 0.2s ease; }
.sel-bar-enter-from, .sel-bar-leave-to { opacity: 0; transform: translateY(-8px); }

.content { padding: 28px 32px; max-width: 1080px; width: 100%; margin: 0 auto; display: flex; flex-direction: column; gap: 24px; box-sizing: border-box; }
.mono { font-family: var(--font-mono); font-size: 10px; font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase; color: var(--text-mute); }

.title-row { display: flex; align-items: flex-end; justify-content: space-between; }
.page-title { font-size: 32px; font-weight: 600; letter-spacing: -0.8px; line-height: 1.1; margin: 6px 0 0; }
.page-sub { font-size: 13px; color: var(--text-dim); margin: 6px 0 0; max-width: 480px; }

.filter-bar { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.filter-group { display: flex; align-items: center; gap: 6px; }
.tag-group { gap: 6px; }
.filter-icon { color: var(--text-mute); }
.divider { width: 1px; height: 20px; background: var(--border); }
.spacer { flex: 1; }
.sort-toggle { display: flex; align-items: center; gap: 8px; }
.view-toggle { display: flex; align-items: center; gap: 8px; }
.view-btns { display: flex; gap: 2px; padding: 3px; background: var(--surface); border: 1px solid var(--border); border-radius: 8px; }
.view-btn { padding: 4px; border-radius: 5px; color: var(--text-mute); cursor: pointer; transition: all 0.15s; }
.view-btn.active { background: var(--surface-hi); color: var(--accent); }

.recipe-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.recipe-list { display: flex; flex-direction: column; gap: 10px; }

.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 80px 20px; gap: 12px; text-align: center; }
.empty-icon { width: 56px; height: 56px; border-radius: 16px; background: var(--surface); border: 1px solid var(--border); display: flex; align-items: center; justify-content: center; color: var(--text-dim); }
.empty-title { font-size: 16px; font-weight: 600; }
.empty-sub { font-size: 13px; color: var(--text-dim); max-width: 280px; }

@media (max-width: 960px) { .recipe-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 768px) { .topbar, .content { padding-left: 20px; padding-right: 20px; } .recipe-grid { grid-template-columns: 1fr; } }
</style>
