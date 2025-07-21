// frontend/src/router/guards.js
import { useAuthStore } from '@/stores/auth'

// Функция для определения правильной страницы логина
const getLoginPath = (targetPath) => {
  if (targetPath.startsWith('/admin')) {
    return '/admin/login'
  } else if (targetPath.startsWith('/worker')) {
    return '/worker/login'
  }
  return '/login'
}

// Функция для определения правильного дашборда на основе роли пользователя
const getDashboardPath = (user) => {
  if (!user) return '/home'

  console.log('[Guards] Getting dashboard for user:', user)

  // Проверяем админа
  if (user.role === 'admin' || user.is_superuser === true || user.is_superuser === 1) {
    console.log('[Guards] Redirecting to admin dashboard')
    return '/admin/dashboard'
  }

  // Проверяем работника
  if (user.role === 'city_worker') {
    console.log('[Guards] Redirecting to worker dashboard')
    return '/worker/dashboard'
  }

  console.log('[Guards] Default redirect to home')
  return '/home'
}

// Проверка доступа к админке
const canAccessAdmin = (user) => {
  if (!user) return false
  console.log('[Guards] Checking admin access for user:', user)
  const hasAccess = user.role === 'admin' || user.is_superuser === true || user.is_superuser === 1
  console.log('[Guards] Admin access result:', hasAccess)
  return hasAccess
}

// Проверка доступа к рабочей панели
const canAccessWorker = (user) => {
  if (!user) return false
  console.log('[Guards] Checking worker access for user:', user)
  const hasAccess = user.role === 'city_worker'
  console.log('[Guards] Worker access result:', hasAccess)
  return hasAccess
}

export const setupRouterGuards = (router) => {
  router.beforeEach(async (to, from, next) => {
    console.log(`[Router] Navigating from ${from.path} to: ${to.path}`)

    const authStore = useAuthStore()

    // 🔥 ДОЖИДАЕМСЯ ИНИЦИАЛИЗАЦИИ STORE
    if (!authStore.isInitialized) {
      console.log('[Router] Waiting for auth store initialization...')
      await authStore.initialize()
    }

    console.log('[Router] Auth state:', {
      isAuthenticated: authStore.isAuthenticated,
      user: authStore.user,
      hasToken: authStore.hasToken
    })

    // 🔥 ОБРАБОТКА СТРАНИЦ ЛОГИНА - ПРЕДОТВРАЩАЕМ БЕСКОНЕЧНЫЕ РЕДИРЕКТЫ
    const loginPaths = ['/login', '/admin/login', '/worker/login']
    if (loginPaths.includes(to.path)) {
      console.log('[Router] Login page detected:', to.path)

      // Если пользователь уже авторизован, перенаправляем на дашборд
      if (authStore.isAuthenticated) {
        const dashboardPath = getDashboardPath(authStore.user)
        console.log('[Router] User already authenticated, redirecting to:', dashboardPath)
        return next(dashboardPath)
      }

      // Если не авторизован, разрешаем доступ к странице логина
      console.log('[Router] Allowing access to login page')
      return next()
    }

    // 🔥 ОБРАБОТКА КОРНЕВОГО МАРШРУТА
    if (to.path === '/' || to.name === 'Root') {
      console.log('[Router] Root path detected')

      if (!authStore.isAuthenticated) {
        console.log('[Router] Not authenticated, redirecting to login')
        return next('/login')
      }

      const dashboardPath = getDashboardPath(authStore.user)
      console.log('[Router] Authenticated, redirecting to:', dashboardPath)
      return next(dashboardPath)
    }

    // 🔥 ПРИОРИТЕТНАЯ ОБРАБОТКА ВСЕХ АДМИНСКИХ МАРШРУТОВ
    if (to.path.startsWith('/admin') && to.path !== '/admin/login') {
      console.log('[Router] Admin area access detected:', to.path)

      // Сначала проверяем аутентификацию
      if (!authStore.isAuthenticated) {
        console.log('[Router] Not authenticated, redirecting to admin login')
        return next('/admin/login')
      }

      // Затем проверяем права доступа
      if (!canAccessAdmin(authStore.user)) {
        console.log('[Router] User cannot access admin area, user:', authStore.user)
        console.log('[Router] Current user is authenticated but not admin - logging out and redirecting to admin login')

        // 🔥 РАЗЛОГИНИВАЕМ ПОЛЬЗОВАТЕЛЯ И ПЕРЕНАПРАВЛЯЕМ НА АДМИНСКИЙ ЛОГИН
        authStore.logout()
        return next('/admin/login')
      }

      // Обработка прямого доступа к /admin
      if (to.path === '/admin') {
        console.log('[Router] Direct /admin access, redirecting to dashboard')
        return next('/admin/dashboard')
      }

      console.log('[Router] Admin access granted to:', to.path)
      return next()
    }

    // 🔥 ПРИОРИТЕТНАЯ ОБРАБОТКА ВСЕХ РАБОЧИХ МАРШРУТОВ
    if (to.path.startsWith('/worker') && to.path !== '/worker/login') {
      console.log('[Router] Worker area access detected:', to.path)

      // Сначала проверяем аутентификацию
      if (!authStore.isAuthenticated) {
        console.log('[Router] Not authenticated, redirecting to worker login')
        return next('/worker/login')
      }

      // Затем проверяем права доступа
      if (!canAccessWorker(authStore.user)) {
        console.log('[Router] User cannot access worker area, user:', authStore.user)
        console.log('[Router] Current user is authenticated but not worker - logging out and redirecting to worker login')

        // 🔥 РАЗЛОГИНИВАЕМ ПОЛЬЗОВАТЕЛЯ И ПЕРЕНАПРАВЛЯЕМ НА РАБОЧИЙ ЛОГИН
        authStore.logout()
        return next('/worker/login')
      }

      // Обработка прямого доступа к /worker
      if (to.path === '/worker') {
        console.log('[Router] Direct /worker access, redirecting to dashboard')
        return next('/worker/dashboard')
      }

      console.log('[Router] Worker access granted to:', to.path)
      return next()
    }

    // Проверяем требования к аутентификации для остальных маршрутов
    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
      console.log('[Router] Route requires auth, redirecting to appropriate login')
      const loginPath = getLoginPath(to.path)
      return next(loginPath)
    }

    // Проверяем роль пользователя для остальных маршрутов
    if (to.meta.requiresRole) {
      const requiredRole = to.meta.requiresRole

      if (!authStore.hasRole(requiredRole)) {
        console.log(`[Router] Role check failed. Required: ${requiredRole}, User role:`, authStore.user?.role)

        if (!authStore.isAuthenticated) {
          const loginPath = getLoginPath(to.path)
          return next(loginPath)
        }

        // Если пользователь авторизован, но роль не подходит, редиректим на home
        console.log(`[Router] Role mismatch, redirecting to home`)
        return next('/home')
      }
    }

    console.log('[Router] Navigation approved')
    next()
  })

  // Обработка ошибок навигации
  router.onError((error) => {
    console.error('[Router] Navigation error:', error)

    // Предотвращаем бесконечные редиректы при ошибках
    if (error.message.includes('Infinite redirect')) {
      console.error('[Router] Infinite redirect detected, stopping navigation')
      return
    }

    if (error.message.includes('auth') || error.message.includes('401')) {
      const authStore = useAuthStore()
      authStore.logout()
      router.push('/login')
    }
  })
}