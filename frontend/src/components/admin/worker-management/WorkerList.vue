<template>
  <div class="worker-list">
    <!-- Показываем загрузку -->
    <div v-if="loading" class="loading-indicator">
      <div class="spinner"></div>
      <p>Загрузка работников...</p>
    </div>

    <!-- Показываем пустое состояние -->
    <div v-else-if="!workers || workers.length === 0" class="empty-state">
      <h3>Работники не найдены</h3>
      <p>Добавьте первого работника или измените фильтры поиска</p>
    </div>

    <!-- Показываем список работников -->
    <div v-else class="workers-grid">
      <WorkerCard
        v-for="worker in workers"
        :key="worker.id"
        :worker="worker"
        :cities="cities"
        @edit-worker="handleEditWorker"
        @delete-worker="handleDeleteWorker"
        @toggle-status="handleToggleStatus"
      />
    </div>
  </div>
</template>

<script setup>
import '@/assets/styles/components/admin/worker-management/WorkerList.css'
import WorkerCard from './WorkerCard.vue'

defineProps({
  workers: {
    type: Array,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  cities: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['edit-worker', 'delete-worker', 'toggle-status'])

// Функции-обработчики с отладкой
const handleEditWorker = (worker) => {
  console.log('📋 WorkerList: получено событие edit-worker для работника:', worker)
  emit('edit-worker', worker)
}

const handleDeleteWorker = (workerId) => {
  console.log('📋 WorkerList: получено событие delete-worker для ID:', workerId)
  emit('delete-worker', workerId)
}

const handleToggleStatus = (workerId) => {
  console.log('📋 WorkerList: получено событие toggle-status для ID:', workerId)
  emit('toggle-status', workerId)
}
</script>