<template>
  <div class="mp-view">

    <!-- ── Household context bar ──────────────────────────────── -->
    <div class="context-bar">
      <Avatar :name="hh.current?.name || '?'" :color="hhColor" :size="30" :round="false" />
      <div class="hh-info">
        <div class="hh-name-row">
          <span class="hh-name">{{ hh.current?.name }}</span>
          <Pill v-if="isHhAdmin" tone="accent">{{ $t('household.roles.' + (hh.current?.role || 'member')) }}</Pill>
        </div>
        <span class="mono dim">{{ $t('household.memberCount', { count: hh.current?.member_count ?? 0 }) }}</span>
      </div>
      <!-- scope switch -->
      <div class="seg-ctrl">
        <button
          v-for="s in SCOPES" :key="s.id"
          class="seg-btn" :class="{ active: scope === s.id }"
          @click="setScope(s.id)"
        >
          <AppIcon :d="I[s.icon]" :size="15" :sw="2" />
          {{ $t('mealplanner.scope.' + s.id) }}
        </button>
      </div>
    </div>

    <!-- ── Title + view switch ─────────────────────────────────── -->
    <div class="title-row">
      <div>
        <div class="mono dim">{{ $t('mealplanner.title') }} · {{ visibleCount }} {{ visibleCount === 1 ? $t('mealplanner.plan') : $t('mealplanner.plans') }}{{ scope === 'household' ? ' · everyone' : '' }}</div>
        <h1 class="page-heading">{{ $t('mealplanner.heading') }}</h1>
      </div>
      <div class="seg-ctrl">
        <button
          v-for="v in VIEWS" :key="v.id"
          class="seg-btn accent-active" :class="{ active: view === v.id }"
          @click="view = v.id; selectedDay = null"
        >{{ $t('mealplanner.view.' + v.id) }}</button>
      </div>
    </div>

    <!-- ── Nav row ────────────────────────────────────────────── -->
    <div class="nav-row">
      <button class="icon-btn" @click="step(-1)"><AppIcon :d="I.chevL" :size="18" :sw="2.2" /></button>
      <button class="icon-btn" @click="step(1)"><AppIcon :d="I.chevR" :size="18" :sw="2.2" /></button>
      <button class="ghost-btn today-btn" @click="goToday">
        <AppIcon :d="I.calendar" :size="15" :sw="2">
          <circle cx="12" cy="14.5" r="2" fill="currentColor" stroke="none" />
        </AppIcon>
        {{ $t('mealplanner.today') }}
      </button>
      <span class="period-label">{{ periodLabel }}</span>
      <span class="flex1" />
      <template v-if="!readOnly && !selecting">
        <button class="ghost-btn" @click="selecting = true">
          <AppIcon :d="I.check" :size="15" :sw="2.2" />
          {{ $t('mealplanner.select') }}
        </button>
        <button class="primary-btn" @click="openEditor({ date: view === 'daily' ? ymd(cursor) : (selectedDay || ymd(todayDate)) })">
          <AppIcon :d="I.plus" :size="16" :sw="2.2" />
          {{ $t('mealplanner.addPlan') }}
        </button>
      </template>
      <Pill v-if="readOnly">{{ $t('mealplanner.readonly') }}</Pill>
    </div>

    <!-- ── Selection bar ─────────────────────────────────────── -->
    <div v-if="selecting" class="select-bar">
      <span class="select-count">{{ $t('mealplanner.selected', { n: selectedIds.size }) }}</span>
      <span class="select-hint">{{ $t('mealplanner.selectHint') }}</span>
      <span class="flex1" />
      <button class="ghost-btn" @click="exitSelect">{{ $t('global.cancel') }}</button>
      <button
        class="danger-btn"
        :disabled="!selectedIds.size"
        @click="selectedIds.size && (confirm = true)"
      >
        <AppIcon :d="I.trash" :size="15" :sw="2" />
        {{ $t('global.delete') }}
      </button>
    </div>

    <!-- ── Body ──────────────────────────────────────────────── -->
    <div class="body-scroll">

      <!-- Daily -->
      <div v-if="view === 'daily'" class="daily-wrap">
        <div
          class="daily-header"
          @contextmenu.prevent="!readOnly && !selecting && openEditor({ date: ymd(cursor) })"
        >
          <div class="day-badge" :class="{ today: isToday(cursor) }">
            <span class="day-badge-dow">{{ DOW_SHORT[cursor.getDay()] }}</span>
            <span class="day-badge-num">{{ cursor.getDate() }}</span>
          </div>
          <div>
            <div class="day-long-label">{{ fmtDayLong(cursor) }}</div>
            <div class="mono dim">
              <span v-if="isToday(cursor)" class="accent-text">Today · </span>
              {{ plansForDay(cursor).length }} {{ plansForDay(cursor).length === 1 ? $t('mealplanner.plan') : $t('mealplanner.plans') }}
            </div>
          </div>
        </div>

        <div v-if="plansForDay(cursor).length === 0" class="empty-day">
          <div class="empty-icon"><AppIcon :d="I.calendar" :size="22" :sw="1.6" /></div>
          <p>{{ readOnly ? $t('mealplanner.noPlansDay') : $t('mealplanner.emptyDay') }}</p>
          <button v-if="!readOnly" class="primary-btn" @click="openEditor({ date: ymd(cursor) })">
            <AppIcon :d="I.plus" :size="15" :sw="2.2" /> {{ $t('mealplanner.addMealPlan') }}
          </button>
        </div>
        <div v-else class="plan-list">
          <PlanCard
            v-for="p in plansForDay(cursor)" :key="p.id"
            :plan="p"
            :selecting="selecting"
            :selected="selectedIds.has(p.id)"
            :read-only="readOnly"
            draggable
            @click="onPlanClick(p)"
            @long-press="enterSelect(p.id)"
            @drag-start="dragId = p.id; dragDate = p.plan_date"
            @drag-end="dragId = null; dragDate = null; dragOverDay = null"
            @drop-on="onDropOn(p.id, p.plan_date)"
          />
          <button v-if="!readOnly && !selecting" class="add-day-btn" @click="openEditor({ date: ymd(cursor) })">
            <AppIcon :d="I.plus" :size="14" :sw="2.2" />
          </button>
        </div>
      </div>

      <!-- Weekly -->
      <div v-else-if="view === 'weekly'" class="week-grid">
        <div
          v-for="d in weekDays" :key="ymd(d)"
          class="week-col"
          :class="{ today: isToday(d), selected: selectedDay === ymd(d), 'drag-over': dragOverDay === ymd(d) && dragId }"
          @click="pickDay(d)"
          @contextmenu.prevent="!readOnly && !selecting && openEditor({ date: ymd(d) })"
        >
          <button class="week-col-header" @click="pickDay(d)">
            <span class="week-dow" :class="{ today: isToday(d) }">{{ DOW_SHORT[d.getDay()] }}</span>
            <span class="week-num" :class="{ today: isToday(d) }">{{ d.getDate() }}</span>
            <span class="flex1" />
            <span v-if="plansForDay(d).length" class="mono dim" :class="{ 'accent-text': isToday(d) }">{{ plansForDay(d).length }}</span>
          </button>
          <div class="week-col-body" @dragover.prevent="dragOverDay = ymd(d)" @drop.prevent="onDropDay(ymd(d))">
            <PlanCard
              v-for="p in plansForDay(d)" :key="p.id"
              :plan="p"
              :selecting="selecting"
              :selected="selectedIds.has(p.id)"
              :read-only="readOnly"
              @click="onPlanClick(p)"
              @long-press="enterSelect(p.id)"
              @drag-start="dragId = p.id; dragDate = p.plan_date"
              @drag-end="dragId = null; dragDate = null; dragOverDay = null"
              @drop-on="onDropOn(p.id, p.plan_date)"
            />
            <button v-if="!readOnly && !selecting" class="add-day-btn compact" @click.stop="openEditor({ date: ymd(d) })">
              <AppIcon :d="I.plus" :size="12" :sw="2.2" />
            </button>
          </div>
        </div>
      </div>

      <!-- Monthly -->
      <div v-else class="month-view">
        <div class="month-dow-row">
          <div v-for="h in dowHeaders" :key="h" class="month-dow">{{ h }}</div>
        </div>
        <div class="month-grid">
          <template v-for="(week, wi) in monthGrid" :key="wi">
            <div
              v-for="d in week" :key="ymd(d)"
              class="month-cell"
              :class="{
                today: isToday(d),
                selected: selectedDay === ymd(d),
                'other-month': d.getMonth() !== cursor.getMonth(),
                'drag-over': dragOverDay === ymd(d) && dragId,
              }"
              @click="pickDay(d)"
              @contextmenu.prevent="!readOnly && !selecting && openEditor({ date: ymd(d) })"
              @dragover.prevent="dragOverDay = ymd(d)"
              @drop.prevent="onDropDay(ymd(d))"
            >
              <div class="month-cell-header">
                <span class="month-num" :class="{ today: isToday(d) }">{{ d.getDate() }}</span>
                <span class="flex1" />
                <span v-if="plansForDay(d).length" class="mono" style="font-size:10px" :class="isToday(d) ? 'accent-text' : 'dim'">
                  {{ plansForDay(d).length }}
                </span>
              </div>
              <div class="month-cell-plans">
                <div v-for="p in plansForDay(d).slice(0, 3)" :key="p.id" @click.stop="onPlanClick(p)">
                  <PlanCard :plan="p" compact :selecting="selecting" :selected="selectedIds.has(p.id)" :read-only="readOnly"
                    @click="onPlanClick(p)" @long-press="enterSelect(p.id)" />
                </div>
                <span v-if="plansForDay(d).length > 3" class="more-label">
                  {{ $t('mealplanner.moreCount', { n: plansForDay(d).length - 3 }) }}
                </span>
              </div>
            </div>
          </template>
        </div>
      </div>

    </div><!-- /body-scroll -->

    <!-- ── Toast ─────────────────────────────────────────────── -->
    <Transition name="toast">
      <div v-if="toastMsg" class="toast">
        <span class="toast-dot" />{{ toastMsg }}
      </div>
    </Transition>

    <!-- ── Modals ─────────────────────────────────────────────── -->
    <Teleport to="body">

      <!-- Plan Editor -->
      <div v-if="editor" class="modal-overlay" @click.self="editor = null">
        <div class="modal" style="max-width:560px">
          <div class="modal-header">
            <div class="modal-icon accent-icon">
              <AppIcon :d="editor.plan ? I.pencil : I.plus" :size="18" :sw="2" />
            </div>
            <div class="flex1">
              <div class="modal-title">{{ editor.plan ? $t('mealplanner.editPlan') : $t('mealplanner.newPlan') }}</div>
              <div class="mono dim">{{ fmtDayLong(new Date(editorDate + 'T00:00:00')) }}</div>
            </div>
            <button class="icon-btn" @click="editor = null"><AppIcon :d="I.x" :size="16" /></button>
          </div>

          <div class="modal-body">
            <!-- Kind toggle -->
            <div class="seg-ctrl full">
              <button
                v-for="k in KINDS" :key="k.id"
                class="seg-btn flex1" :class="{ active: editorKind === k.id }"
                @click="editorKind = k.id"
              >
                <AppIcon :d="I[k.icon]" :size="15" :sw="2" />
                {{ $t('mealplanner.' + k.label) }}
              </button>
            </div>

            <!-- Recipe kind -->
            <template v-if="editorKind === 'recipe'">
              <div>
                <div class="field-label">{{ $t('mealplanner.recipe') }}</div>
                <button class="recipe-picker-btn" :class="{ open: pickerOpen }" @click="pickerOpen = !pickerOpen">
                  <template v-if="selectedRecipe">
                    <span class="recipe-glyph" :style="{ background: `${recipeTone(selectedRecipe)}22`, color: recipeTone(selectedRecipe) }">
                      {{ (selectedRecipe.name[0] || '?').toUpperCase() }}
                    </span>
                    <span class="flex1" style="font-size:14px;font-weight:600">{{ selectedRecipe.name }}</span>
                  </template>
                  <span v-else class="mute">{{ $t('mealplanner.chooseCookbook') }}</span>
                  <AppIcon :d="I.chevR" :size="16" :sw="2" />
                </button>
                <div v-if="pickerOpen" class="recipe-list">
                  <button
                    v-for="r in recipeStore.allItems" :key="r.id"
                    class="recipe-list-item" :class="{ active: editorRecipeId === r.id }"
                    @click="editorRecipeId = r.id; pickerOpen = false"
                  >
                    <span class="recipe-glyph sm" :style="{ background: `${recipeTone(r)}22`, color: recipeTone(r) }">
                      {{ (r.name[0] || '?').toUpperCase() }}
                    </span>
                    <div class="flex1" style="min-width:0">
                      <div style="font-size:13.5px;font-weight:600">{{ r.name }}</div>
                      <div class="desc-line">{{ r.description }}</div>
                    </div>
                    <AppIcon v-if="editorRecipeId === r.id" :d="I.check" :size="15" :sw="2.5" />
                  </button>
                  <div v-if="!recipeStore.allItems.length" class="mute" style="padding:14px;font-size:13px">
                    {{ $t('recipes.noRecipes') }}
                  </div>
                </div>
              </div>
              <div v-if="selectedRecipe" class="recipe-preview">
                <div class="field-label">{{ $t('mealplanner.fromTheRecipe') }}</div>
                <p class="recipe-preview-desc">{{ selectedRecipe.description }}</p>
              </div>
              <div>
                <div class="field-label">{{ $t('mealplanner.yourNotes') }}</div>
                <textarea v-model="editorNotes" class="field-textarea" rows="3"
                  :placeholder="$t('mealplanner.yourNotes') + '…'" />
              </div>
            </template>

            <!-- Manual kind -->
            <template v-else>
              <div>
                <div class="field-label">{{ $t('mealplanner.titleField') }}</div>
                <input v-model="editorTitle" class="field-input" :placeholder="$t('mealplanner.titleField')" autofocus />
              </div>
              <div>
                <div class="field-label">{{ $t('mealplanner.description') }}</div>
                <textarea v-model="editorDescription" class="field-textarea" rows="3"
                  :placeholder="$t('mealplanner.description') + '…'" />
              </div>
            </template>

            <!-- Date -->
            <div>
              <div class="field-label">{{ $t('mealplanner.date') }}</div>
              <input v-model="editorDate" type="date" class="field-input" style="color-scheme:dark" />
            </div>
          </div>

          <div class="modal-footer">
            <button v-if="editor.plan" class="ghost-btn danger"
              @click="doDeletePlan(editor.plan.id)">
              <AppIcon :d="I.trash" :size="15" :sw="2" /> {{ $t('global.delete') }}
            </button>
            <span class="flex1" />
            <button class="ghost-btn" @click="editor = null">{{ $t('global.cancel') }}</button>
            <button class="primary-btn" :disabled="!editorCanSave" @click="saveEditor">
              <AppIcon :d="I.check" :size="16" :sw="2.4" />
              {{ editor.plan ? $t('mealplanner.saveChanges') : $t('mealplanner.addPlan') }}
            </button>
          </div>
        </div>
      </div>

      <!-- Plan Detail -->
      <div v-if="detail" class="modal-overlay" @click.self="detail = null">
        <div class="modal" style="max-width:520px">
          <div class="detail-tone-bar" :style="{ background: detailTone }" />
          <div class="detail-header">
            <div class="detail-glyph" :style="{ background: `${detailTone}22`, color: detailTone }">
              <template v-if="detail.kind === 'recipe'">{{ (detail.recipe_name || 'R')[0].toUpperCase() }}</template>
              <AppIcon v-else :d="I.note" :size="20" :sw="1.8" />
            </div>
            <div class="flex1" style="min-width:0">
              <div class="detail-pills">
                <Pill :tone="detail.kind === 'recipe' ? 'accent' : 'neutral'">
                  {{ detail.kind === 'recipe' ? $t('mealplanner.recipe') : $t('mealplanner.note') }}
                </Pill>
                <span class="mono dim">{{ fmtDayLong(new Date(detail.plan_date + 'T00:00:00')) }}</span>
              </div>
              <h2 class="detail-title">{{ detail.kind === 'recipe' ? detail.recipe_name : detail.title }}</h2>
            </div>
            <button class="icon-btn" @click="detail = null"><AppIcon :d="I.x" :size="16" /></button>
          </div>
          <div class="modal-body">
            <div v-if="detail.kind === 'recipe' ? detail.recipe_description : detail.description">
              <div class="field-label">{{ detail.kind === 'recipe' ? $t('mealplanner.fromTheRecipe') : $t('mealplanner.description') }}</div>
              <p class="detail-text">{{ detail.kind === 'recipe' ? detail.recipe_description : detail.description }}</p>
            </div>
            <div v-if="detail.notes" class="notes-block">
              <div class="field-label">{{ $t('mealplanner.yourNotes') }}</div>
              <p class="detail-text">{{ detail.notes }}</p>
            </div>
            <p v-if="!detail.notes && !(detail.kind === 'recipe' ? detail.recipe_description : detail.description)" class="mute" style="font-size:13px">
              {{ $t('mealplanner.noDetails') }}
            </p>
            <div class="planned-by">
              <span class="user-dot-lg" :style="{ background: avatarColor(detail.user_id) }">
                {{ (detail.user_name || '?')[0].toUpperCase() }}
              </span>
              <span class="mono dim">
                {{ $t('mealplanner.plannedBy', { name: detail.user_name })}}
                {{ detail.user_id === auth.user?.id ? $t('mealplanner.you') : '' }}
              </span>
            </div>
          </div>
          <div class="modal-footer">
            <button v-if="detail.kind === 'recipe'" class="ghost-btn"
              @click="$router.push('/recipes/' + detail.recipe_id)">
              <AppIcon :d="I.external" :size="15" :sw="2" /> {{ $t('mealplanner.openRecipe') }}
            </button>
            <button v-if="!readOnly" class="ghost-btn danger" @click="doDeletePlan(detail.id)">
              <AppIcon :d="I.trash" :size="15" :sw="2" /> {{ $t('global.delete') }}
            </button>
            <span class="flex1" />
            <Pill v-if="readOnly">{{ $t('mealplanner.readonly') }}</Pill>
            <button v-if="!readOnly" class="primary-btn" @click="openEditor({ plan: detail }); detail = null">
              <AppIcon :d="I.pencil" :size="15" :sw="2" /> {{ $t('global.edit') }}
            </button>
          </div>
        </div>
      </div>

      <!-- Confirm delete -->
      <div v-if="confirm" class="modal-overlay" @click.self="confirm = false">
        <div class="modal" style="max-width:420px">
          <div class="modal-body">
            <div class="danger-icon"><AppIcon :d="I.trash" :size="20" :sw="2" /></div>
            <h2 class="modal-title" style="font-size:19px;margin-bottom:8px">
              {{ $t('global.delete') }} {{ selectedIds.size }} {{ selectedIds.size === 1 ? $t('mealplanner.plan') : $t('mealplanner.plans') }}?
            </h2>
            <p style="font-size:14px;color:var(--text-dim);line-height:1.5">
              This removes {{ selectedIds.size === 1 ? 'it' : 'them' }} from your planner. This can't be undone.
            </p>
            <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:22px">
              <button class="ghost-btn" @click="confirm = false">{{ $t('global.cancel') }}</button>
              <button class="primary-btn danger-primary" @click="deleteSelected">
                <AppIcon :d="I.trash" :size="15" :sw="2" /> {{ $t('global.delete') }}
              </button>
            </div>
          </div>
        </div>
      </div>

    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore, avatarColor, MODULES } from '../stores/auth'
import { useHouseholdStore } from '../stores/household'
import { useMealPlanStore } from '../stores/mealplan'
import { useRecipeStore } from '../stores/recipes'
import { I } from '../components/icons.js'
import AppIcon from '../components/AppIcon.vue'
import Pill from '../components/Pill.vue'
import Avatar from '../components/Avatar.vue'
import PlanCard from '../components/PlanCard.vue'

const { t } = useI18n()
const router = useRouter()
const auth        = useAuthStore()
const hh          = useHouseholdStore()
const planStore   = useMealPlanStore()
const recipeStore = useRecipeStore()

// ── Constants ─────────────────────────────────────────────────────────────────
const VIEWS  = [{ id: 'daily' }, { id: 'weekly' }, { id: 'monthly' }]
const SCOPES = [{ id: 'mine', icon: 'user' }, { id: 'household', icon: 'users' }]
const KINDS  = [{ id: 'recipe', icon: 'chef', label: 'fromRecipe' }, { id: 'manual', icon: 'note', label: 'manual' }]
const MONTHS  = ['January','February','March','April','May','June','July','August','September','October','November','December']
const DOW_SHORT = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']
const TONES = ['#c79bff','#ffb86b','#7cf2a0','#9bd9ff','#ff9ec7','#ff9466','#ffd166']

// ── Date helpers ──────────────────────────────────────────────────────────────
function today() { const d = new Date(); d.setHours(0,0,0,0); return d }
function ymd(d) {
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
}
function addDays(d, n) { const x = new Date(d); x.setDate(x.getDate()+n); return x }
function addMonths(d, n) { const x = new Date(d); x.setMonth(x.getMonth()+n, 1); return x }
function startOfWeek(d) {
  const x = new Date(d); x.setHours(0,0,0,0)
  const diff = (x.getDay() - 1 + 7) % 7   // Monday start
  x.setDate(x.getDate() - diff)
  return x
}
function isToday(d) { return ymd(d) === ymd(today()) }
function fmtDayLong(d) {
  return `${DOW_SHORT[d.getDay()]}, ${MONTHS[d.getMonth()]} ${d.getDate()}`
}
function recipeTone(r) { return TONES[(r?.id || 0) % TONES.length] }

// ── State ─────────────────────────────────────────────────────────────────────
const view        = ref('weekly')
const scope       = ref('mine')
const cursor      = ref(today())
const selecting   = ref(false)
const selectedIds = ref(new Set())
const selectedDay = ref(null)  // ymd string — highlighted day in weekly/monthly views
const editor      = ref(null)   // { plan?, date? }
const detail      = ref(null)
const confirm     = ref(false)
const toastMsg    = ref(null)
const dragId      = ref(null)
const dragDate    = ref(null)
const dragOverDay = ref(null)

// Editor fields
const editorKind        = ref('recipe')
const editorRecipeId    = ref(null)
const editorTitle       = ref('')
const editorDescription = ref('')
const editorNotes       = ref('')
const editorDate        = ref(ymd(today()))
const pickerOpen        = ref(false)
const todayDate         = today()

// ── Computed ──────────────────────────────────────────────────────────────────
const readOnly   = computed(() => scope.value === 'household')
const isHhAdmin  = computed(() => ['owner','admin'].includes(hh.current?.role))
const hhColor    = computed(() => {
  const colors = ['#c79bff','#ffb86b','#7cf2a0','#9bd9ff','#ff9ec7','#ffd166']
  return colors[((hh.current?.id || 1) - 1) % colors.length]
})
const visibleCount = computed(() => planStore.plans.length)

const selectedRecipe = computed(() =>
  recipeStore.allItems.find(r => r.id === editorRecipeId.value) || null
)
const editorCanSave = computed(() => {
  if (editorKind.value === 'recipe') return !!editorRecipeId.value
  return !!(editorTitle.value || '').trim()
})

const detailTone = computed(() => {
  if (!detail.value) return '#9ca0a8'
  if (detail.value.kind === 'recipe' && detail.value.recipe_id != null)
    return TONES[detail.value.recipe_id % TONES.length]
  return '#9ca0a8'
})

// ── Date range for current view ───────────────────────────────────────────────
const dateRange = computed(() => {
  if (view.value === 'daily') {
    const d = ymd(cursor.value)
    return { from: d, to: d }
  }
  if (view.value === 'weekly') {
    const s = startOfWeek(cursor.value)
    return { from: ymd(s), to: ymd(addDays(s, 6)) }
  }
  // monthly — include full grid
  const first = new Date(cursor.value.getFullYear(), cursor.value.getMonth(), 1)
  const gridStart = startOfWeek(first)
  const last = new Date(cursor.value.getFullYear(), cursor.value.getMonth() + 1, 0)
  const gridEnd = addDays(startOfWeek(last), 6)
  return { from: ymd(gridStart), to: ymd(gridEnd) }
})

const periodLabel = computed(() => {
  if (view.value === 'daily') return fmtDayLong(cursor.value)
  if (view.value === 'weekly') {
    const s = startOfWeek(cursor.value)
    const e = addDays(s, 6)
    if (s.getMonth() === e.getMonth())
      return `${MONTHS[s.getMonth()]} ${s.getDate()}–${e.getDate()}, ${e.getFullYear()}`
    return `${MONTHS[s.getMonth()].slice(0,3)} ${s.getDate()} – ${MONTHS[e.getMonth()].slice(0,3)} ${e.getDate()}, ${e.getFullYear()}`
  }
  return `${MONTHS[cursor.value.getMonth()]} ${cursor.value.getFullYear()}`
})

const weekDays = computed(() => {
  const s = startOfWeek(cursor.value)
  return Array.from({ length: 7 }, (_, i) => addDays(s, i))
})

const monthGrid = computed(() => {
  const yr = cursor.value.getFullYear(), mo = cursor.value.getMonth()
  const first = new Date(yr, mo, 1)
  const gridStart = startOfWeek(first)
  const weeks = []
  let d = new Date(gridStart)
  for (let w = 0; w < 6; w++) {
    const row = []
    for (let i = 0; i < 7; i++) { row.push(new Date(d)); d = addDays(d, 1) }
    weeks.push(row)
    if (d.getMonth() !== mo && w >= 4) break
  }
  return weeks
})

const dowHeaders = computed(() =>
  Array.from({ length: 7 }, (_, i) => DOW_SHORT[(1 + i) % 7])
)

// ── Plan helpers ──────────────────────────────────────────────────────────────
function plansForDay(d) {
  const dateStr = ymd(d)
  return planStore.plans
    .filter(p => p.plan_date === dateStr)
    .sort((a, b) => (a.sort_order ?? 0) - (b.sort_order ?? 0))
}

// ── Load ──────────────────────────────────────────────────────────────────────
async function loadPlans() {
  if (!hh.current) return
  try {
    await planStore.load(hh.current.id, dateRange.value.from, dateRange.value.to, scope.value)
  } catch {}
}

watch([view, scope, () => cursor.value?.getTime()], loadPlans, { immediate: true })

// ── Navigation ────────────────────────────────────────────────────────────────
function step(dir) {
  if (view.value === 'daily')   cursor.value = addDays(cursor.value, dir)
  else if (view.value === 'weekly') cursor.value = addDays(cursor.value, dir * 7)
  else cursor.value = addMonths(cursor.value, dir)
}
function goToday()   { cursor.value = today(); selectedDay.value = null }
function pickDay(d)  { selectedDay.value = ymd(d) }
function setScope(s) { scope.value = s; exitSelect() }

// ── Toast ─────────────────────────────────────────────────────────────────────
function flash(msg) {
  toastMsg.value = msg
  setTimeout(() => { toastMsg.value = null }, 1900)
}

// ── Editor ────────────────────────────────────────────────────────────────────
function openEditor(opts) {
  const plan = opts.plan
  if (plan) {
    editorKind.value        = plan.kind || 'recipe'
    editorRecipeId.value    = plan.recipe_id || null
    editorTitle.value       = plan.title || ''
    editorDescription.value = plan.description || ''
    editorNotes.value       = plan.notes || ''
    editorDate.value        = plan.plan_date
  } else {
    editorKind.value        = 'recipe'
    editorRecipeId.value    = null
    editorTitle.value       = ''
    editorDescription.value = ''
    editorNotes.value       = ''
    editorDate.value        = opts.date || ymd(today())
  }
  pickerOpen.value = false
  editor.value = opts
  // lazy-load recipes
  if (recipeStore.allItems.length === 0) recipeStore.loadAll()
}

async function saveEditor() {
  if (!hh.current || !editorCanSave.value) return
  const payload = {
    id: editor.value?.plan?.id,
    plan_date: editorDate.value,
    kind: editorKind.value,
    notes: editorNotes.value,
  }
  if (editorKind.value === 'recipe') {
    payload.recipe_id = editorRecipeId.value
    payload.title = null; payload.description = null
  } else {
    payload.title = editorTitle.value.trim()
    payload.description = editorDescription.value
    payload.recipe_id = null
  }
  try {
    if (payload.id) {
      await planStore.update(payload.id, payload)
      flash(t('mealplanner.planUpdated'))
    } else {
      await planStore.create(hh.current.id, payload)
      flash(t('mealplanner.planAdded'))
    }
    editor.value = null
  } catch (e) {
    flash(e.message)
  }
}

async function doDeletePlan(id) {
  try {
    await planStore.remove(id)
    flash(t('mealplanner.planDeleted'))
    editor.value = null
    detail.value = null
  } catch (e) { flash(e.message) }
}

// ── Selection ─────────────────────────────────────────────────────────────────
function enterSelect(id) {
  if (readOnly.value) return
  selecting.value = true
  selectedIds.value = new Set([id])
}
function toggleSelect(id) {
  const s = new Set(selectedIds.value)
  s.has(id) ? s.delete(id) : s.add(id)
  selectedIds.value = s
}
function exitSelect() {
  selecting.value = false
  selectedIds.value = new Set()
}
function onPlanClick(p) {
  if (selecting.value) toggleSelect(p.id)
  else detail.value = p
}

async function deleteSelected() {
  const ids = [...selectedIds.value]
  try {
    const res = await planStore.bulkRemove(ids)
    flash(t('mealplanner.plansDeleted', { n: res.deleted.length }))
  } catch(e) { flash(e.message) }
  exitSelect()
  confirm.value = false
}

// ── Drag & drop reorder / move ────────────────────────────────────────────────
async function onDropOn(targetId, targetDate) {
  const src     = dragId.value
  const srcDate = dragDate.value
  dragId.value      = null
  dragDate.value    = null
  dragOverDay.value = null
  if (!src || src === targetId || !hh.current) return

  if (srcDate && srcDate !== targetDate) {
    // Moving to a different day
    try {
      await planStore.update(src, { plan_date: targetDate })
      flash(t('mealplanner.planUpdated'))
    } catch (e) { flash(e.message) }
    return
  }

  // Same-day reorder
  const dayPlans = plansForDay(new Date(targetDate + 'T00:00:00'))
  const ids = dayPlans.map(p => p.id)
  const fromIdx = ids.indexOf(src)
  const toIdx   = ids.indexOf(targetId)
  if (fromIdx < 0 || toIdx < 0) return
  ids.splice(toIdx, 0, ids.splice(fromIdx, 1)[0])
  try { await planStore.reorder(hh.current.id, targetDate, ids) } catch {}
}

async function onDropDay(targetDate) {
  const src     = dragId.value
  const srcDate = dragDate.value
  dragId.value      = null
  dragDate.value    = null
  dragOverDay.value = null
  if (!src || !hh.current || srcDate === targetDate) return
  try {
    await planStore.update(src, { plan_date: targetDate })
    flash(t('mealplanner.planUpdated'))
  } catch (e) { flash(e.message) }
}
</script>

<style scoped>
.mp-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  position: relative;
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-sans);
}

/* Context bar */
.context-bar {
  padding: 18px 32px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 14px;
  flex-shrink: 0;
}
.hh-info { flex: 1; }
.hh-name-row { display: flex; align-items: center; gap: 8px; }
.hh-name { font-size: 16px; font-weight: 600; letter-spacing: -0.2px; }

/* Segmented control */
.seg-ctrl {
  display: flex;
  gap: 3px;
  padding: 3px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
}
.seg-ctrl.full { width: 100%; }
.seg-btn {
  padding: 7px 13px;
  border-radius: 7px;
  border: 0;
  cursor: pointer;
  background: transparent;
  color: var(--text-dim);
  font-family: var(--font-sans);
  font-size: 13px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  transition: background 160ms ease, color 160ms ease;
}
.seg-btn:hover { color: var(--text); }
.seg-btn.active { background: var(--surface-hi); color: var(--accent); }
.seg-btn.accent-active.active { background: var(--accent); color: var(--accent-ink); }
.seg-btn.flex1 { flex: 1; justify-content: center; }

/* Title row */
.title-row {
  padding: 22px 32px 16px;
  flex-shrink: 0;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
}
.page-heading {
  margin: 6px 0 0;
  font-size: 30px;
  font-weight: 600;
  letter-spacing: -0.8px;
  line-height: 1.1;
}

/* Nav row */
.nav-row {
  padding: 0 32px 18px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}
.period-label { font-size: 18px; font-weight: 600; letter-spacing: -0.3px; margin-left: 4px; white-space: nowrap; }

/* Selection bar */
.select-bar {
  margin: 0 32px 14px;
  padding: 10px 14px;
  border-radius: 12px;
  background: var(--surface);
  border: 1px solid rgba(199,155,255,0.33);
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}
.select-count { font-size: 14px; font-weight: 600; }
.select-hint  { font-size: 12px; color: var(--text-dim); }

/* Buttons */
.icon-btn {
  width: 38px; height: 38px;
  border-radius: 10px;
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--text);
  cursor: pointer;
  display: inline-flex; align-items: center; justify-content: center;
}
.icon-btn:hover { border-color: var(--border-hi); }

.ghost-btn {
  padding: 9px 14px;
  border-radius: 10px;
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--text);
  cursor: pointer;
  font-family: var(--font-sans);
  font-size: 13px;
  font-weight: 600;
  display: inline-flex; align-items: center; gap: 7px;
}
.ghost-btn:hover { border-color: var(--border-hi); }
.ghost-btn.danger { color: var(--danger); border-color: rgba(255,122,122,0.3); background: rgba(255,122,122,0.06); }
.ghost-btn.today-btn { width: auto; }

.primary-btn {
  padding: 9px 16px;
  border-radius: 10px;
  background: var(--accent);
  color: var(--accent-ink);
  border: 0;
  cursor: pointer;
  font-family: var(--font-sans);
  font-size: 13px;
  font-weight: 600;
  display: inline-flex; align-items: center; gap: 7px;
  box-shadow: 0 10px 24px -10px var(--accent);
}
.primary-btn:disabled { background: var(--surface-hi); color: var(--text-mute); box-shadow: none; cursor: not-allowed; }
.primary-btn.danger-primary { background: var(--danger); color: #1a0707; box-shadow: 0 10px 24px -10px var(--danger); }

.danger-btn {
  padding: 9px 14px;
  border-radius: 10px;
  border: 1px solid transparent;
  cursor: pointer;
  font-family: var(--font-sans);
  font-size: 13px;
  font-weight: 600;
  display: inline-flex; align-items: center; gap: 7px;
  background: rgba(255,122,122,0.12);
  color: var(--danger);
  border-color: rgba(255,122,122,0.35);
}
.danger-btn:disabled { background: var(--surface-hi); color: var(--text-mute); border-color: var(--border); cursor: not-allowed; }

/* Body scroll */
.body-scroll { flex: 1; overflow: auto; padding: 0 32px 32px; }

/* Daily */
.daily-wrap { max-width: 720px; margin: 0 auto; }
.daily-header { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.day-badge {
  width: 54px; height: 54px;
  border-radius: 14px;
  flex-shrink: 0;
  background: var(--surface);
  border: 1px solid var(--border);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.day-badge.today { background: var(--accent); border-color: var(--accent); color: var(--accent-ink); }
.day-badge-dow {
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  opacity: 0.8;
}
.day-badge-num { font-size: 22px; font-weight: 700; line-height: 1; }
.day-long-label { font-size: 18px; font-weight: 600; letter-spacing: -0.3px; }

.empty-day {
  padding: 44px 16px;
  border: 1px dashed var(--border);
  border-radius: 16px;
  display: flex; flex-direction: column; align-items: center; gap: 12px;
  color: var(--text-dim); text-align: center;
}
.empty-icon {
  width: 44px; height: 44px;
  border-radius: 13px;
  background: var(--surface);
  color: var(--text-mute);
  display: flex; align-items: center; justify-content: center;
}
.empty-day p { margin: 0; font-size: 14px; }

.plan-list { display: flex; flex-direction: column; gap: 10px; }

.add-day-btn {
  width: 100%;
  padding: 9px;
  border-radius: 10px;
  background: transparent;
  border: 1px dashed var(--border-hi);
  color: var(--text-dim);
  cursor: pointer;
  font-family: var(--font-sans);
  font-size: 12.5px;
  font-weight: 500;
  display: flex; align-items: center; justify-content: center; gap: 6px;
}
.add-day-btn:hover { color: var(--accent); border-color: rgba(199,155,255,0.4); }
.add-day-btn.compact { padding: 5px; font-size: 11px; border-radius: 8px; }

/* Weekly */
.week-grid {
  display: grid;
  /* minmax(0, 1fr) — NOT plain 1fr. A plain 1fr track cannot shrink below its
     content's min-content width, so long recipe titles blew the tracks past the
     container and pushed whole days off-screen on narrow viewports. */
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 10px;
  min-height: 520px;
}
.week-col {
  display: flex;
  flex-direction: column;
  min-width: 0;          /* let the column shrink instead of forcing the track wider */
  gap: 8px;
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 10px;
}
.week-col.today     { }
.week-col.selected  { background: rgba(199,155,255,0.09); border-color: rgba(199,155,255,0.55); box-shadow: 0 0 0 1px rgba(199,155,255,0.3) inset; }
.week-col.drag-over { background: rgba(199,155,255,0.07); border-color: rgba(199,155,255,0.45); outline: 2px dashed rgba(199,155,255,0.45); outline-offset: -1px; }

.week-col-header {
  display: flex;
  align-items: center;
  gap: 8px;
  background: transparent;
  border: 0;
  cursor: pointer;
  color: var(--text);
  padding: 2px 2px 6px;
  text-align: left;
  border-bottom: 1px solid var(--border);
}
.week-dow {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text-mute);
  letter-spacing: 0.5px;
  text-transform: uppercase;
}
.week-dow.today, .week-num.today { color: var(--accent); }
.week-num {
  width: 22px; height: 22px;
  border-radius: 7px;
  font-size: 12px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  background: transparent;
}
.week-num.today { background: var(--accent); color: var(--accent-ink); }
.week-col-body { display: flex; flex-direction: column; gap: 6px; flex: 1; min-width: 0; }

/* Monthly */
.month-dow-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8px;
  margin-bottom: 8px;
}
.month-dow {
  text-align: center;
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text-mute);
  letter-spacing: 0.5px;
  text-transform: uppercase;
  padding: 2px 0;
}
.month-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8px;
}
.month-cell {
  min-height: 116px;
  border-radius: 12px;
  padding: 8px;
  cursor: pointer;
  background: var(--bg2);
  border: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 5px;
  transition: border-color 0.15s;
}
.month-cell:hover { border-color: var(--border-hi); }
.month-cell.today     { }
.month-cell.selected  { background: rgba(199,155,255,0.11); border-color: rgba(199,155,255,0.6); box-shadow: 0 0 0 1px rgba(199,155,255,0.25) inset; }
.month-cell.drag-over { background: rgba(199,155,255,0.07); border-color: rgba(199,155,255,0.45); outline: 2px dashed rgba(199,155,255,0.45); outline-offset: -1px; }
.month-cell.other-month { opacity: 0.42; }
.month-cell-header { display: flex; align-items: center; gap: 6px; }
.month-num {
  width: 22px; height: 22px;
  border-radius: 7px;
  font-size: 12px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}
.month-num.today { background: var(--accent); color: var(--accent-ink); }
.month-cell-plans { display: flex; flex-direction: column; gap: 4px; }
.more-label { font-size: 10.5px; color: var(--text-dim); font-family: var(--font-mono); padding-left: 2px; }

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; z-index: 200;
  display: flex; align-items: center; justify-content: center;
  padding: 28px;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(3px);
}
.modal {
  position: relative;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 20px;
  box-shadow: 0 30px 80px rgba(0,0,0,0.6);
}
.modal-header {
  padding: 18px 22px;
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 12px;
}
.modal-title { font-size: 17px; font-weight: 600; letter-spacing: -0.3px; }
.modal-body { padding: 22px; display: flex; flex-direction: column; gap: 18px; }
.modal-footer {
  padding: 16px 22px;
  border-top: 1px solid var(--border);
  display: flex; align-items: center; gap: 10px;
}

.modal-icon {
  width: 36px; height: 36px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.accent-icon { background: var(--accent-dim); color: var(--accent); }
.danger-icon {
  width: 44px; height: 44px;
  border-radius: 12px;
  background: rgba(255,122,122,0.12); color: var(--danger);
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 14px;
}

/* Field */
.field-label {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text-mute);
  letter-spacing: 0.5px;
  text-transform: uppercase;
  margin-bottom: 8px;
}
.field-input, .field-textarea {
  width: 100%;
  box-sizing: border-box;
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: 12px;
  padding: 11px 14px;
  color: var(--text);
  font-family: var(--font-sans);
  font-size: 14px;
  outline: none;
  transition: border-color 0.15s;
}
.field-input:focus, .field-textarea:focus { border-color: var(--accent); }
.field-textarea { resize: vertical; line-height: 1.5; min-height: 64px; }

/* Recipe picker */
.recipe-picker-btn {
  width: 100%;
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: 12px;
  padding: 11px 14px;
  cursor: pointer;
  text-align: left;
  display: flex; align-items: center; gap: 12px;
  color: var(--text);
  font-family: var(--font-sans);
  transition: border-color 0.15s;
}
.recipe-picker-btn:hover, .recipe-picker-btn.open { border-color: var(--accent); }
.recipe-glyph {
  width: 30px; height: 30px;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 13px;
  flex-shrink: 0;
}
.recipe-glyph.sm { width: 28px; height: 28px; font-size: 12px; }
.recipe-list {
  margin-top: 8px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  max-height: 220px;
  overflow-y: auto;
}
.recipe-list-item {
  width: 100%;
  padding: 10px 14px;
  background: transparent;
  border: 0;
  border-top: 1px solid var(--border);
  cursor: pointer;
  text-align: left;
  display: flex; align-items: center; gap: 12px;
  color: var(--text);
  font-family: var(--font-sans);
}
.recipe-list-item:first-child { border-top: 0; }
.recipe-list-item:hover, .recipe-list-item.active { background: var(--accent-dim); }
.desc-line {
  font-size: 11.5px;
  color: var(--text-dim);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.recipe-preview {
  padding: 12px 14px;
  border-radius: 12px;
  background: var(--surface);
  border: 1px solid var(--border);
}
.recipe-preview-desc { margin: 6px 0 0; font-size: 13px; color: var(--text-dim); line-height: 1.5; }

/* Detail modal */
.detail-tone-bar { height: 8px; border-radius: 20px 20px 0 0; }
.detail-header {
  padding: 20px 22px 0;
  display: flex; align-items: flex-start; gap: 14px;
}
.detail-glyph {
  width: 44px; height: 44px;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 18px;
  flex-shrink: 0;
}
.detail-pills { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.detail-title { margin: 0; font-size: 22px; font-weight: 600; letter-spacing: -0.5px; line-height: 1.15; }
.detail-text { margin: 6px 0 0; font-size: 14px; color: var(--text); line-height: 1.55; }
.notes-block {
  padding: 12px 14px;
  border-radius: 12px;
  background: var(--surface);
  border: 1px solid var(--border);
}
.planned-by { display: flex; align-items: center; gap: 8px; }
.user-dot-lg {
  width: 22px; height: 22px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700;
  color: var(--accent-ink);
  flex-shrink: 0;
}

/* Utility */
.mono  { font-family: var(--font-mono); font-size: 10px; font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase; }
.dim   { color: var(--text-mute); }
.mute  { color: var(--text-mute); }
.accent-text { color: var(--accent); font-weight: 600; }
.flex1 { flex: 1; }

/* Toast */
.toast {
  position: absolute;
  left: 50%; bottom: 24px;
  transform: translateX(-50%);
  background: var(--surface-hi);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 11px 16px;
  font-size: 13px;
  display: flex; align-items: center; gap: 10px;
  box-shadow: 0 12px 30px rgba(0,0,0,0.4);
  z-index: 60;
  white-space: nowrap;
  pointer-events: none;
}
.toast-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--accent);
  flex-shrink: 0;
}
.toast-enter-active, .toast-leave-active { transition: opacity 0.2s, transform 0.2s; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(8px); }

/* Mobile */
@media (max-width: 768px) {
  .context-bar, .title-row, .nav-row, .body-scroll { padding-left: 16px; padding-right: 16px; }
  .week-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .month-grid { grid-template-columns: repeat(7, minmax(0, 1fr)); }
  .month-cell { min-height: 60px; padding: 4px; }
  .select-bar { margin: 0 16px 10px; }
  .title-row { flex-direction: column; align-items: flex-start; }
  /* Wrap the header rows — previously "Add plan" and the scope switch were
     clipped off the right edge with no horizontal scroll to reach them. */
  .context-bar { flex-wrap: wrap; }
  .context-bar .seg-ctrl { width: 100%; }
  .context-bar .seg-btn { flex: 1; justify-content: center; }
  .nav-row { flex-wrap: wrap; row-gap: 10px; }
  .nav-row .flex1 { flex-basis: 100%; height: 0; }
}

@media (max-width: 520px) {
  /* One day per row: at phone widths a 2-up week is unreadable */
  .week-grid { grid-template-columns: minmax(0, 1fr); min-height: 0; }
  .week-col { min-height: 96px; }
}
</style>
