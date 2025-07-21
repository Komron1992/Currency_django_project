<template>
  <div class="admin-layout">
    <AdminNavbar @logout="handleLogout" />
    <div class="admin-content">
      <div class="container">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script>
import '@/assets/styles/layouts/AdminLayout.css'
import AdminNavbar from '@/components/admin/AdminNavbar.vue'
import { authAPI } from '@/services/api.js'

export default {
  name: 'AdminLayout',
  components: {
    AdminNavbar
  },

  methods: {
    async handleLogout() {
      try {
        await authAPI.logout()
        this.$router.push('/admin/login')
      } catch (error) {
        console.error('Ошибка при выходе:', error)
        // В любом случае перенаправляем на страницу входа
        this.$router.push('/admin/login')
      }
    }
  }
}
</script>
