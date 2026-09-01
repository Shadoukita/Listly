<template>
  <div class="recipe-detail-view">
    <!-- Topbar -->
    <div class="topbar">
      <router-link to="/recipes" class="back-btn">
        <AppIcon :d="I.chevR" :size="14" :sw="2" class="back-icon" />
        {{ $t('recipes.backToRecipes') }}
      </router-link>
      <span class="spacer" />
      <template v-if="recipe">
        <Pill v-if="!recipe.is_public" tone="neutral">
          <AppIcon :d="I.lock" :size="10" /> {{ $t('recipes.householdOnly') }}
        </Pill>
        <button
          class="fav-topbar-btn"
          :class="{ 'is-fav': recipe.is_favorited }"
          @click="onFavorite"
          :title="recipe.is_favorited ? $t('recipes.unfavorite') : $t('recipes.favorite')"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path :d="I.heart" :fill="recipe.is_favorited ? 'currentColor' : 'none'" />
          </svg>
          {{ recipe.is_favorited ? $t('recipes.unfavorite') : $t('recipes.favorite') }}
        </button>
        <router-link v-if="canEdit" :to="`/recipes/${recipe.id}/edit`">
          <AppButton variant="outline" size="sm">
            <AppIcon :d="I.settings" :size="14" /> {{ $t('global.edit') }}
          </AppButton>
        </router-link>
        <AppButton v-if="canDelete" variant="outline" size="sm" class="delete-btn" @click="deleteRecipe">
          <AppIcon :d="I.trash" :size="14" /> {{ $t('recipes.delete') }}
        </AppButton>
      </template>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="mono">{{ $t('global.loading') }}</div>
    </div>

    <template v-else-if="recipe">
      <!-- Hero image -->
      <div class="hero-img" :style="heroStyle">
        <div class="hero-glow" :style="{ background: cardColor }" />
        <div v-if="!recipe.image_url" class="hero-placeholder">
          <div class="hero-plate">{{ recipe.name[0] }}</div>
        </div>
        <img v-else :src="recipe.image_url" class="hero-photo" alt="" />
        <div class="hero-badge">
          <AppIcon :d="I.chef" :size="10" :sw="2.2" /> {{ $t('recipes.badge') }}
        </div>
      </div>

      <!-- Content -->
      <div class="content">
        <!-- Title block -->
        <div>
          <div class="tags-row" v-if="tags.length">
            <Chip v-for="tag in tags" :key="tag">{{ tag }}</Chip>
          </div>
          <h1 class="recipe-title">{{ recipe.name }}</h1>
          <p v-if="recipe.description" class="recipe-desc">{{ recipe.description }}</p>
          <div class="author-row" v-if="recipe.created_by_name">
            <Avatar :name="recipe.created_by_name" :src="recipe.created_by_profile_image || ''" :color="avatarColor(recipe.created_by)" :size="24" />
            <span class="author-text">{{ $t('recipes.addedBy', { name: recipe.created_by_name }) }}</span>
          </div>
        </div>

        <!-- Stats strip -->
        <div class="stats-grid">
          <div class="stat-card">
            <div class="mono">{{ $t('recipes.prep') }}</div>
            <div class="stat-val">{{ recipe.prep_time || '–' }}</div>
          </div>
          <div class="stat-card">
            <div class="mono">{{ $t('recipes.cook') }}</div>
            <div class="stat-val">{{ recipe.cook_time || '–' }}</div>
          </div>
          <!-- Servings — interactive stepper when a number is parseable -->
          <div class="stat-card serving-stat-card">
            <div class="mono">{{ $t('recipes.servings') }}</div>
            <template v-if="baseServings">
              <div class="serving-stepper">
                <button class="svc-btn" @click="currentServings = Math.max(1, currentServings - 1)" :disabled="currentServings <= 1">−</button>
                <span class="svc-num">{{ currentServings }}</span>
                <button class="svc-btn" @click="currentServings++">+</button>
              </div>
              <div v-if="currentServings !== baseServings" class="svc-note mono">
                {{ $t('recipes.originalServings', { n: baseServings }) }}
              </div>
            </template>
            <template v-else>
              <div class="stat-val">{{ recipe.servings || '–' }}</div>
            </template>
          </div>
          <div class="stat-card">
            <div class="mono">{{ $t('recipes.difficulty') }}</div>
            <div class="stat-val">{{ recipe.difficulty || '–' }}</div>
          </div>
          <div class="stat-card">
            <div class="mono">{{ $t('recipes.calories') }}</div>
            <div class="stat-val">{{ recipe.calories != null ? recipe.calories + ' kcal' : '–' }}</div>
            <div v-if="recipe.calories != null" class="stat-unit mono">{{ $t('recipes.per') }} {{ recipe.calories_unit === '100g' ? $t('recipes.per100gLabel') : $t('recipes.perServingLabel') }}</div>
          </div>
        </div>

        <!-- Two-column body -->
        <div class="body-grid">
          <!-- Ingredients -->
          <div>
            <div class="col-header">
              <h3 class="col-title">{{ $t('recipes.ingredients') }}</h3>
              <div class="mono">{{ totalIngredients }}</div>
            </div>
            <!-- Scale banner — visible when servings differ from original -->
            <div v-if="baseServings && currentServings !== baseServings" class="scale-banner">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="9"/><path d="M12 8v4l2.5 2.5"/>
              </svg>
              {{ $t('recipes.scaledFor', { n: currentServings }) }}
            </div>

            <div class="ingredient-list">
              <template v-for="(section, si) in scaledIngredientSections" :key="si">
                <!-- Section header — shown when there are multiple sections or the section has a name -->
                <div
                  v-if="section.name || ingredientSections.length > 1"
                  class="ing-section-header"
                  :class="{ 'ing-section-divider': si > 0 }"
                >
                  {{ section.name || `${$t('recipes.ingredients')} ${si + 1}` }}
                </div>
                <div
                  v-for="(ing, ii) in section.items" :key="`${si}:${ii}`"
                  class="ingredient-row"
                  :class="{ divide: ii > 0 || (si > 0 && !section.name) }"
                >
                  <span
                    class="ing-check"
                    :class="{ checked: checkedIng.has(`${si}:${ii}`) }"
                    @click="toggleIng(`${si}:${ii}`)"
                  >
                    <AppIcon v-if="checkedIng.has(`${si}:${ii}`)" :d="I.check" :size="11" :sw="3" />
                  </span>
                  <span v-if="ing.quantity" class="ing-qty">{{ ing.quantity }}</span>
                  <span class="ing-name" :class="{ 'ing-done': checkedIng.has(`${si}:${ii}`) }">{{ ing.name }}</span>
                </div>
              </template>
            </div>

            <!-- Push to list CTA -->
            <div class="push-cta">
              <div class="push-icon">
                <AppIcon :d="I.cart" :size="16" />
              </div>
              <div class="push-text">
                <div class="push-title">{{ $t('recipes.addAllToList') }}</div>
                <div class="push-sub">{{ $t('recipes.pushSub', { n: totalIngredients, hh: hh.current?.name }) }}</div>
              </div>
            </div>
            <AppButton size="sm" :full="true" :disabled="pushing" @click="pushToList">
              <AppIcon :d="I.cart" :size="14" /> {{ pushing ? $t('recipes.adding') : $t('recipes.addToList', { n: totalIngredients }) }}
            </AppButton>
            <div v-if="pushed" class="push-confirm">
              <AppIcon :d="I.check" :size="13" /> {{ $t('recipes.addedConfirm') }}
            </div>
            <div v-if="canEdit" class="visibility-row">
              <ToggleRow
                :icon="I.globe"
                :label="$t('recipes.publicRecipe')"
                :hint="$t('recipes.publicRecipeHint')"
                :on="recipe.is_public"
                @change="toggleVisibility"
              />
            </div>
          </div>

          <!-- Methods / Steps -->
          <div>
            <div class="col-header">
              <h3 class="col-title">{{ $t('recipes.method') }}</h3>
              <div class="mono">{{ $t('recipes.stepsCount', { n: totalSteps }) }}</div>
            </div>
            <div class="methods-body">
              <div
                v-for="(method, mi) in methods"
                :key="mi"
                class="method-group"
                :class="{ 'method-group-divider': mi > 0 }"
              >
                <div v-if="method.name" class="method-label">{{ method.name }}</div>
                <div class="steps-list">
                  <div v-for="(step, si) in method.steps" :key="si" class="step-card">
                    <div class="step-num">{{ si + 1 }}</div>
                    <p class="step-text">{{ step }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <div v-else class="loading-state">
      <div class="mono">{{ $t('recipes.notFound') }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore, avatarColor } from '../stores/auth'
import { useHouseholdStore } from '../stores/household'
import { useRecipeStore } from '../stores/recipes'
import Avatar from '../components/Avatar.vue'
import Pill from '../components/Pill.vue'
import Chip from '../components/Chip.vue'
import AppButton from '../components/AppButton.vue'
import AppIcon from '../components/AppIcon.vue'
import ToggleRow from '../components/ToggleRow.vue'
import { I } from '../components/icons.js'

const { t }   = useI18n()
const route   = useRoute()
const router  = useRouter()
const auth    = useAuthStore()
const hh      = useHouseholdStore()
const recipes = useRecipeStore()

const loading         = ref(true)
const recipe          = ref(null)
const checkedIng      = ref(new Set())
const pushing         = ref(false)
const pushed          = ref(false)
const favPending      = ref(false)
const currentServings = ref(0)  // 0 = not yet initialized

const PALETTE = ['#c79bff','#ffb86b','#7cf2a0','#9bd9ff','#ff9ec7','#ffd166']
const cardColor = computed(() => {
  const id = recipe.value?.id || 1
  return PALETTE[(id - 1) % PALETTE.length]
})
const heroStyle = computed(() => ({
  background: `linear-gradient(135deg, ${cardColor.value}33 0%, ${cardColor.value}11 60%, var(--surface-hi) 100%)`,
}))

// Role in the recipe's own household (null if user is not a member there)
const recipeHHRole = computed(() => {
  if (!recipe.value) return null
  const found = hh.households.find(h => h.id === recipe.value.household_id)
  return found?.role || null
})

const canEdit   = computed(() =>
  auth.isAdmin ||
  (recipeHHRole.value && ['owner', 'admin', 'member'].includes(recipeHHRole.value))
)
const canDelete = computed(() =>
  auth.isAdmin ||
  (recipeHHRole.value && ['owner', 'admin'].includes(recipeHHRole.value))
)

const tags = computed(() => {
  try { return JSON.parse(recipe.value?.tags_json || '[]') } catch { return [] }
})

// Support both new sectioned format and legacy flat format
const ingredientSections = computed(() => {
  try {
    const parsed = JSON.parse(recipe.value?.ingredients_json || '[]')
    if (!parsed.length) return [{ name: '', items: [] }]
    // New format: first element has an "items" key
    if (parsed[0] && 'items' in parsed[0]) return parsed
    // Legacy flat format: wrap in a single unnamed section
    return [{ name: '', items: parsed }]
  } catch { return [{ name: '', items: [] }] }
})
const totalIngredients = computed(() =>
  ingredientSections.value.reduce((sum, s) => sum + (s.items?.length || 0), 0)
)

// ─── Serving calculator ───────────────────────────────────────────────────────

// Parse the first number found in the servings string  e.g. "4 Portionen" → 4
const baseServings = computed(() => {
  const s = recipe.value?.servings
  if (!s) return null
  const m = String(s).match(/\d+/)
  if (!m) return null
  const n = parseInt(m[0])
  return n > 0 ? n : null
})

const scaleFactor = computed(() => {
  if (!baseServings.value || !currentServings.value) return 1
  return currentServings.value / baseServings.value
})

// Initialize currentServings once baseServings is known
watch(baseServings, (n) => {
  if (n && !currentServings.value) currentServings.value = n
}, { immediate: true })

// Parse a leading number out of a quantity string and return { num, rest }
function _parseQtyNum(qty) {
  if (!qty) return null
  let s = qty.trim()
  // Unicode fractions
  s = s.replace('½','0.5').replace('¼','0.25').replace('¾','0.75')
       .replace('⅓','0.3333').replace('⅔','0.6667')
  // Match  number  optionally followed by  / number  (fraction like 1/2)
  const m = s.match(/^(\d+[\d,\.]*)(?:\s*\/\s*(\d+[\d,\.]*))?/)
  if (!m) return null
  const a = parseFloat(m[1].replace(',', '.'))
  const b = m[2] ? parseFloat(m[2].replace(',', '.')) : null
  const num = b ? a / b : a
  if (isNaN(num)) return null
  const rest = s.slice(m[0].length)   // everything after the number
  return { num, rest }
}

function _fmtNum(n) {
  if (n === Math.round(n)) return String(Math.round(n))
  const r = Math.round(n * 10) / 10
  if (r === Math.round(r)) return String(Math.round(r))
  return r.toFixed(1)
}

function scaleQty(qty, factor) {
  if (!qty || factor === 1) return qty
  const p = _parseQtyNum(qty)
  if (!p) return qty
  const scaled = p.num * factor
  return p.rest ? `${_fmtNum(scaled)}${p.rest}` : _fmtNum(scaled)
}

// Ingredient sections with quantities scaled to currentServings
const scaledIngredientSections = computed(() => {
  const f = scaleFactor.value
  if (f === 1) return ingredientSections.value
  return ingredientSections.value.map(section => ({
    ...section,
    items: (section.items || []).map(ing => ({
      ...ing,
      quantity: scaleQty(ing.quantity, f),
    })),
  }))
})

// methods: prefer methods_json, fall back to legacy steps_json as single unnamed method
const methods = computed(() => {
  if (recipe.value?.methods_json) {
    try {
      const m = JSON.parse(recipe.value.methods_json)
      if (m && m.length) return m
    } catch {}
  }
  try {
    const s = JSON.parse(recipe.value?.steps_json || '[]')
    if (s.length) return [{ name: '', steps: s }]
  } catch {}
  return []
})
const totalSteps = computed(() => methods.value.reduce((sum, m) => sum + (m.steps?.length || 0), 0))

function toggleIng(key) {
  const s = new Set(checkedIng.value)
  s.has(key) ? s.delete(key) : s.add(key)
  checkedIng.value = s
}

async function onFavorite() {
  if (!recipe.value || favPending.value) return
  favPending.value = true
  try {
    const isFav = await recipes.toggleFavorite(recipe.value.id)
    recipe.value = { ...recipe.value, is_favorited: isFav }
  } catch(e) {}
  finally { favPending.value = false }
}

async function toggleVisibility(val) {
  if (!recipe.value) return
  try {
    const updated = await recipes.update(recipe.value.id, { is_public: val })
    recipe.value = { ...recipe.value, is_public: updated.is_public }
  } catch(e) {}
}

async function deleteRecipe() {
  if (!recipe.value) return
  if (!confirm(t('recipes.deleteConfirm'))) return
  try {
    await recipes.remove(recipe.value.id)
    router.replace('/recipes')
  } catch(e) {}
}

async function pushToList() {
  if (!recipe.value) return
  pushing.value = true
  try {
    // When scaled, send the already-computed quantities so the backend uses them directly
    let items = null
    if (scaleFactor.value !== 1) {
      items = scaledIngredientSections.value.flatMap(s =>
        (s.items || []).filter(i => i.name?.trim()).map(i => ({ name: i.name, quantity: i.quantity || '' }))
      )
    }
    await recipes.pushToList(recipe.value.id, items)
    pushed.value = true
    setTimeout(() => pushed.value = false, 3000)
  } catch(e) {}
  finally { pushing.value = false }
}

onMounted(async () => {
  try {
    recipe.value = await recipes.get(route.params.id)
  } catch(e) {}
  finally { loading.value = false }
})
</script>

<style scoped>
.recipe-detail-view { display: flex; flex-direction: column; min-height: 100%; }

.topbar {
  padding: 14px 32px; border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 12px;
}
.back-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 7px 12px; border-radius: 8px;
  background: var(--surface); border: 1px solid var(--border);
  color: var(--text-dim); font-size: 12px; cursor: pointer;
  transition: color 0.15s;
}
.back-btn:hover { color: var(--text); }
.back-icon { transform: scaleX(-1); }
.spacer { flex: 1; }
.delete-btn { color: var(--danger) !important; border-color: var(--danger) !important; }
.delete-btn:hover { background: var(--danger-bg) !important; }
.fav-topbar-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 7px 12px; border-radius: 8px;
  background: var(--surface); border: 1px solid var(--border);
  color: var(--text-dim); font-size: 12px; cursor: pointer;
  transition: color 0.15s, border-color 0.15s, background 0.15s;
}
.fav-topbar-btn:hover { border-color: #ff6b8a; color: #ff6b8a; }
.fav-topbar-btn.is-fav {
  color: #ff6b8a;
  border-color: rgba(255,107,138,0.4);
  background: rgba(255,107,138,0.1);
}

.hero-img {
  position: relative; width: 100%; height: 280px;
  display: flex; align-items: center; justify-content: center;
  overflow: hidden;
}
.hero-glow { position: absolute; width: 70%; height: 70%; border-radius: 50%; opacity: 0.18; filter: blur(40px); }
.hero-placeholder {
  position: relative; width: 96px; height: 96px; border-radius: 50%;
  background: var(--bg2); border: 1px solid rgba(199,155,255,0.33);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 8px 24px rgba(0,0,0,0.4);
}
.hero-plate { font-size: 36px; font-weight: 700; color: v-bind(cardColor); letter-spacing: -1px; }
.hero-photo { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.hero-badge {
  position: absolute; top: 14px; left: 14px;
  display: inline-flex; align-items: center; gap: 5px;
  padding: 3px 8px; border-radius: 999px;
  background: rgba(0,0,0,0.4); color: #f0f1f3;
  font-family: var(--font-mono); font-size: 10px; letter-spacing: 0.4px;
  text-transform: uppercase; backdrop-filter: blur(8px);
}

.content { padding: 24px 32px; max-width: 1080px; width: 100%; margin: 0 auto; display: flex; flex-direction: column; gap: 22px; box-sizing: border-box; }
.mono { font-family: var(--font-mono); font-size: 10px; font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase; color: var(--text-mute); }

.tags-row { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 6px; }
.recipe-title { margin: 0; font-size: 34px; font-weight: 600; letter-spacing: -0.9px; line-height: 1.05; }
.recipe-desc { margin: 10px 0 0; font-size: 15px; color: var(--text-dim); line-height: 1.6; max-width: 640px; }
.author-row { display: flex; align-items: center; gap: 8px; margin-top: 14px; }
.author-text { font-size: 13px; color: var(--text-dim); }

.stats-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; }
.stat-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 12px 14px; }
.stat-val { font-size: 22px; font-weight: 600; letter-spacing: -0.4px; margin-top: 2px; }
.stat-unit { font-family: var(--font-mono); font-size: 9px; font-weight: 500; letter-spacing: 0.4px; text-transform: uppercase; color: var(--text-mute); margin-top: 1px; }

/* Serving stepper (detail view) */
.serving-stat-card { min-width: 0; }
.serving-stepper {
  display: flex; align-items: center; gap: 6px; margin-top: 4px;
}
.svc-btn {
  width: 28px; height: 28px; border-radius: 8px;
  background: var(--bg); border: 1.5px solid var(--border);
  color: var(--accent); font-size: 20px; font-weight: 500;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.15s; flex-shrink: 0;
  line-height: 1; user-select: none;
}
.svc-btn:hover:not(:disabled) { background: var(--accent-dim); border-color: var(--accent); }
.svc-btn:disabled { opacity: 0.3; cursor: not-allowed; }
.svc-num {
  font-size: 22px; font-weight: 600; letter-spacing: -0.4px;
  min-width: 28px; text-align: center; color: var(--text);
}
.svc-note {
  font-size: 9px; color: var(--text-mute); margin-top: 3px;
  font-family: var(--font-mono); letter-spacing: 0.4px; text-transform: uppercase;
}

/* Scale banner */
.scale-banner {
  display: flex; align-items: center; gap: 7px; margin-bottom: 10px;
  padding: 7px 12px; border-radius: 9px;
  background: rgba(199,155,255,0.1); border: 1px solid rgba(199,155,255,0.25);
  color: var(--accent); font-size: 12px; font-weight: 500;
}

.body-grid { display: grid; grid-template-columns: 380px 1fr; gap: 28px; margin-top: 6px; }

.col-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.col-title { margin: 0; font-size: 17px; font-weight: 600; letter-spacing: -0.2px; }

.ingredient-list { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; overflow: hidden; }
.ing-section-header {
  padding: 7px 14px 5px;
  font-family: var(--font-mono); font-size: 10px; font-weight: 600;
  letter-spacing: 0.6px; text-transform: uppercase; color: var(--accent);
  background: var(--surface-hi);
  display: flex; align-items: center; gap: 6px;
}
.ing-section-header::before {
  content: ''; display: inline-block; width: 3px; height: 12px;
  border-radius: 2px; background: var(--accent); flex-shrink: 0;
}
.ing-section-divider { border-top: 1px solid var(--border); }
.ingredient-row { display: flex; align-items: center; gap: 12px; padding: 11px 14px; }
.ingredient-row.divide { border-top: 1px solid var(--border); }
.ing-check {
  width: 18px; height: 18px; border-radius: 5px; flex-shrink: 0;
  border: 1.5px solid var(--border-hi); display: flex; align-items: center; justify-content: center;
  color: var(--text-dim); cursor: pointer; transition: all 0.15s;
}
.ing-check.checked { background: var(--surface-hi); }
.ing-name { flex: 1; font-size: 13.5px; color: var(--text); }
.ing-name.ing-done { text-decoration: line-through; text-decoration-color: var(--text-mute); color: var(--text-dim); }
.ing-qty { font-family: var(--font-mono); font-size: 12px; color: #ffffff; flex-shrink: 0; }

.push-cta {
  margin-top: 14px; padding: 14px; border-radius: 14px;
  background: var(--accent-dim); border: 1px solid rgba(199,155,255,0.2);
  display: flex; align-items: center; gap: 12px; cursor: pointer;
}
.push-icon {
  width: 32px; height: 32px; border-radius: 9px;
  background: var(--accent); color: var(--accent-ink);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.push-text { flex: 1; }
.push-title { font-size: 13px; font-weight: 600; color: var(--accent); }
.push-sub { font-size: 11.5px; color: var(--text-dim); margin-top: 2px; }
.push-confirm { display: flex; align-items: center; gap: 6px; font-size: 13px; color: var(--success); margin-top: 8px; }
.visibility-row { margin-top: 14px; }

.methods-body { display: flex; flex-direction: column; gap: 16px; }

.method-group { display: flex; flex-direction: column; gap: 10px; }
.method-group-divider { padding-top: 16px; border-top: 1px solid var(--border); }

.method-label {
  font-size: 13px; font-weight: 700; letter-spacing: 0.1px;
  color: var(--text); padding: 0 2px;
  display: flex; align-items: center; gap: 6px;
}
.method-label::before {
  content: '';
  display: inline-block; width: 3px; height: 14px;
  border-radius: 2px; background: var(--accent);
  flex-shrink: 0;
}

.steps-list { display: flex; flex-direction: column; gap: 8px; }
.step-card {
  background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
  padding: 12px 14px; display: flex; gap: 12px;
}
.step-num {
  width: 26px; height: 26px; border-radius: 7px; flex-shrink: 0;
  background: var(--surface-hi); color: var(--accent);
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-mono); font-size: 12px; font-weight: 600;
}
.step-text { margin: 0; font-size: 13px; color: #ffffff; line-height: 1.55; }

.loading-state { display: flex; align-items: center; justify-content: center; padding: 100px 20px; }

@media (max-width: 900px) { .body-grid { grid-template-columns: 1fr; } .stats-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 768px) {
  .topbar, .content { padding-left: 20px; padding-right: 20px; }
  .hero-img { height: 200px; }
  /* Back / Favorite / Edit / Delete do not fit on one phone row — "Delete
     recipe" was clipped past the right edge. Wrap instead of overflowing. */
  .topbar { flex-wrap: wrap; row-gap: 10px; }
  .topbar .spacer { display: none; }
  .back-btn { flex-basis: 100%; justify-content: center; }
  .topbar .btn { flex: 1 1 auto; justify-content: center; min-width: 0; }
}
</style>
