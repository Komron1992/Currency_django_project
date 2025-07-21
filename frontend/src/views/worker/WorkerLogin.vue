<template>
  <div class="login-container">
    <!-- Анимированный фон -->
    <div class="animated-bg">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>
    </div>

    <!-- Основной контейнер -->
    <div class="main-container">
      <!-- Логотип и заголовок -->
      <div class="header">
        <div class="logo">
          <div class="logo-icon">🏢</div>
        </div>
        <h1 class="title">Рабочая панель</h1>
        <p class="subtitle">Вход для работников обменных пунктов</p>
      </div>

      <!-- Форма входа -->
      <div class="form-container">
        <form @submit.prevent="handleLogin" class="login-form">
          <!-- Поле username -->
          <div class="input-group">
            <label for="username" class="input-label">
              Имя пользователя
            </label>
            <div class="input-wrapper">
              <div class="input-icon">
                <span>👤</span>
              </div>
              <input
                id="username"
                v-model="form.username"
                type="text"
                required
                class="input-field"
                placeholder="Введите имя пользователя"
                :disabled="loading"
                autocomplete="username"
              />
            </div>
          </div>

          <!-- Поле password -->
          <div class="input-group">
            <label for="password" class="input-label">
              Пароль
            </label>
            <div class="input-wrapper">
              <div class="input-icon">
                <span>🔒</span>
              </div>
              <input
                id="password"
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                required
                class="input-field password-field"
                placeholder="Введите пароль"
                :disabled="loading"
                autocomplete="current-password"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="password-toggle"
                :disabled="loading"
                :title="showPassword ? 'Скрыть пароль' : 'Показать пароль'"
              >
                <span v-if="showPassword">👁️</span>
                <span v-else>🙈</span>
              </button>
            </div>
          </div>

          <!-- Кнопка входа -->
          <button
            type="submit"
            class="login-button"
            :class="{ 'loading': loading }"
            :disabled="loading"
          >
            <span v-if="loading" class="loading-content">
              <svg class="spinner" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Вход...
            </span>
            <span v-else>Войти в систему</span>
          </button>
        </form>

        <!-- Сообщение об ошибке -->
        <Transition
          enter-active-class="error-enter-active"
          enter-from-class="error-enter-from"
          enter-to-class="error-enter-to"
          leave-active-class="error-leave-active"
          leave-from-class="error-leave-from"
          leave-to-class="error-leave-to"
        >
          <div v-if="error" class="error-message">
            <div class="error-content">
              <span>⚠️</span>
              <p class="error-text">{{ error }}</p>
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import '@/assets/styles/views/worker/WorkerLogin.css'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  username: '',
  password: ''
})

const showPassword = ref(false)
const loading = ref(false)
const error = ref('')

// Если уже авторизован, перенаправляем на дашборд
onMounted(() => {
  if (authStore.isAuthenticated && authStore.isCityWorker) {
    router.push('/worker/dashboard')
  }
})

const handleLogin = async () => {
  // Очищаем предыдущие ошибки
  error.value = ''

  // Валидация формы
  if (!form.value.username.trim()) {
    error.value = 'Введите имя пользователя'
    return
  }

  if (!form.value.password.trim()) {
    error.value = 'Введите пароль'
    return
  }

  if (form.value.username.trim().length < 3) {
    error.value = 'Имя пользователя должно содержать минимум 3 символа'
    return
  }

  if (form.value.password.length < 4) {
    error.value = 'Пароль должен содержать минимум 4 символа'
    return
  }

  loading.value = true

  try {
    const result = await authStore.login({
      username: form.value.username.trim(),
      password: form.value.password
    })

    if (result.success) {
      // Успешная авторизация
      router.push('/worker/dashboard')
    } else {
      error.value = result.error || 'Неверное имя пользователя или пароль'
    }
  } catch (err) {
    console.error('Login error:', err)

    // Обработка различных типов ошибок
    if (err.response?.status === 401) {
      error.value = 'Неверное имя пользователя или пароль'
    } else if (err.response?.status === 403) {
      error.value = 'Доступ запрещен. Обратитесь к администратору'
    } else if (err.response?.status === 429) {
      error.value = 'Слишком много попыток входа. Попробуйте позже'
    } else if (err.code === 'NETWORK_ERROR') {
      error.value = 'Ошибка сети. Проверьте подключение к интернету'
    } else {
      error.value = 'Произошла ошибка при входе. Попробуйте еще раз'
    }
  } finally {
    loading.value = false
  }
}

// Обработка Enter в форме
const handleKeyPress = (event) => {
  if (event.key === 'Enter' && !loading.value) {
    handleLogin()
  }
}
</script>