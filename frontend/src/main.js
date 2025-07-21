import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/global.css'
import { useAuthStore } from '@/stores/auth'

const app = createApp(App)
const pinia = createPinia()

// Подключение Pinia
app.use(pinia)

// Подключение Router
app.use(router)

// 🔥 ИНИЦИАЛИЗАЦИЯ AUTH STORE ПРИ ЗАГРУЗКЕ ПРИЛОЖЕНИЯ
const initApp = async () => {
  try {
    const authStore = useAuthStore()
    await authStore.initialize()
    console.log('[Main] Auth store initialized successfully')
  } catch (error) {
    console.error('[Main] Failed to initialize auth store:', error)
  }
}

// Обработка глобальных ошибок
app.config.errorHandler = (err, vm, info) => {
  console.error('Global error:', err)
  console.error('Component:', vm)
  console.error('Info:', info)
}

// Инициализируем приложение
initApp().then(() => {
  app.mount('#app')
})