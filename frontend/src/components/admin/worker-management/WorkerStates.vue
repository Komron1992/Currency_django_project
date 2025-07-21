<!-- WorkerStates.vue -->
<template>
  <div class="worker-states">
    <!-- Состояние загрузки -->
    <div v-if="loading" class="state-container loading">
      <div class="loading-spinner"></div>
      <p>Загрузка работников...</p>
    </div>

    <!-- Состояние ошибки -->
    <div v-else-if="error" class="state-container error">
      <div class="error-icon">⚠️</div>
      <h3>Ошибка загрузки</h3>
      <p>{{ error }}</p>
      <button @click="$emit('retry')" class="retry-btn">
        Попробовать снова
      </button>
    </div>

    <!-- Пустое состояние -->
    <div v-else-if="workersCount === 0" class="state-container empty">
      <div class="empty-icon">👥</div>
      <h3>Работники не найдены</h3>
      <p>Добавьте первого работника для начала работы</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  loading: {
    type: Boolean,
    required: true
  },
  error: {
    type: String,
    default: ''
  },
  workersCount: {
    type: Number,
    required: true
  }
})

defineEmits(['retry'])
</script>

<style scoped>
.worker-states {
  width: 100%;
}

.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  margin: 20px 0;
}

.loading .loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon,
.empty-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.state-container h3 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 24px;
}

.state-container p {
  margin: 0 0 20px 0;
  color: #666;
  font-size: 16px;
}

.retry-btn {
  background: #667eea;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.retry-btn:hover {
  background: #5a6fd8;
}

.loading p {
  color: #667eea;
  font-weight: 500;
}
</style>