<template>
  <div class="test-container">
    <h2>Тест модального окна</h2>

    <!-- Отладочная информация -->
    <div class="debug-panel">
      <h3>Состояние:</h3>
      <p><strong>showModal:</strong> {{ showModal }}</p>
      <p><strong>cities.length:</strong> {{ cities.length }}</p>
      <p><strong>Время последнего клика:</strong> {{ lastClickTime }}</p>
    </div>

    <!-- Кнопки тестирования -->
    <div class="buttons">
      <button @click="toggleModal" class="test-btn primary">
        {{ showModal ? 'Закрыть' : 'Открыть' }} модальное окно
      </button>

      <button @click="forceOpen" class="test-btn success">
        Принудительно открыть
      </button>

      <button @click="resetState" class="test-btn warning">
        Сбросить состояние
      </button>

      <button @click="loadCities" class="test-btn info">
        Загрузить города
      </button>
    </div>

    <!-- Простое модальное окно для теста -->
    <div v-if="showModal" class="simple-modal-overlay" @click.self="closeModal">
      <div class="simple-modal-content">
        <div class="simple-modal-header">
          <h3>Тестовое модальное окно</h3>
          <button @click="closeModal" class="simple-close-btn">&times;</button>
        </div>
        <div class="simple-modal-body">
          <p>Если вы видите это окно, значит модальные окна работают!</p>
          <p><strong>Количество городов:</strong> {{ cities.length }}</p>
          <div v-if="cities.length > 0">
            <p><strong>Первый город:</strong> {{ cities[0].name }}</p>
          </div>
        </div>
        <div class="simple-modal-footer">
          <button @click="closeModal" class="test-btn">Закрыть</button>
        </div>
      </div>
    </div>

    <!-- Ваш WorkerModal для сравнения -->
    <WorkerModal
      :isVisible="showWorkerModal"
      :editingWorker="null"
      :cities="cities"
      :saving="false"
      @close="closeWorkerModal"
      @save="handleSave"
    />

    <div class="worker-modal-test">
      <h3>Тест WorkerModal:</h3>
      <p><strong>showWorkerModal:</strong> {{ showWorkerModal }}</p>
      <button @click="openWorkerModal" class="test-btn primary">
        Открыть WorkerModal
      </button>
    </div>

    <!-- Консольные логи -->
    <div class="console-logs">
      <h3>Логи:</h3>
      <div class="logs-container">
        <div v-for="(log, index) in logs" :key="index" class="log-entry">
          <span class="log-time">{{ log.time }}</span>
          <span class="log-message">{{ log.message }}</span>
        </div>
      </div>
      <button @click="clearLogs" class="test-btn">Очистить логи</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
// Импортируйте ваш WorkerModal
// import WorkerModal from '@/components/admin/worker-management/WorkerModal.vue'

// Для тестирования создадим заглушку
const WorkerModal = {
  template: `
    <div v-if="isVisible" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000;">
      <div style="background: white; padding: 20px; border-radius: 8px; max-width: 500px; width: 90%;">
        <h3>WorkerModal работает!</h3>
        <p>Cities: {{ cities.length }}</p>
        <button @click="$emit('close')" style="padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">
          Закрыть
        </button>
      </div>
    </div>
  `,
  props: ['isVisible', 'editingWorker', 'cities', 'saving'],
  emits: ['close', 'save']
}

// Реактивные данные
const showModal = ref(false)
const showWorkerModal = ref(false)
const cities = ref([])
const lastClickTime = ref('')
const logs = ref([])

// Функции логирования
const addLog = (message) => {
  const time = new Date().toLocaleTimeString()
  logs.value.unshift({ time, message })
  console.log(`[${time}] ${message}`)
  if (logs.value.length > 10) {
    logs.value = logs.value.slice(0, 10)
  }
}

const clearLogs = () => {
  logs.value = []
  console.clear()
}

// Функции для простого модального окна
const toggleModal = () => {
  lastClickTime.value = new Date().toLocaleTimeString()
  addLog(`Переключение модального окна: ${showModal.value} -> ${!showModal.value}`)
  showModal.value = !showModal.value
}

const forceOpen = () => {
  addLog('Принудительное открытие модального окна')
  showModal.value = true
}

const closeModal = () => {
  addLog('Закрытие простого модального окна')
  showModal.value = false
}

const resetState = () => {
  addLog('Сброс состояния')
  showModal.value = false
  showWorkerModal.value = false
}

// Функции для WorkerModal
const openWorkerModal = () => {
  addLog('Попытка открытия WorkerModal')
  showWorkerModal.value = true
  addLog(`WorkerModal состояние после клика: ${showWorkerModal.value}`)
}

const closeWorkerModal = () => {
  addLog('Закрытие WorkerModal')
  showWorkerModal.value = false
}

const handleSave = (data) => {
  addLog('Сохранение данных из WorkerModal: ' + JSON.stringify(data))
  closeWorkerModal()
}

// Загрузка городов
const loadCities = () => {
  addLog('Загрузка городов...')
  cities.value = [
    { id: 1, name: 'Душанбе' },
    { id: 2, name: 'Худжанд' },
    { id: 3, name: 'Куляб' },
    { id: 4, name: 'Курган-Тюбе' },
    { id: 5, name: 'Истаравшан' }
  ]
  addLog(`Загружено городов: ${cities.value.length}`)
}

// Инициализация
onMounted(() => {
  addLog('Компонент загружен')
  loadCities()
})
</script>

<style scoped>
.test-container {
  padding: 20px;
  font-family: Arial, sans-serif;
}

.debug-panel {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 5px;
  margin-bottom: 20px;
  border: 1px solid #dee2e6;
}

.debug-panel h3 {
  margin-top: 0;
  color: #495057;
}

.debug-panel p {
  margin: 5px 0;
  font-family: monospace;
}

.buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.test-btn {
  padding: 10px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.test-btn.primary {
  background-color: #007bff;
  color: white;
}

.test-btn.primary:hover {
  background-color: #0056b3;
}

.test-btn.success {
  background-color: #28a745;
  color: white;
}

.test-btn.success:hover {
  background-color: #1e7e34;
}

.test-btn.warning {
  background-color: #ffc107;
  color: #212529;
}

.test-btn.warning:hover {
  background-color: #e0a800;
}

.test-btn.info {
  background-color: #17a2b8;
  color: white;
}

.test-btn.info:hover {
  background-color: #117a8b;
}

.test-btn:not(.primary):not(.success):not(.warning):not(.info) {
  background-color: #6c757d;
  color: white;
}

.test-btn:not(.primary):not(.success):not(.warning):not(.info):hover {
  background-color: #5a6268;
}

/* Простое модальное окно */
.simple-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.simple-modal-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 90%;
  max-width: 500px;
}

.simple-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 20px 10px;
  border-bottom: 1px solid #e9ecef;
}

.simple-modal-header h3 {
  margin: 0;
  color: #333;
}

.simple-close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6c757d;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.simple-close-btn:hover {
  background-color: #f8f9fa;
  color: #333;
}

.simple-modal-body {
  padding: 20px;
}

.simple-modal-footer {
  padding: 10px 20px 20px;
  text-align: right;
}

.worker-modal-test {
  background: #e3f2fd;
  padding: 15px;
  border-radius: 5px;
  margin: 20px 0;
  border: 1px solid #bbdefb;
}

.worker-modal-test h3 {
  margin-top: 0;
  color: #1976d2;
}

.console-logs {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 5px;
  margin-top: 20px;
  border: 1px solid #ddd;
}

.console-logs h3 {
  margin-top: 0;
  color: #333;
}

.logs-container {
  max-height: 200px;
  overflow-y: auto;
  background: white;
  padding: 10px;
  border-radius: 3px;
  margin: 10px 0;
  font-family: monospace;
  font-size: 12px;
}

.log-entry {
  display: flex;
  margin-bottom: 5px;
  padding: 2px 0;
  border-bottom: 1px solid #eee;
}

.log-time {
  color: #666;
  margin-right: 10px;
  white-space: nowrap;
}

.log-message {
  color: #333;
}
</style>