<template>
  <div class="recipe-create-view">
    <!-- Topbar -->
    <div class="topbar">
      <AppButton variant="ghost" size="sm" @click="cancel">← {{ $t('global.cancel') }}</AppButton>
      <div class="topbar-meta">
        <div class="mono">{{ isEdit ? $t('recipes.edit') : $t('recipes.newRecipe') }}</div>
        <div class="topbar-draft">{{ form.name || $t('recipes.untitledDraft') }}</div>
      </div>
      <span class="spacer" />
      <AppButton variant="outline" size="sm" @click="save(false)" :disabled="saving">{{ $t('recipes.saveDraft') }}</AppButton>
      <AppButton size="sm" @click="save(true)" :disabled="saving || !canPublish">
        <AppIcon :d="I.check" :size="14" /> {{ saving ? $t('recipes.saving') : $t('recipes.publish') }}
      </AppButton>
    </div>

    <div class="content">
      <!-- Import from URL panel -->
      <div class="import-panel">
        <div class="import-glow" />
        <div class="import-header">
          <div class="import-icon"><AppIcon :d="I.link" :size="20" /></div>
          <div class="import-copy">
            <div class="import-title">{{ $t('recipes.importFrom') }}</div>
            <div class="import-sub">{{ $t('recipes.importFromDesc') }}</div>
          </div>
          <Pill tone="accent">{{ $t('recipes.importBeta') }}</Pill>
        </div>
        <div class="import-input-row">
          <div class="url-field" :class="{ focused: urlFocused }">
            <AppIcon :d="I.globe" :size="16" class="url-icon" />
            <input
              v-model="importUrl" type="url" placeholder="https://..."
              class="url-input"
              @focus="urlFocused = true" @blur="urlFocused = false"
              @keydown.enter="importFromUrl"
            />
          </div>
          <AppButton @click="importFromUrl" :disabled="importing || !importUrl.trim()">
            <AppIcon :d="I.chevR" :size="14" /> {{ importing ? $t('recipes.importing') : $t('recipes.importBtn') }}
          </AppButton>
        </div>
        <div v-if="importError" class="import-error">{{ importError }}</div>
      </div>

      <!-- Divider -->
      <div class="or-divider">
        <span class="or-line" />
        <div class="mono">{{ $t('recipes.orFillManually') }}</div>
        <span class="or-line" />
      </div>

      <!-- Restricted notice -->
      <div v-if="isRestricted" class="restricted-notice">
        <AppIcon :d="I.lock" :size="14" />
        {{ $t('household.settings.restrictedNoCreate') }}
      </div>

      <!-- Form: two columns -->
      <div class="form-grid" :class="{ 'form-disabled': isRestricted }">
        <!-- LEFT: basics -->
        <div class="form-left">
          <div>
            <div class="field-label mono">{{ $t('recipes.coverPhoto') }}</div>
            <div class="cover-slot">
              <ImageSlot v-model="form.image_url" deferred @file="pendingImageFile = $event" />
            </div>
            <div class="cover-hint mono">{{ $t('recipes.coverHint') }}</div>
          </div>

          <Field v-model="form.name" :label="$t('recipes.name')" :placeholder="$t('recipes.namePlaceholder')" />

          <div class="textarea-field">
            <div class="field-label mono">{{ $t('recipes.description') }}</div>
            <textarea v-model="form.description" class="desc-textarea" :placeholder="$t('recipes.descriptionPlaceholder')" rows="3" />
          </div>

          <!-- Tags -->
          <div>
            <div class="field-label mono">{{ $t('recipes.tagsLabel') }}</div>
            <div class="tags-row">
              <div v-for="tag in form.tags" :key="tag" class="tag-pill">
                {{ tag }}
                <button class="tag-remove" @click="removeTag(tag)"><AppIcon :d="I.x" :size="10" :sw="2.4" /></button>
              </div>
              <div class="tag-add" v-if="!addingTag" @click="addingTag = true">
                <AppIcon :d="I.plus" :size="11" :sw="2.4" /> {{ $t('recipes.addTag') }}
              </div>
              <input
                v-else v-model="newTagInput" class="tag-input"
                :placeholder="$t('recipes.tagNamePlaceholder')"
                @keydown.enter="addTag" @keydown.escape="addingTag = false"
                @blur="addTag" ref="tagInputRef" autofocus
              />
            </div>
          </div>

          <!-- Time & servings -->
          <div>
            <div class="field-label mono">{{ $t('recipes.timeServings') }}</div>
            <div class="meta-grid">
              <Field v-model="form.prep_time" :label="$t('recipes.prep')" :placeholder="$t('recipes.prepPlaceholder')" />
              <Field v-model="form.cook_time" :label="$t('recipes.cook')" :placeholder="$t('recipes.cookPlaceholder')" />
              <div class="srv-stepper-field">
                <div class="field-label mono">{{ $t('recipes.servings') }}</div>
                <div class="srv-stepper-row">
                  <button type="button" class="srv-btn" @click="form.servings = Math.max(1, (form.servings || 1) - 1)" :disabled="!form.servings || form.servings <= 1">−</button>
                  <span class="srv-num">{{ form.servings || '–' }}</span>
                  <button type="button" class="srv-btn" @click="form.servings = (Number(form.servings) || 0) + 1">+</button>
                </div>
              </div>
              <div class="select-field">
                <div class="field-label mono" style="margin-bottom:6px;">{{ $t('recipes.difficulty') }}</div>
                <select v-model="form.difficulty" class="diff-select">
                  <option value="">–</option>
                  <option v-for="d in DIFFICULTIES" :key="d" :value="d">{{ d }}</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Nutrition -->
          <div>
            <div class="field-label mono">{{ $t('recipes.nutrition') }}</div>
            <div class="cal-row">
              <Field v-model="form.calories" :label="$t('recipes.caloriesLabel')" :placeholder="$t('recipes.caloriesPlaceholder')" type="number" />
              <div class="unit-select-wrap">
                <span class="unit-select-label">{{ $t('recipes.per') }}</span>
                <select v-model="form.calories_unit" class="unit-select">
                  <option value="100g">{{ $t('recipes.per100g') }}</option>
                  <option value="serving">{{ $t('recipes.perServing') }}</option>
                </select>
              </div>
            </div>
          </div>

          <ToggleRow :icon="I.globe" :label="$t('recipes.publicRecipe')" :on="form.is_public" centered @change="form.is_public = $event" />
        </div>

        <!-- RIGHT: ingredients + steps -->
        <div class="form-right">

          <!-- ── Ingredients (multi-section, draggable) ─────────────────── -->
          <div>
            <div class="right-header">
              <h3 class="right-title">{{ $t('recipes.ingredients') }}</h3>
              <div class="right-header-actions">
                <div class="mono">{{ totalIngredients }}</div>
                <button class="add-section-btn" @click="addSection">
                  <AppIcon :d="I.plus" :size="12" :sw="2.4" /> {{ $t('recipes.addSection') }}
                </button>
              </div>
            </div>

            <div class="sections-editor">
              <div
                v-for="(section, si) in form.ingredientSections"
                :key="si"
                class="section-block"
              >
                <!-- Section header -->
                <div class="section-header">
                  <input
                    v-model="section.name"
                    class="section-name-input"
                    :placeholder="form.ingredientSections.length === 1
                      ? t('recipes.sectionNameOptional')
                      : t('recipes.sectionNameN', { n: si + 1 })"
                  />
                  <button v-if="form.ingredientSections.length > 1" class="section-del-btn" @click="removeSection(si)">
                    <AppIcon :d="I.x" :size="12" />
                  </button>
                </div>

                <!-- Ingredient rows -->
                <div
                  class="ing-list"
                  @dragover.prevent="ingDragOverList(si, $event)"
                  @drop.prevent="ingDropList(si, $event)"
                >
                  <div
                    v-for="(ing, ii) in section.items"
                    :key="ii"
                    class="ing-row"
                    :class="{
                      divide:      ii > 0,
                      'ing-dragging':   isIngDragging(si, ii),
                      'ing-drop-above': isIngDropAbove(si, ii),
                    }"
                    draggable="true"
                    @dragstart="ingDragStart(si, ii, $event)"
                    @dragend="ingDragEnd"
                    @dragover.prevent.stop="ingDragOverItem(si, ii, $event)"
                    @dragleave.stop="ingDragLeaveItem"
                    @drop.prevent.stop="ingDropItem(si, ii, $event)"
                  >
                    <span class="drag-handle" title="Drag to reorder">
                      <svg width="12" height="14" viewBox="0 0 12 14" fill="currentColor">
                        <circle cx="3" cy="3" r="1.2"/><circle cx="9" cy="3" r="1.2"/>
                        <circle cx="3" cy="7" r="1.2"/><circle cx="9" cy="7" r="1.2"/>
                        <circle cx="3" cy="11" r="1.2"/><circle cx="9" cy="11" r="1.2"/>
                      </svg>
                    </span>
                    <input v-model="ing.name" class="ing-name-input" :placeholder="$t('recipes.ingredientNamePlaceholder')" />
                    <input v-model="ing.quantity" class="ing-qty-input" :placeholder="$t('recipes.qtyPlaceholder')" />
                    <button class="row-del" @click="removeIngredient(si, ii)">
                      <AppIcon :d="I.x" :size="13" />
                    </button>
                  </div>

                  <!-- Bottom drop zone (drop after last item) -->
                  <div
                    class="list-drop-end"
                    :class="{ 'drop-end-active': isIngDropEnd(si) }"
                    @dragover.prevent.stop="ingDragOverEnd(si, $event)"
                    @dragleave.stop="ingDropTarget = null"
                    @drop.prevent.stop="ingDropEnd(si, $event)"
                  />

                  <button class="add-row" @click="addIngredient(si)">
                    <AppIcon :d="I.plus" :size="14" :sw="2.4" /> {{ $t('recipes.addIngredient') }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- ── Methods (draggable steps) ──────────────────────────────── -->
          <div>
            <div class="right-header">
              <h3 class="right-title">{{ $t('recipes.methods') }}</h3>
              <button class="add-method-btn" @click="addMethod">
                <AppIcon :d="I.plus" :size="12" :sw="2.4" /> {{ $t('recipes.addMethod') }}
              </button>
            </div>
            <div class="methods-editor">
              <div v-for="(method, mi) in form.methods" :key="mi" class="method-block">
                <div class="method-header">
                  <input
                    v-model="method.name"
                    class="method-name-input"
                    :placeholder="form.methods.length === 1 ? t('recipes.methodNameOptional') : t('recipes.methodNameN', { n: mi + 1 })"
                  />
                  <button class="method-del-btn" @click="removeMethod(mi)">
                    <AppIcon :d="I.x" :size="12" />
                  </button>
                </div>

                <div
                  class="method-steps"
                  @dragover.prevent="stepDragOverList(mi, $event)"
                  @drop.prevent="stepDropList(mi, $event)"
                >
                  <div
                    v-for="(step, sti) in method.steps"
                    :key="sti"
                    class="step-row"
                    :class="{
                      'step-empty':      !step,
                      'step-dragging':   isStepDragging(mi, sti),
                      'step-drop-above': isStepDropAbove(mi, sti),
                    }"
                    draggable="true"
                    @dragstart="stepDragStart(mi, sti, $event)"
                    @dragend="stepDragEnd"
                    @dragover.prevent.stop="stepDragOverItem(mi, sti, $event)"
                    @dragleave.stop="stepDragLeaveItem"
                    @drop.prevent.stop="stepDropItem(mi, sti, $event)"
                  >
                    <span class="drag-handle step-drag-handle" title="Drag to reorder">
                      <svg width="10" height="12" viewBox="0 0 10 12" fill="currentColor">
                        <circle cx="2.5" cy="2" r="1.1"/><circle cx="7.5" cy="2" r="1.1"/>
                        <circle cx="2.5" cy="6" r="1.1"/><circle cx="7.5" cy="6" r="1.1"/>
                        <circle cx="2.5" cy="10" r="1.1"/><circle cx="7.5" cy="10" r="1.1"/>
                      </svg>
                    </span>
                    <div class="step-num">{{ sti + 1 }}</div>
                    <textarea
                      v-model="method.steps[sti]"
                      class="step-input"
                      :placeholder="t('recipes.stepPlaceholder', { n: sti + 1 })"
                      rows="2"
                    />
                    <button class="row-del" @click="removeStep(mi, sti)">
                      <AppIcon :d="I.x" :size="13" />
                    </button>
                  </div>

                  <!-- Bottom drop zone -->
                  <div
                    class="list-drop-end"
                    :class="{ 'drop-end-active': isStepDropEnd(mi) }"
                    @dragover.prevent.stop="stepDragOverEnd(mi, $event)"
                    @dragleave.stop="stepDropTarget = null"
                    @drop.prevent.stop="stepDropEnd(mi, $event)"
                  />

                  <button class="add-step" @click="addStep(mi)">
                    <AppIcon :d="I.plus" :size="14" :sw="2.4" /> {{ $t('recipes.addStep') }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Footer hint -->
          <div class="footer-hint">
            <AppIcon :d="I.shield" :size="14" />
            <span>{{ $t('recipes.publishHint', { hh: hh.current?.name || '…' }) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { useHouseholdStore } from '../stores/household'
import { useRecipeStore } from '../stores/recipes'
import AppButton from '../components/AppButton.vue'
import AppIcon from '../components/AppIcon.vue'
import Pill from '../components/Pill.vue'
import Field from '../components/Field.vue'
import ImageSlot from '../components/ImageSlot.vue'
import ToggleRow from '../components/ToggleRow.vue'
import { I } from '../components/icons.js'

const { t }   = useI18n()
const route   = useRoute()
const router  = useRouter()
const hh      = useHouseholdStore()
const recipes = useRecipeStore()

const isEdit = computed(() => !!route.params.id && route.path.includes('/edit'))

const importUrl        = ref('')
const urlFocused       = ref(false)
const importing        = ref(false)
const importError      = ref('')
const saving           = ref(false)
const addingTag        = ref(false)
const newTagInput      = ref('')
const tagInputRef      = ref(null)
const pendingImageFile = ref(null)

const DIFFICULTIES = ['Easy', 'Medium', 'Hard', 'Expert']

const form = ref({
  name:               '',
  description:        '',
  image_url:          '',
  prep_time:          '',
  cook_time:          '',
  servings:           0,
  difficulty:         '',
  calories:           '',
  calories_unit:      '100g',
  is_public:          true,
  tags:               [],
  ingredientSections: [{ name: '', items: [{ name: '', quantity: '' }] }],
  methods:            [{ name: '', steps: [''] }],
  source_url:         '',
})

const isRestricted = computed(() => hh.current?.role === 'restricted')

const totalIngredients = computed(() =>
  form.value.ingredientSections.reduce((sum, s) => sum + s.items.length, 0)
)

const canPublish = computed(() =>
  !isRestricted.value &&
  form.value.name.trim() &&
  form.value.ingredientSections.some(s => s.items.some(i => i.name.trim()))
)

// ─── Import ───────────────────────────────────────────────────────────────────

async function importFromUrl() {
  const url = importUrl.value.trim()
  if (!url) return
  importing.value = true
  importError.value = ''
  try {
    const data = await recipes.importFromUrl(url)
    if (data.error) { importError.value = data.error; return }
    form.value.name        = data.name || ''
    form.value.description = data.description || ''
    form.value.image_url   = data.image_url || ''
    form.value.prep_time   = data.prep_time || ''
    form.value.cook_time   = data.cook_time || ''
    const srvMatch = (data.servings || '').match(/\d+/)
    form.value.servings = srvMatch ? parseInt(srvMatch[0]) : 0
    form.value.tags        = data.tags || []
    form.value.source_url  = url
    if (data.ingredient_sections && data.ingredient_sections.length) {
      form.value.ingredientSections = data.ingredient_sections.map(s => ({
        name:  s.name || '',
        items: (s.items || []).length
          ? s.items.map(i => ({ name: i.name || '', quantity: i.quantity || '' }))
          : [{ name: '', quantity: '' }],
      }))
    } else {
      form.value.ingredientSections = [{ name: '', items: [{ name: '', quantity: '' }] }]
    }
    const importedSteps = (data.steps || []).filter(Boolean)
    form.value.methods = [{ name: '', steps: importedSteps.length ? importedSteps : [''] }]
  } catch(e) {
    importError.value = e.message || 'Failed to import. Check the URL and try again.'
  } finally { importing.value = false }
}

// ─── Ingredient sections ──────────────────────────────────────────────────────

function addSection() {
  form.value.ingredientSections.push({ name: '', items: [{ name: '', quantity: '' }] })
}
function removeSection(si) {
  form.value.ingredientSections.splice(si, 1)
  if (!form.value.ingredientSections.length) {
    form.value.ingredientSections.push({ name: '', items: [{ name: '', quantity: '' }] })
  }
}
function addIngredient(si) {
  form.value.ingredientSections[si].items.push({ name: '', quantity: '' })
}
function removeIngredient(si, ii) {
  form.value.ingredientSections[si].items.splice(ii, 1)
  if (!form.value.ingredientSections[si].items.length) {
    form.value.ingredientSections[si].items.push({ name: '', quantity: '' })
  }
}

// ─── Methods ──────────────────────────────────────────────────────────────────

function addMethod() {
  form.value.methods.push({ name: '', steps: [''] })
}
function removeMethod(mi) {
  form.value.methods.splice(mi, 1)
  if (!form.value.methods.length) form.value.methods.push({ name: '', steps: [''] })
}
function addStep(mi) {
  form.value.methods[mi].steps.push('')
}
function removeStep(mi, sti) {
  form.value.methods[mi].steps.splice(sti, 1)
  if (!form.value.methods[mi].steps.length) form.value.methods[mi].steps.push('')
}

// ─── Tags ─────────────────────────────────────────────────────────────────────

function addTag() {
  const tag = newTagInput.value.trim().toLowerCase()
  if (tag && !form.value.tags.includes(tag)) form.value.tags.push(tag)
  newTagInput.value = ''
  addingTag.value = false
}
function removeTag(tag) { form.value.tags = form.value.tags.filter(t => t !== tag) }

// ─── Image upload ─────────────────────────────────────────────────────────────

async function _uploadPendingImage(recipeId) {
  const token = localStorage.getItem('token')
  const headers = token ? { Authorization: `Bearer ${token}` } : {}
  const fd = new FormData()
  fd.append('type', 'recipe')
  fd.append('id', String(recipeId))
  if (pendingImageFile.value) {
    fd.append('file', pendingImageFile.value)
  } else if (form.value.image_url?.startsWith('http')) {
    fd.append('url', form.value.image_url)
  } else {
    return null
  }
  const res = await fetch('/api/upload', { method: 'POST', headers, body: fd })
  const data = await res.json()
  return data.url || null
}

// ─── Save ─────────────────────────────────────────────────────────────────────

async function save(publish) {
  if (saving.value) return
  if (publish && !canPublish.value) return
  saving.value = true
  try {
    const imageNeedsUpload = form.value.image_url.startsWith('blob:') || form.value.image_url.startsWith('http')
    const payload = {
      name:             form.value.name.trim(),
      description:      form.value.description.trim(),
      image_url:        imageNeedsUpload ? '' : form.value.image_url,
      prep_time:        form.value.prep_time,
      cook_time:        form.value.cook_time,
      servings:         form.value.servings ? String(form.value.servings) : '',
      difficulty:       form.value.difficulty,
      calories:         form.value.calories !== '' ? Number(form.value.calories) : null,
      calories_unit:    form.value.calories_unit || 'serving',
      source_url:       form.value.source_url,
      tags_json:        JSON.stringify(form.value.tags),
      ingredients_json: JSON.stringify(
        form.value.ingredientSections
          .map(s => ({ name: s.name.trim(), items: s.items.filter(i => i.name.trim()) }))
          .filter(s => s.items.length)
      ),
      methods_json: JSON.stringify(
        form.value.methods
          .map(m => ({ name: m.name.trim(), steps: m.steps.filter(Boolean) }))
          .filter(m => m.steps.length)
      ),
      is_public: form.value.is_public,
    }
    if (isEdit.value) {
      const imageUrl = await _uploadPendingImage(route.params.id)
      if (imageUrl) payload.image_url = imageUrl
      await recipes.update(route.params.id, payload)
      router.replace(`/recipes/${route.params.id}`)
    } else {
      const created = await recipes.create(hh.current.id, payload)
      const imageUrl = await _uploadPendingImage(created.id)
      if (imageUrl) await recipes.update(created.id, { image_url: imageUrl })
      router.replace(`/recipes/${created.id}`)
    }
  } catch(e) {} finally { saving.value = false }
}

function cancel() {
  if (isEdit.value) router.back()
  else router.replace('/recipes')
}

// ─── Load (edit mode) ─────────────────────────────────────────────────────────

function _loadIngredientSections(raw) {
  if (!raw || !raw.length) return [{ name: '', items: [{ name: '', quantity: '' }] }]
  if (raw[0] && 'items' in raw[0]) {
    return raw.map(s => ({
      name:  s.name || '',
      items: s.items && s.items.length ? s.items : [{ name: '', quantity: '' }],
    }))
  }
  return [{ name: '', items: raw }]
}

onMounted(async () => {
  if (isEdit.value) {
    try {
      const r = await recipes.get(route.params.id)
      if (r) {
        form.value.name          = r.name || ''
        form.value.description   = r.description || ''
        form.value.image_url     = r.image_url || ''
        form.value.prep_time     = r.prep_time || ''
        form.value.cook_time     = r.cook_time || ''
        const srvEdit = (r.servings || '').match(/\d+/)
        form.value.servings = srvEdit ? parseInt(srvEdit[0]) : 0
        form.value.difficulty    = r.difficulty || ''
        form.value.calories      = r.calories != null ? String(r.calories) : ''
        form.value.calories_unit = r.calories_unit || '100g'
        form.value.source_url    = r.source_url || ''
        form.value.tags          = JSON.parse(r.tags_json || '[]')
        form.value.is_public     = r.is_public ?? true
        form.value.ingredientSections = _loadIngredientSections(JSON.parse(r.ingredients_json || '[]'))
        const savedMethods = r.methods_json ? JSON.parse(r.methods_json) : null
        if (savedMethods && savedMethods.length) {
          form.value.methods = savedMethods.map(m => ({
            name:  m.name || '',
            steps: m.steps && m.steps.length ? m.steps : [''],
          }))
        } else {
          const legacySteps = JSON.parse(r.steps_json || '[""]')
          form.value.methods = [{ name: '', steps: legacySteps.length ? legacySteps : [''] }]
        }
      }
    } catch(e) {}
  }
})

// ─── Drag & Drop: Ingredients ─────────────────────────────────────────────────
// ingDragSrc  = { si, ii }         — item being dragged
// ingDropTarget = { si, ii }       — drop before this item
//              | { si, end:true }  — drop after last item in section

let ingDragSrc    = null
let ingDropTarget = ref(null)

function isIngDragging(si, ii) {
  return ingDragSrc && ingDragSrc.si === si && ingDragSrc.ii === ii
}
function isIngDropAbove(si, ii) {
  const t = ingDropTarget.value
  return t && !t.end && t.si === si && t.ii === ii
}
function isIngDropEnd(si) {
  const t = ingDropTarget.value
  return t && t.end && t.si === si
}

function ingDragStart(si, ii, e) {
  ingDragSrc = { si, ii }
  e.dataTransfer.effectAllowed = 'move'
  e.dataTransfer.setData('text/plain', '')
}
function ingDragEnd() {
  ingDragSrc = null
  ingDropTarget.value = null
}
function ingDragOverItem(si, ii, e) {
  if (!ingDragSrc) return
  e.dataTransfer.dropEffect = 'move'
  // Show drop indicator above top half, below bottom half
  const rect = e.currentTarget.getBoundingClientRect()
  const insertAt = e.clientY < rect.top + rect.height / 2 ? ii : ii + 1
  ingDropTarget.value = { si, ii: insertAt }
}
function ingDragLeaveItem() {
  // let the list-level handler decide; clear only if no subsequent dragover fires
  // (browsers fire leave before the next enter, so just clear and let the next over re-set)
  ingDropTarget.value = null
}
function ingDragOverEnd(si, e) {
  if (!ingDragSrc) return
  e.dataTransfer.dropEffect = 'move'
  ingDropTarget.value = { si, end: true }
}
function ingDragOverList(si, e) {
  // fallback: keep drop target live when hovering list padding
  if (!ingDragSrc) return
  e.dataTransfer.dropEffect = 'move'
}
function ingDropItem(si, ii, e) {
  if (!ingDragSrc) return
  const rect = e.currentTarget.getBoundingClientRect()
  const insertAt = e.clientY < rect.top + rect.height / 2 ? ii : ii + 1
  _moveIngredient(ingDragSrc.si, ingDragSrc.ii, si, insertAt)
  ingDragSrc = null
  ingDropTarget.value = null
}
function ingDropEnd(si, e) {
  if (!ingDragSrc) return
  _moveIngredient(ingDragSrc.si, ingDragSrc.ii, si, form.value.ingredientSections[si].items.length)
  ingDragSrc = null
  ingDropTarget.value = null
}
function ingDropList(si, e) {
  if (!ingDragSrc) return
  _moveIngredient(ingDragSrc.si, ingDragSrc.ii, si, form.value.ingredientSections[si].items.length)
  ingDragSrc = null
  ingDropTarget.value = null
}
function _moveIngredient(fromSi, fromIi, toSi, toIi) {
  if (fromSi === toSi && fromIi === toIi) return
  const sections = form.value.ingredientSections
  const item = sections[fromSi].items[fromIi]
  sections[fromSi].items.splice(fromIi, 1)
  let insertAt = toIi
  if (fromSi === toSi && fromIi < toIi) insertAt--
  insertAt = Math.max(0, Math.min(insertAt, sections[toSi].items.length))
  sections[toSi].items.splice(insertAt, 0, item)
  if (!sections[fromSi].items.length) {
    sections[fromSi].items.push({ name: '', quantity: '' })
  }
}

// ─── Drag & Drop: Steps ───────────────────────────────────────────────────────
// stepDragSrc   = { mi, sti }
// stepDropTarget = { mi, sti } | { mi, end:true }

let stepDragSrc    = null
let stepDropTarget = ref(null)

function isStepDragging(mi, sti) {
  return stepDragSrc && stepDragSrc.mi === mi && stepDragSrc.sti === sti
}
function isStepDropAbove(mi, sti) {
  const t = stepDropTarget.value
  return t && !t.end && t.mi === mi && t.sti === sti
}
function isStepDropEnd(mi) {
  const t = stepDropTarget.value
  return t && t.end && t.mi === mi
}

function stepDragStart(mi, sti, e) {
  stepDragSrc = { mi, sti }
  e.dataTransfer.effectAllowed = 'move'
  e.dataTransfer.setData('text/plain', '')
}
function stepDragEnd() {
  stepDragSrc = null
  stepDropTarget.value = null
}
function stepDragOverItem(mi, sti, e) {
  if (!stepDragSrc) return
  e.dataTransfer.dropEffect = 'move'
  const rect = e.currentTarget.getBoundingClientRect()
  const insertAt = e.clientY < rect.top + rect.height / 2 ? sti : sti + 1
  stepDropTarget.value = { mi, sti: insertAt }
}
function stepDragLeaveItem() {
  stepDropTarget.value = null
}
function stepDragOverEnd(mi, e) {
  if (!stepDragSrc) return
  e.dataTransfer.dropEffect = 'move'
  stepDropTarget.value = { mi, end: true }
}
function stepDragOverList(mi, e) {
  if (!stepDragSrc) return
  e.dataTransfer.dropEffect = 'move'
}
function stepDropItem(mi, sti, e) {
  if (!stepDragSrc) return
  const rect = e.currentTarget.getBoundingClientRect()
  const insertAt = e.clientY < rect.top + rect.height / 2 ? sti : sti + 1
  _moveStep(stepDragSrc.mi, stepDragSrc.sti, mi, insertAt)
  stepDragSrc = null
  stepDropTarget.value = null
}
function stepDropEnd(mi, e) {
  if (!stepDragSrc) return
  _moveStep(stepDragSrc.mi, stepDragSrc.sti, mi, form.value.methods[mi].steps.length)
  stepDragSrc = null
  stepDropTarget.value = null
}
function stepDropList(mi, e) {
  if (!stepDragSrc) return
  _moveStep(stepDragSrc.mi, stepDragSrc.sti, mi, form.value.methods[mi].steps.length)
  stepDragSrc = null
  stepDropTarget.value = null
}
function _moveStep(fromMi, fromSti, toMi, toSti) {
  if (fromMi === toMi && fromSti === toSti) return
  const methods = form.value.methods
  const step = methods[fromMi].steps[fromSti]
  methods[fromMi].steps.splice(fromSti, 1)
  let insertAt = toSti
  if (fromMi === toMi && fromSti < toSti) insertAt--
  insertAt = Math.max(0, Math.min(insertAt, methods[toMi].steps.length))
  methods[toMi].steps.splice(insertAt, 0, step)
  if (!methods[fromMi].steps.length) {
    methods[fromMi].steps.push('')
  }
}
</script>

<style scoped>
.recipe-create-view { display: flex; flex-direction: column; min-height: 100%; }

.topbar {
  padding: 14px 32px; border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 12px;
}
.topbar-meta { display: flex; flex-direction: column; gap: 1px; }
.topbar-draft { font-size: 14px; font-weight: 500; margin-top: 1px; }
.spacer { flex: 1; }
.mono { font-family: var(--font-mono); font-size: 10px; font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase; color: var(--text-mute); }

.content { padding: 24px 32px; max-width: 1080px; width: 100%; margin: 0 auto; display: flex; flex-direction: column; gap: 22px; box-sizing: border-box; }

/* Import panel */
.import-panel {
  background: var(--surface); border: 1.5px solid var(--accent); border-radius: 16px;
  padding: 18px; display: flex; flex-direction: column; gap: 12px;
  position: relative; overflow: hidden;
}
.import-glow {
  position: absolute; right: -40px; top: -40px; width: 160px; height: 160px;
  background: var(--accent); opacity: 0.06; border-radius: 50%; filter: blur(28px);
  pointer-events: none;
}
.import-header { display: flex; align-items: center; gap: 12px; }
.import-icon {
  width: 40px; height: 40px; border-radius: 11px;
  background: var(--accent-dim); color: var(--accent);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.import-copy { flex: 1; }
.import-title { font-size: 16px; font-weight: 600; letter-spacing: -0.2px; }
.import-sub { font-size: 12.5px; color: var(--text-dim); margin-top: 2px; }
.import-input-row { display: flex; gap: 10px; }
.url-field {
  flex: 1; background: var(--bg); border: 1.5px solid var(--accent); border-radius: 12px;
  padding: 11px 16px; display: flex; align-items: center; gap: 8px; transition: border-color 0.15s;
}
.url-field:not(.focused) { border-color: rgba(199,155,255,0.4); }
.url-icon { color: var(--accent); flex-shrink: 0; }
.url-input {
  flex: 1; background: transparent; color: var(--text);
  font-family: var(--font-mono); font-size: 13px; letter-spacing: 0.2px;
}
.url-input::placeholder { color: var(--text-mute); }
.import-error { font-size: 13px; color: var(--danger); padding: 8px 12px; background: var(--danger-bg); border-radius: 8px; }

.or-divider { display: flex; align-items: center; gap: 14px; }
.or-line { flex: 1; height: 1px; background: var(--border); }

/* Form grid */
.form-grid { display: grid; grid-template-columns: 380px 1fr; gap: 22px; }
.form-left { display: flex; flex-direction: column; gap: 14px; min-width: 0; overflow: hidden; }
.form-right { display: flex; flex-direction: column; gap: 22px; min-width: 0; }
.field-label { display: block; margin-bottom: 8px; }
.cover-slot { border-radius: 14px; overflow: hidden; border: 1px dashed var(--border-hi); }
.cover-hint { display: block; margin-top: 8px; color: var(--text-mute); font-size: 11.5px; }
.textarea-field { display: flex; flex-direction: column; }
.desc-textarea {
  background: var(--surface); border: 1.5px solid var(--border); border-radius: 12px;
  padding: 10px 14px; color: var(--text); font-size: 13.5px; line-height: 1.5;
  resize: vertical; transition: border-color 0.15s; font-family: var(--font-sans);
}
.desc-textarea:focus { border-color: var(--accent); outline: none; }
.desc-textarea::placeholder { color: var(--text-mute); }

.tags-row { display: flex; gap: 6px; flex-wrap: wrap; }
.tag-pill {
  padding: 5px 11px; border-radius: 999px; background: var(--accent-dim);
  color: var(--accent); font-size: 12px; font-weight: 500;
  display: inline-flex; align-items: center; gap: 6px;
}
.tag-remove { color: var(--accent); opacity: 0.7; cursor: pointer; }
.tag-add {
  padding: 5px 11px; border-radius: 999px;
  background: var(--surface); border: 1px dashed var(--border-hi);
  color: var(--text-dim); font-size: 12px;
  display: inline-flex; align-items: center; gap: 6px; cursor: pointer;
}
.tag-input {
  padding: 5px 11px; border-radius: 999px; border: 1px solid var(--accent);
  background: var(--bg); color: var(--text); font-size: 12px; outline: none; min-width: 80px;
}

.meta-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
.cal-row { display: flex; align-items: stretch; gap: 8px; }
.cal-row > :first-child { flex: 1; }
.unit-select-wrap {
  flex: 0 0 100px; display: flex; flex-direction: column; gap: 2px;
  background: var(--surface); border: 1.5px solid var(--border);
  border-radius: var(--r-field); padding: 10px 14px; transition: border-color 0.15s;
}
.unit-select-wrap:focus-within { border-color: var(--accent); }
.unit-select-label {
  font-family: var(--font-mono); font-size: 10px; font-weight: 500;
  letter-spacing: 0.5px; text-transform: uppercase; color: var(--text-mute);
}
.unit-select { background: transparent; border: none; outline: none; color: var(--text); font-size: 14px; width: 100%; cursor: pointer; padding: 0; }
.unit-select option { background: var(--surface); }
.diff-select {
  width: 100%; min-width: 0; padding: 10px 12px; border-radius: 10px;
  background: var(--surface); border: 1.5px solid var(--border);
  color: var(--text); font-size: 14px; box-sizing: border-box;
}

/* Servings stepper (create/edit form) */
.srv-stepper-field {
  background: var(--surface); border: 1.5px solid var(--border);
  border-radius: var(--r-field); padding: 10px 14px;
  display: flex; flex-direction: column; gap: 6px;
  transition: border-color 0.15s;
}
.srv-stepper-field:focus-within { border-color: var(--accent); }
.srv-stepper-row { display: flex; align-items: center; gap: 6px; }
.srv-btn {
  width: 22px; height: 22px; border-radius: 6px;
  background: var(--bg); border: 1px solid var(--border);
  color: var(--accent); font-size: 16px; font-weight: 600;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.15s; flex-shrink: 0; line-height: 1;
  user-select: none;
}
.srv-btn:hover:not(:disabled) { background: var(--accent-dim); border-color: var(--accent); }
.srv-btn:disabled { opacity: 0.3; cursor: not-allowed; }
.srv-num { flex: 1; font-size: 14px; font-weight: 500; color: var(--text); text-align: center; }

/* ── Ingredient sections ──────────────────────────────────────────────────── */
.right-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.right-header-actions { display: flex; align-items: center; gap: 10px; }
.right-title { margin: 0; font-size: 15px; font-weight: 600; letter-spacing: -0.2px; }

.add-section-btn {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 4px 10px; border-radius: 7px;
  background: var(--accent-dim); color: var(--accent);
  font-size: 12px; font-weight: 500; cursor: pointer; transition: opacity 0.15s;
}
.add-section-btn:hover { opacity: 0.8; }

.sections-editor { display: flex; flex-direction: column; gap: 10px; }
.section-block {
  background: var(--surface); border: 1px solid var(--border); border-radius: 14px; overflow: hidden;
}
.section-header {
  display: flex; align-items: center; gap: 8px;
  padding: 9px 12px; border-bottom: 1px solid var(--border); background: var(--surface-hi);
}
.section-name-input {
  flex: 1; background: transparent; color: var(--text);
  font-size: 12px; font-weight: 600; letter-spacing: 0.1px; font-family: var(--font-mono);
}
.section-name-input::placeholder { color: var(--text-mute); font-weight: 400; }
.section-del-btn {
  color: var(--text-mute); opacity: 0.6; cursor: pointer;
  display: flex; align-items: center; justify-content: center; transition: all 0.15s;
}
.section-del-btn:hover { color: var(--danger); opacity: 1; }

.ing-list { overflow: hidden; }
.ing-row {
  display: flex; align-items: center; gap: 10px; padding: 9px 12px;
  position: relative; cursor: default; transition: background 0.1s;
}
.ing-row.divide { border-top: 1px solid var(--border); }
.ing-row:hover { background: var(--surface-hi); }

/* Drag states — ingredients */
.ing-row.ing-dragging { opacity: 0.35; }
.ing-row.ing-drop-above { box-shadow: inset 0 2px 0 var(--accent); }

.drag-handle {
  color: var(--text-mute); cursor: grab; flex-shrink: 0; opacity: 0.5;
  transition: opacity 0.15s;
}
.drag-handle:hover { opacity: 1; }
.drag-handle:active { cursor: grabbing; }

.step-drag-handle { margin-top: 3px; }

.ing-name-input { flex: 1; background: transparent; color: var(--text); font-size: 13.5px; }
.ing-name-input::placeholder { color: var(--text-mute); }
.ing-qty-input {
  width: 80px; font-family: var(--font-mono); font-size: 12px; color: var(--text-dim);
  border-left: 1px solid var(--border); padding-left: 10px; background: transparent;
}
.ing-qty-input::placeholder { color: var(--text-mute); }
.row-del { color: var(--text-mute); opacity: 0.7; cursor: pointer; transition: all 0.15s; }
.row-del:hover { color: var(--danger); opacity: 1; }

/* Bottom drop zone (shared by both ingredients and steps) */
.list-drop-end {
  height: 4px; margin: 0 12px 0; border-radius: 2px; transition: all 0.15s;
}
.drop-end-active {
  height: 22px !important; margin: 4px 10px !important;
  background: var(--accent-dim); border: 1px dashed rgba(199,155,255,0.45);
  border-radius: 6px;
}

.add-row {
  display: flex; align-items: center; gap: 10px; padding: 9px 12px;
  border-top: 1px solid var(--border);
  color: var(--accent); font-size: 13px; font-weight: 500; cursor: pointer;
  width: 100%; text-align: left;
}

/* ── Methods editor ───────────────────────────────────────────────────────── */
.add-method-btn {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 4px 10px; border-radius: 7px;
  background: var(--accent-dim); color: var(--accent);
  font-size: 12px; font-weight: 500; cursor: pointer; transition: opacity 0.15s;
}
.add-method-btn:hover { opacity: 0.8; }
.methods-editor { display: flex; flex-direction: column; gap: 12px; }
.method-block {
  background: var(--surface); border: 1px solid var(--border); border-radius: 14px; overflow: hidden;
}
.method-header {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 14px; border-bottom: 1px solid var(--border); background: var(--surface-hi);
}
.method-name-input {
  flex: 1; background: transparent; color: var(--text);
  font-size: 13px; font-weight: 600; letter-spacing: -0.1px;
}
.method-name-input::placeholder { color: var(--text-mute); font-weight: 400; }
.method-del-btn {
  color: var(--text-mute); opacity: 0.6; cursor: pointer;
  display: flex; align-items: center; justify-content: center; transition: all 0.15s;
}
.method-del-btn:hover { color: var(--danger); opacity: 1; }

.method-steps { display: flex; flex-direction: column; }
.step-row {
  padding: 10px 14px; display: flex; gap: 10px; align-items: flex-start;
  border-bottom: 1px solid var(--border); position: relative; transition: background 0.1s;
}
.step-row:hover { background: var(--surface-hi); }
.step-row.step-empty { background: transparent; }

/* Drag states — steps */
.step-row.step-dragging { opacity: 0.35; }
.step-row.step-drop-above { box-shadow: inset 0 2px 0 var(--accent); }

.step-num {
  width: 24px; height: 24px; border-radius: 6px; flex-shrink: 0; margin-top: 2px;
  background: var(--bg); border: 1px solid var(--border); color: var(--accent);
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-mono); font-size: 11px; font-weight: 600;
}
.step-input {
  flex: 1; background: transparent; color: var(--text); font-size: 13.5px;
  line-height: 1.5; resize: none; font-family: var(--font-sans);
}
.step-input::placeholder { color: var(--text-mute); }
.add-step {
  padding: 9px 14px; display: flex; align-items: center; gap: 10px;
  color: var(--accent); font-size: 13px; font-weight: 500; cursor: pointer;
  width: 100%; text-align: left;
}

.footer-hint {
  padding: 12px 14px; border-radius: 10px;
  background: var(--surface); border: 1px solid var(--border);
  display: flex; gap: 10px; align-items: center; color: var(--text-dim);
  font-size: 12px; line-height: 1.5;
}

.restricted-notice {
  display: flex; align-items: center; gap: 8px; padding: 12px 16px; border-radius: 10px;
  background: var(--danger-bg); border: 1px solid rgba(255,122,122,0.25);
  color: var(--danger); font-size: 13px;
}
.form-disabled { opacity: 0.45; pointer-events: none; }

@media (max-width: 900px) { .form-grid { grid-template-columns: 1fr; } }
@media (max-width: 768px) { .topbar, .content { padding-left: 20px; padding-right: 20px; } }
</style>
