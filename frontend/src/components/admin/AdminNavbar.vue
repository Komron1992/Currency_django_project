<template>
  <nav class="admin-navbar">
    <div class="navbar-brand">
        <!-- ❌ БЫЛО: to="/dashboard" -->
        <!-- ✅ ДОЛЖНО БЫТЬ: -->
        <router-link to="/admin/dashboard" class="brand-link">
        <h2>💼 Админ панель</h2>
        </router-link>
    </div>

    <div class="navbar-menu">
  <!-- ❌ БЫЛО: to="/dashboard" -->
  <!-- ✅ ДОЛЖНО БЫТЬ: -->
  <router-link
    to="/admin/dashboard"
    class="nav-button home-button"
    :class="{ active: $route.path === '/admin/dashboard' }"
  >
    🏠 Главная
  </router-link>

  <!-- ❌ БЫЛО: to="/market-exchange-rates" -->
  <!-- ✅ ДОЛЖНО БЫТЬ: -->
  <router-link
    to="/admin/market-exchange-rates"
    class="nav-button"
    :class="{ active: $route.path === '/admin/market-exchange-rates' }"
  >
    💱 Курсы валют
  </router-link>

  <!-- ❌ БЫЛО: to="/workers" -->
  <!-- ✅ ДОЛЖНО БЫТЬ: -->
  <router-link
    to="/admin/workers"
    class="nav-button"
    :class="{ active: $route.path === '/admin/workers' }"
  >
    👥 Работники
  </router-link>

      <button
        @click="goToPublicSite"
        class="nav-button public-button"
        type="button"
      >
        🌐 Публичный сайт
      </button>

      <div class="user-info">
        <span class="user-role">{{ getCurrentUserRole() }}</span>
      </div>

      <button
        @click="logout"
        class="nav-button logout-button"
        type="button"
        :disabled="authStore.loading"
      >
        {{ authStore.loading ? '🔄 Выход...' : '🚪 Выйти' }}
      </button>
    </div>
  </nav>
</template>

<script>
import '@/assets/styles/components/admin/AdminNavbar.css'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'AdminNavbar',

  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },

  methods: {
    getCurrentUserRole() {
      const user = this.authStore.user

      if (!user) return 'Неизвестно'

      if (user.is_superuser) return 'Супер админ'
      if (user.role === 'admin') return 'Админ'
      if (user.role === 'worker') return 'Работник'
      return user.role || 'Пользователь'
    },

    goToPublicSite() {
      // Открываем публичный сайт в новой вкладке
      const publicUrl = process.env.VUE_APP_PUBLIC_URL || 'http://localhost:5174'
      window.open(publicUrl, '_blank')
    },

    async logout() {
      if (!confirm('Вы уверены, что хотите выйти?')) {
        return
      }

      try {
        // Используем метод logout из store
        this.authStore.logout()

        // Эмитим событие для родительского компонента
        this.$emit('logout')

        // Перенаправляем на страницу входа
        this.$router.push('/login')

      } catch (error) {
        console.error('Ошибка при выходе:', error)
        // В любом случае перенаправляем на страницу входа
        this.$router.push('/login')
      }
    }
  }
}
</script>
