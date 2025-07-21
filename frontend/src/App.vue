<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// Инициализируем auth store при загрузке приложения
onMounted(async () => {
  console.log('[App] Initializing auth store...')
  await authStore.initialize()
  console.log('[App] Auth store initialized, user:', authStore.user)
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Arial', sans-serif;
  background-color: #f5f5f5;
}

#app {
  min-height: 100vh;
}
</style>