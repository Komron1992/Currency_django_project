<template>
  <div class="register">
    <h2>Регистрация</h2>

    <div v-if="userStore.error" class="error">
      {{ userStore.error }}
    </div>

    <div v-if="successMessage" class="success">
      {{ successMessage }}
    </div>

    <form @submit.prevent="handleRegister">
      <div>
        <label for="username">Имя пользователя:</label>
        <input
          type="text"
          id="username"
          v-model="username"
          required
          :disabled="userStore.loading"
        />
      </div>

      <div>
        <label for="email">Email:</label>
        <input
          type="email"
          id="email"
          v-model="email"
          :disabled="userStore.loading"
        />
      </div>

      <div>
        <label for="password">Пароль:</label>
        <input
          type="password"
          id="password"
          v-model="password"
          required
          :disabled="userStore.loading"
        />
      </div>

      <div>
        <label for="password_confirm">Подтверждение пароля:</label>
        <input
          type="password"
          id="password_confirm"
          v-model="password_confirm"
          required
          :disabled="userStore.loading"
        />
      </div>

      <div>
        <label for="first_name">Имя:</label>
        <input
          type="text"
          id="first_name"
          v-model="first_name"
          :disabled="userStore.loading"
        />
      </div>

      <div>
        <label for="last_name">Фамилия:</label>
        <input
          type="text"
          id="last_name"
          v-model="last_name"
          :disabled="userStore.loading"
        />
      </div>

      <div>
        <label for="phone">Телефон:</label>
        <input
          type="tel"
          id="phone"
          v-model="phone"
          placeholder="+992 XX XXX XX XX"
          :disabled="userStore.loading"
        />
      </div>

      <div>
        <label for="date_of_birth">Дата рождения:</label>
        <input
          type="date"
          id="date_of_birth"
          v-model="date_of_birth"
          :disabled="userStore.loading"
        />
      </div>

      <button type="submit" :disabled="userStore.loading">
        {{ userStore.loading ? 'Регистрация...' : 'Зарегистрироваться' }}
      </button>
    </form>

    <p>Уже есть аккаунт? <router-link to="/login">Войти</router-link></p>
  </div>
</template>

<script setup>
import '@/assets/styles/views/public/Register.css'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUsersStore } from '@/stores/users'

const router = useRouter()
const userStore = useUsersStore()

const username = ref('')
const email = ref('')
const password = ref('')
const password_confirm = ref('')
const first_name = ref('')
const last_name = ref('')
const phone = ref('')
const date_of_birth = ref('')
const successMessage = ref('')

const handleRegister = async () => {
  // Проверка совпадения паролей на фронтенде
  if (password.value !== password_confirm.value) {
    userStore.error = 'Пароли не совпадают'
    return
  }

  const result = await userStore.register({
    username: username.value,
    email: email.value,
    password: password.value,
    password_confirm: password_confirm.value,
    first_name: first_name.value,
    last_name: last_name.value,
    phone: phone.value,
    date_of_birth: date_of_birth.value
  })

  if (result.success) {
    successMessage.value = result.message
    console.log('[Register] Success:', result.message)

    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } else {
    console.log('[Register] Failed:', result.error)
  }
}
</script>