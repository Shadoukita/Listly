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
          <div class="stat-card">
            <div class="mono">{{ $t('recipes.servings') }}</div>
            <div class="stat-val">{{ recipe.servings || '–' }}</div>
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
              <div class="mono">{{ ingredients.length }}</div>
            </div>
            <div class="ingredient-list">
              <div
                v-for="(ing, i) in ingredients" :key="i"
                class="ingredient-row"
                :class="{ divide: i > 0 }"
              >
                <span class="ing-check" :class="{ checked: checkedIng.has(i) }" @click="toggleIng(i)">
                  <AppIcon v-if="checkedIng.has(i)" :d="I.check" :size="11" :sw="3" />
                </span>
                <span class="ing-name" :class="{ 'ing-done': checkedIng.has(i) }">{{ ing.name }}</span>
                <span class="ing-qty">{{ ing.quantity }}</span>
              </div>
            </div>

            <!-- Push to list CTA -->
            <div class="push-cta">
              <div class="push-icon">
                <AppIcon :d="I.cart" :size="16" />
              </div>
              <div class="push-text">
                <div class="push-title">{{ $t('recipes.addAllToList') }}</div>
                <div class="push-sub">{{ $t('recipes.pushSub', { n: ingredients.length, hh: hh.current?.name }) }}</div>
              </div>
            </div>
            <AppButton size="sm" :full="true" :disabled="pushing" @click="pushToList">
              <AppIcon :d="I.cart" :size="14" /> {{ pushing ? $t('recipes.adding') : $t('recipes.addToList', { n: ingredients.length }) }}
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
import { ref, computed, onMounted } from 'vue'
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

const loading    = ref(true)
const recipe     = ref(null)
const checkedIng = ref(new Set())
const pushing    = ref(false)
const pushed     = ref(false)

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
const ingredients = computed(() => {
  try { return JSON.parse(recipe.value?.ingredients_json || '[]') } catch { return [] }
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

function toggleIng(i) {
  const s = new Set(checkedIng.value)
  s.has(i) ? s.delete(i) : s.add(i)
  checkedIng.value = s
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
    await recipes.pushToList(recipe.value.id)
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
  display: flex; align-items: center; gap: 12;
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

.body-grid { display: grid; grid-template-columns: 380px 1fr; gap: 28px; margin-top: 6px; }

.col-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.col-title { margin: 0; font-size: 17px; font-weight: 600; letter-spacing: -0.2px; }

.ingredient-list { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; overflow: hidden; }
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
.ing-qty { font-family: var(--font-mono); font-size: 12px; color: var(--text-mute); }

.push-cta {
  margin-top: 14px; padding: 14px; border-radius: 14px;
  background: var(--accent-dim); border: 1px solid rgba(199,155,255,0.2);
  display: flex; align-items: center; gap: 12; cursor: pointer;
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
.step-text { margin: 0; font-size: 13px; color: var(--text-dim); line-height: 1.55; }

.loading-state { display: flex; align-items: center; justify-content: center; padding: 100px 20px; }

@media (max-width: 900px) { .body-grid { grid-template-columns: 1fr; } .stats-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 768px) { .topbar, .content { padding-left: 20px; padding-right: 20px; } .hero-img { height: 200px; } }
</style>
