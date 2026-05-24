import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { setupAllowed } from './stores/connection'

const SetupView          = () => import('./views/SetupView.vue')
const LoginView          = () => import('./views/LoginView.vue')
const InviteView         = () => import('./views/InviteView.vue')
const AppLayout          = () => import('./views/AppLayout.vue')
const ShoppingView       = () => import('./views/ShoppingView.vue')
const RecipesView        = () => import('./views/RecipesView.vue')
const RecipeDetailView   = () => import('./views/RecipeDetailView.vue')
const RecipeCreateView   = () => import('./views/RecipeCreateView.vue')
const ProfileView        = () => import('./views/ProfileView.vue')
const SettingsView       = () => import('./views/SettingsView.vue')
const AdminView          = () => import('./views/AdminView.vue')
const HouseholdSettingsView = () => import('./views/HouseholdSettingsView.vue')

const routes = [
  { path: '/setup',  component: SetupView },
  { path: '/login',  component: LoginView },
  { path: '/invite', component: InviteView },
  {
    path: '/',
    component: AppLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '',                        redirect: '/shopping' },
      { path: 'shopping',                component: ShoppingView },
      { path: 'recipes',                 component: RecipesView },
      { path: 'recipes/new',             component: RecipeCreateView },
      { path: 'recipes/:id/edit',        component: RecipeCreateView },
      { path: 'recipes/:id',             component: RecipeDetailView },
      { path: 'profile',                 component: ProfileView },
      { path: 'settings',                component: SettingsView },
      { path: 'admin',                   component: AdminView, meta: { requiresAdmin: true } },
      { path: 'households/:id/settings', component: HouseholdSettingsView },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.path === '/setup' && !setupAllowed.value) return '/'
  if (to.meta.requiresAuth && !auth.isLoggedIn) return '/login'
  if (to.meta.requiresAdmin && !auth.isAdmin) return '/'
})
