import { createRouter, createWebHistory } from 'vue-router'
import { setupRouterGuards } from './guards.js'

// Public Views
import Home from '../views/public/Home.vue'
import Login from '../views/public/Login.vue'
import Register from '../views/public/Register.vue'

// Admin Views
import AdminLogin from '../views/admin/AdminLogin.vue'
import AdminDashboard from '../views/admin/AdminDashboard.vue'
import WorkerManagement from '../views/admin/WorkerManagement.vue'
import MarketRatesManagement from '../views/admin/MarketRatesManagement.vue'
import UserManagement from '../views/admin/UserManagement.vue' // убедись, что файл существует

// Worker Views
import WorkerLogin from '../views/worker/WorkerLogin.vue'
import WorkerDashboard from '../views/worker/WorkerDashboard.vue'
import WorkerProfile from '../views/worker/WorkerProfile.vue'

// Layouts
import PublicLayout from '../layouts/PublicLayout.vue'
import AdminLayout from '../layouts/AdminLayout.vue'
import WorkerLayout from '../layouts/WorkerLayout.vue'

const routes = [
  // Корневой путь (временный, редиректы обрабатываются в guards)
  {
    path: '/',
    name: 'Root',
    component: () => import('../views/public/Home.vue')
  },

  // Публичная часть
  {
    path: '/home',
    component: PublicLayout,
    children: [
      {
        path: '',
        name: 'Home',
        component: Home
      }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresGuest: true }
  },

  // Админская часть
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: AdminLogin
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, requiresRole: 'admin' },
    children: [
      {
        path: '',
        redirect: '/admin/dashboard'
      },
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: AdminDashboard
      },
      {
        path: 'workers',
        name: 'WorkerManagement',
        component: WorkerManagement
      },
      {
        path: 'market-exchange-rates',
        name: 'MarketRatesManagement',
        component: MarketRatesManagement
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: UserManagement
      }
    ]
  },

  // Работники
  {
    path: '/worker/login',
    name: 'WorkerLogin',
    component: WorkerLogin
  },
  {
    path: '/worker',
    component: WorkerLayout,
    meta: { requiresAuth: true, requiresRole: 'city_worker' },
    children: [
      {
        path: '',
        redirect: '/worker/dashboard'
      },
      {
        path: 'dashboard',
        name: 'WorkerDashboard',
        component: WorkerDashboard
      },
      {
        path: 'profile',
        name: 'WorkerProfile',
        component: WorkerProfile
      }
    ]
  },

  // 404
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Подключаем guards
setupRouterGuards(router)

export default router
