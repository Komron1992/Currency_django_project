<template>
  <div class="worker-card" :class="{ inactive: !worker.is_worker_active }">
    <div class="card-header">
      <div class="worker-info">
        <div class="avatar">
          {{ getInitials(worker.full_name || worker.username) }}
        </div>
        <div class="info">
          <h3>{{ worker.full_name || worker.username }}</h3>
          <p class="username">@{{ worker.username }}</p>
        </div>
      </div>
      <div class="status-badge" :class="worker.is_worker_active ? 'active' : 'inactive'">
        {{ worker.is_worker_active ? 'Активен' : 'Неактивен' }}
      </div>
    </div>

    <div class="card-content">
      <div class="detail-row" v-if="worker.email">
        <span class="icon">📧</span>
        <span>{{ worker.email }}</span>
      </div>
      <div class="detail-row" v-if="worker.phone">
        <span class="icon">📱</span>
        <span>{{ worker.phone }}</span>
      </div>
      <div class="detail-row" v-if="worker.city_name">
        <span class="icon">🏙️</span>
        <span>{{ worker.city_name }}</span>
      </div>
      <div class="detail-row" v-if="worker.date_joined">
        <span class="icon">📅</span>
        <span>Присоединился {{ formatDate(worker.date_joined) }}</span>
      </div>
      <div class="detail-row" v-if="worker.last_login">
        <span class="icon">🕐</span>
        <span>Последний вход {{ formatDate(worker.last_login) }}</span>
      </div>
    </div>

    <div class="card-actions">
      <button @click="handleEdit" class="action-btn edit-btn">
        <span class="icon">✏️</span>
        Редактировать
      </button>
      <button
        @click="handleToggleStatus"
        class="action-btn toggle-btn"
        :class="worker.is_worker_active ? 'deactivate' : 'activate'"
      >
        <span class="icon">{{ worker.is_worker_active ? '⏸️' : '▶️' }}</span>
        {{ worker.is_worker_active ? 'Деактивировать' : 'Активировать' }}
      </button>
      <button @click="handleDelete" class="action-btn delete-btn">
        <span class="icon">🗑️</span>
        Удалить
      </button>
    </div>
  </div>
</template>

<script setup>
import '@/assets/styles/components/admin/worker-management/WorkerCard.css'

const props = defineProps({
  worker: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['edit-worker', 'delete-worker', 'toggle-status'])

const getInitials = (name) => {
  if (!name) return '?'
  return name
    .split(' ')
    .map(word => word.charAt(0))
    .join('')
    .substring(0, 2)
    .toUpperCase()
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// Обработчики событий с правильными именами
const handleEdit = () => {
  console.log('🔧 WorkerCard: эмитим edit-worker для:', props.worker)
  emit('edit-worker', props.worker)
}

const handleDelete = () => {
  console.log('🗑️ WorkerCard: эмитим delete-worker для ID:', props.worker.id)
  emit('delete-worker', props.worker.id)
}

const handleToggleStatus = () => {
  console.log('🔄 WorkerCard: эмитим toggle-status для ID:', props.worker.id)
  emit('toggle-status', props.worker.id)
}
</script>