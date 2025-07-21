<template>
  <div class="public-layout">
    <AppHeader />
    <main class="public-main-content">
      <router-view />
    </main>
    <footer class="footer">
      <div class="container">
        <p>&copy; 2025 Currency Exchange. Все права защищены.</p>
      </div>
    </footer>
  </div>
</template>

<script>
import '@/assets/styles/layouts/PublicLayout.css'
import AppHeader from '@components/public/AppHeader.vue'

export default {
  name: 'PublicLayout',
  components: {
    AppHeader
  }
}
</script>
