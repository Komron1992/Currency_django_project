<template>
  <div class="login">
    <h2>Вход</h2>

    <div v-if="error" class="error">
      {{ error }}
    </div>

    <form @submit.prevent="handleLogin">
      <div>
        <label for="username">Имя пользователя:</label>
        <input
          type="text"
          id="username"
          v-model="username"
          required
          :disabled="loading"
        />
      </div>

      <div>
        <label for="password">Пароль:</label>
        <input
          type="password"
          id="password"
          v-model="password"
          required
          :disabled="loading"
        />
      </div>

      <button type="submit" :disabled="loading">
        {{ loading ? 'Вход...' : 'Войти' }}
      </button>
    </form>

    <p>Нет аккаунта? <router-link to="/register">Зарегистрироваться</router-link></p>
  </div>
</template>

<script setup>
import '@/assets/styles/views/public/Login.css'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth' // Изменено с useUsersStore на useAuthStore

const router = useRouter()
const authStore = useAuthStore() // Изменено с userStore на authStore

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  try {
    loading.value = true
    error.value = ''

    const result = await authStore.login({
      username: username.value,
      password: password.value
    })

    if (result.success) {
      console.log('[Login] Success, redirecting to home')
      router.push('/')
    } else {
      console.log('[Login] Failed:', result.error)
      error.value = result.error || 'Ошибка входа'
    }
  } catch (err) {
    console.error('[Login] Exception:', err)
    error.value = 'Произошла ошибка при входе'
  } finally {
    loading.value = false
  }
}
</script>
