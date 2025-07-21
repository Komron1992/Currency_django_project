<template>
  <header class="app-header">
    <div class="header-content">
      <div class="logo">
        <h2>Курсы валют Таджикистана</h2>
      </div>

      <div class="user-section" v-if="authStore.isAuthenticated">
        <span class="welcome-text">
          Добро пожаловать, {{ getUserDisplayName() }}!
          <span v-if="authStore.user?.role" class="user-role">
            ({{ getRoleDisplayName() }})
          </span>
        </span>
        <button @click="handleLogout" class="logout-btn">
          Выйти
        </button>
      </div>

      <div v-else class="auth-section">
        <router-link to="/login" class="login-link">
          Вход
        </router-link>
      </div>
    </div>
  </header>
</template>

<script setup>
import '@/assets/styles/components/public/AppHeader.css'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// Функция для получения отображаемого имени пользователя
const getUserDisplayName = () => {
  const user = authStore.user
  if (!user) return 'Пользователь'

  // Приоритет: first_name + last_name, затем username, затем email
  if (user.first_name && user.last_name) {
    return `${user.first_name} ${user.last_name}`
  } else if (user.first_name) {
    return user.first_name
  } else if (user.username) {
    return user.username
  } else if (user.email) {
    return user.email
  }

  return 'Пользователь'
}

// Функция для получения отображаемого названия роли
const getRoleDisplayName = () => {
  const role = authStore.user?.role
  const roleNames = {
    'admin': 'Администратор',
    'city_worker': 'Работник',
    'worker': 'Работник',
    'user': 'Пользователь'
  }
  return roleNames[role] || role || 'Пользователь'
}

const handleLogout = async () => {
  console.log('[DEBUG] Logout button clicked')

  try {
    // Вызываем logout из authStore
    await authStore.logout()

    // Принудительно перенаправляем на login
    router.replace('/login')

    console.log('[DEBUG] Redirected to login')
  } catch (error) {
    console.error('[DEBUG] Logout error:', error)
    // Все равно перенаправляем на login
    router.replace('/login')
  }
}

// Добавим отладочную информацию
console.log('[AppHeader] Auth store state:', {
  isAuthenticated: authStore.isAuthenticated,
  user: authStore.user,
  token: !!authStore.token
})
</script>
