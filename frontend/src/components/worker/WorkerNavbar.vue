<template>
  <nav class="bg-white shadow-sm border-b border-gray-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <!-- Левая часть - Лого и навигация -->
        <div class="flex items-center space-x-8">
          <!-- Лого -->
          <div class="logo-section">
            <span class="text-2xl mr-2">🏢</span>
            <span class="text-lg font-semibold text-gray-800">Рабочая панель</span>
          </div>

          <!-- Навигационное меню -->
          <div class="md:flex space-x-6">
            <router-link
              to="/worker/dashboard"
              class="nav-link"
              :class="$route.path === '/worker/dashboard' ? 'active' : ''"
            >
              📊 Главная
            </router-link>

            <router-link
              to="/worker/profile"
              class="nav-link"
              :class="$route.path === '/worker/profile' ? 'active' : ''"
            >
              👤 Профиль
            </router-link>
          </div>
        </div>

        <!-- Правая часть - Информация о пользователе -->
        <div class="flex items-center space-x-4">
          <!-- Информация о городе -->
          <div class="info-section sm:flex">
            <span>📍</span>
            <span>{{ authStore.userCity || authStore.user?.city_name || 'Не указан' }}</span>
          </div>

          <!-- Время -->
          <div class="info-section sm:flex">
            <span>🕒</span>
            <span>{{ currentTime }}</span>
          </div>

          <!-- Информация о пользователе -->
          <div class="flex items-center space-x-4">
            <span class="text-sm font-medium text-gray-700">
              {{ authStore.user?.username }}
            </span>
            <div class="user-avatar">
              <span>
                {{ authStore.user?.username?.charAt(0).toUpperCase() }}
              </span>
            </div>
          </div>

          <!-- Кнопка выйти -->
          <button
            @click="handleLogout"
            class="flex items-center space-x-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-md transition-colors"
          >
            <span>🚪</span>
            <span>Выйти</span>
          </button>

          <!-- Мобильное меню -->
          <button
            @click="showMobileMenu = !showMobileMenu"
            class="md:hidden p-2 rounded-md hover:bg-gray-50"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path v-if="!showMobileMenu" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
      </div>

      <!-- Мобильное меню -->
      <div v-if="showMobileMenu" class="mobile-menu md:hidden">
        <div class="space-y-1">
          <router-link
            to="/worker/dashboard"
            @click="showMobileMenu = false"
            class="mobile-nav-link"
            :class="$route.path === '/worker/dashboard' ? 'active' : ''"
          >
            📊 Главная
          </router-link>

          <router-link
            to="/rates"
            @click="showMobileMenu = false"
            class="mobile-nav-link"
            :class="$route.path === '/rates' ? 'active' : ''"
          >
            💱 Курсы валют
          </router-link>

          <router-link
            to="/worker/profile"
            @click="showMobileMenu = false"
            class="mobile-nav-link"
            :class="$route.path === '/worker/profile' ? 'active' : ''"
          >
            👤 Профиль
          </router-link>

          <div class="border-t border-gray-200 pt-2 mt-2">
            <div class="px-3 py-2 text-sm text-gray-600">
              📍 {{ authStore.userCity || authStore.user?.city_name || 'Не указан' }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import '@/assets/styles/components/worker/WorkerNavbar.css'
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const showMobileMenu = ref(false)
const currentTime = ref('')

let timeInterval = null

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)

  // Отладка для проверки данных пользователя
  console.log('User data:', authStore.user)
  console.log('User city:', authStore.userCity)
  console.log('User city_name from user object:', authStore.user?.city_name)
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})

const updateTime = () => {
  currentTime.value = new Date().toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleLogout = async () => {
  console.log('Logout clicked!') // Для отладки
  try {
    await authStore.logout()
    console.log('Logout successful, redirecting...')
    router.push('/worker/login')
  } catch (error) {
    console.error('Logout error:', error)
  }
}

// Директива для закрытия меню при клике вне его
const vClickOutside = {
  beforeMount(el, binding) {
    el.clickOutsideEvent = function(event) {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value()
      }
    }
    document.addEventListener('click', el.clickOutsideEvent)
  },
  unmounted(el) {
    document.removeEventListener('click', el.clickOutsideEvent)
  }
}
</script>