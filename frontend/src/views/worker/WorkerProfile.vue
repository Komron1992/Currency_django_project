<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-4xl mx-auto py-8 px-4">
      <!-- Заголовок -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">👤 Мой профиль</h1>
        <p class="mt-2 text-gray-600">Информация о работнике</p>
      </div>

      <!-- Основная карточка профиля -->
      <div class="profile-card">
        <div class="profile-header">
          <div class="profile-avatar">
            <span class="avatar-text">
              {{ getUserInitial }}
            </span>
          </div>
          <div class="profile-info">
            <h2 class="profile-name">{{ getUserName }}</h2>
            <p class="profile-email">{{ getUserEmail }}</p>
            <div class="profile-meta">
              <span class="meta-item">
                <span class="meta-icon">🏢</span>
                Работник
              </span>
              <span class="meta-item">
                <span class="meta-icon">📍</span>
                {{ getUserCity }}
              </span>
              <span class="meta-item">
                <span class="meta-icon">📅</span>
                {{ formatDate(authStore.user?.date_joined) }}
              </span>
            </div>
          </div>
          <div class="profile-status">
            <div class="status-indicator active"></div>
            <span class="status-text">Активен</span>
          </div>
        </div>
      </div>

      <!-- Детальная информация -->
      <div class="profile-card">
        <div class="profile-section">
          <h3 class="section-title">Личная информация</h3>
          <div class="info-grid">
            <div class="info-item">
              <label class="info-label">Имя пользователя</label>
              <div class="info-value">{{ getUserName }}</div>
            </div>
            <div class="info-item">
              <label class="info-label">Email</label>
              <div class="info-value">{{ getUserEmail }}</div>
            </div>
            <div class="info-item">
              <label class="info-label">Имя</label>
              <div class="info-value">{{ getUserFirstName }}</div>
            </div>
            <div class="info-item">
              <label class="info-label">Фамилия</label>
              <div class="info-value">{{ getUserLastName }}</div>
            </div>
            <div class="info-item">
              <label class="info-label">Телефон</label>
              <div class="info-value">{{ getUserPhone }}</div>
            </div>
            <div class="info-item">
              <label class="info-label">Город</label>
              <div class="info-value">{{ getUserCity }}</div>
            </div>
          </div>
        </div>

        <div class="profile-section">
          <h3 class="section-title">Системная информация</h3>
          <div class="info-grid">
            <div class="info-item">
              <label class="info-label">Дата регистрации</label>
              <div class="info-value">{{ formatDate(authStore.user?.date_joined) }}</div>
            </div>
            <div class="info-item">
              <label class="info-label">Последний вход</label>
              <div class="info-value">{{ formatDate(authStore.user?.last_login) }}</div>
            </div>
            <div class="info-item">
              <label class="info-label">Статус</label>
              <div class="info-value">
                <span class="status-badge active">Активен</span>
              </div>
            </div>
            <div class="info-item">
              <label class="info-label">Роль</label>
              <div class="info-value">
                <span class="role-badge">Работник</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import '@/assets/styles/views/worker/WorkerProfile.css'
import { onMounted, computed } from 'vue'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()

// Computed свойства для безопасного получения данных
const getUserName = computed(() => authStore.user?.username || 'Не указано')
const getUserEmail = computed(() => authStore.user?.email || 'Не указан')
const getUserFirstName = computed(() => authStore.user?.first_name || 'Не указано')
const getUserLastName = computed(() => authStore.user?.last_name || 'Не указано')
const getUserPhone = computed(() => authStore.user?.phone || 'Не указан')
const getUserCity = computed(() => {
  return authStore.userCity ||
         authStore.user?.city_name ||
         authStore.user?.city ||
         authStore.user?.profile?.city ||
         'Не указан'
})
const getUserInitial = computed(() => {
  const username = authStore.user?.username
  return username ? username.charAt(0).toUpperCase() : '?'
})

onMounted(async () => {
  if (!authStore.user) {
    try {
      await authStore.fetchUser()
    } catch (error) {
      console.error('Ошибка при загрузке данных пользователя:', error)
    }
  }
})

const formatDate = (dateString) => {
  if (!dateString || dateString === null) return 'Не указано'

  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) return 'Не указано'

    return date.toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    console.error('Ошибка при форматировании даты:', error)
    return 'Не указано'
  }
}
</script>
