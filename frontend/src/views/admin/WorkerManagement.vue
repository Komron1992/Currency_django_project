<template>
  <div class="worker-management">
    <PageHeader
      title="Управление работниками"
      :show-debug="showDebug"
      @toggle-debug="showDebug = !showDebug"
      @add-worker="openAddWorkerModal"
    />

    <!-- Диагностика API -->
    <div v-if="showDebug" class="debug-panel">
      <h3>Диагностика API:</h3>
      <div class="debug-info">
        <p><strong>API URL:</strong> {{ debugInfo.apiUrl }}</p>
        <p><strong>Заголовки:</strong> {{ JSON.stringify(debugInfo.headers) }}</p>
        <p><strong>Статус ответа:</strong> {{ debugInfo.responseStatus }}</p>
        <p><strong>Тип ответа:</strong> {{ debugInfo.responseType }}</p>
        <p><strong>Городов загружено:</strong> {{ cities.length }}</p>
        <p><strong>Работников загружено:</strong> {{ workers.length }}</p>
      </div>
      <button @click="showDebug = false" class="btn-hide-debug">Скрыть диагностику</button>
    </div>

    <!-- Загрузка данных -->
    <div v-if="isInitialLoading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Загрузка данных...</p>
    </div>

    <!-- Основной контент -->
    <div v-else>
      <!-- Статистика -->
      <WorkerStates
        :total="workers.length"
        :active="activeWorkersCount"
        :inactive="inactiveWorkersCount"
        :filtered="filteredWorkers.length"
      />

      <!-- Список работников -->
      <WorkerList
        :workers="filteredWorkers"
        :loading="workersLoading"
        :cities="cities"
        @edit-worker="handleEditWorker"
        @delete-worker="handleDeleteWorker"
        @toggle-status="handleToggleStatus"
      />
    </div>

    <!-- Модальное окно для добавления/редактирования -->
    <WorkerModal
      :isVisible="showModal"
      :worker="selectedWorker"
      :cities="cities"
      :isEditing="isEditing"
      @close="closeModal"
      @worker-saved="handleWorkerSaved"
    />

    <!-- Отладочная информация для модального окна -->
    <div v-if="showDebug && showModal" class="modal-debug-info">
      <div class="debug-modal">
        <h4>Отладка модального окна:</h4>
        <p><strong>Режим редактирования:</strong> {{ isEditing ? 'Да' : 'Нет' }}</p>
        <p><strong>Выбранный работник:</strong> {{ selectedWorker ? selectedWorker.username : 'Нет' }}</p>
        <p><strong>Городов передано:</strong> {{ cities.length }}</p>
        <p><strong>Первый город:</strong> {{ cities[0]?.name || 'Нет данных' }}</p>
        <p><strong>Состояние загрузки городов:</strong> {{ citiesLoading ? 'Загружается' : 'Готово' }}</p>
        <p><strong>Статус сохранения:</strong> {{ saving ? 'Сохраняется' : 'Готово' }}</p>
      </div>
    </div>

    <!-- Глобальные уведомления -->
    <div v-if="globalMessage" class="global-message" :class="globalMessage.type">
      {{ globalMessage.text }}
    </div>
  </div>
</template>

<script>
import '@/assets/styles/views/admin/WorkerManagement.css'
import { ref, computed, onMounted, reactive, nextTick, watch } from 'vue'
import { useWorkers } from '@/composables/useWorkers'
import { useNotifications } from '@/composables/useNotifications'
import { adminAPI } from '@/services/api.js'
import { citiesService } from '@/services/cities.js'

// Компоненты
import PageHeader from '@/components/admin/worker-management/PageHeader.vue'
import WorkerStates from '@/components/admin/worker-management/WorkerStates.vue'
import WorkerList from '@/components/admin/worker-management/WorkerList.vue'
import WorkerModal from '@/components/admin/worker-management/WorkerModal.vue'

export default {
  name: 'WorkerManagement',
  components: {
    PageHeader,
    WorkerStates,
    WorkerList,
    WorkerModal
  },
  setup() {
    // Состояние компонента
    const showDebug = ref(false)
    const showModal = ref(false)
    const selectedWorker = ref(null)
    const isEditing = ref(false)
    const saving = ref(false)
    const isInitialLoading = ref(true)
    const citiesLoading = ref(false)
    const globalMessage = ref(null)

    // Композаблы
    const {
      workers,
      loading: workersLoading,
      loadWorkers,
      updateWorker,
      deleteWorker,
      createWorker
    } = useWorkers()

    const { showSuccess, showError } = useNotifications()

    // Данные
    const cities = ref([])

    // Отладочная информация
    const debugInfo = reactive({
      apiUrl: '/cities.json',
      headers: {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json"
      },
      responseStatus: 200,
      responseType: 'json',
      lastUpdate: null
    })

    // Функция для показа глобального сообщения
    const showGlobalMessage = (text, type = 'info') => {
      globalMessage.value = { text, type }
      setTimeout(() => {
        globalMessage.value = null
      }, 5000)
    }

    // Улучшенная функция загрузки городов
    const loadCities = async (force = false) => {
      if (cities.value.length > 0 && !force) {
        console.log('🏙️ Города уже загружены:', cities.value.length)
        return cities.value
      }

      console.log('🏙️ Загрузка городов...')
      citiesLoading.value = true

      try {
        const citiesData = force ?
          await citiesService.reloadCities() :
          await citiesService.getAllCities()

        cities.value = citiesData.map(city => ({
          id: city.id,
          name: city.name,
          region: city.region || '',
          name_en: city.name_en || ''
        }))

        console.log('✅ Города загружены успешно:', cities.value.length)

        // Обновляем отладочную информацию
        debugInfo.responseStatus = 200
        debugInfo.responseType = 'json'
        debugInfo.lastUpdate = new Date().toLocaleString()

        return cities.value

      } catch (error) {
        console.error('❌ Ошибка загрузки городов:', error)

        debugInfo.responseStatus = 'ERROR'
        debugInfo.responseType = 'error'
        debugInfo.lastUpdate = new Date().toLocaleString()

        showGlobalMessage('Ошибка загрузки списка городов', 'error')
        return []
      } finally {
        citiesLoading.value = false
      }
    }

    // Вычисляемые свойства
    const filteredWorkers = computed(() => {
      if (!workers.value || !Array.isArray(workers.value)) {
        return []
      }
      return workers.value
    })

    const activeWorkersCount = computed(() => {
      if (!workers.value || workers.value.length === 0) {
        return 0
      }
      return workers.value.filter(worker =>
        worker.is_active || worker.is_worker_active
      ).length
    })

    const inactiveWorkersCount = computed(() => {
      if (!workers.value || workers.value.length === 0) {
        return 0
      }
      return workers.value.filter(worker =>
        !worker.is_worker_active && !worker.is_active
      ).length
    })

    // Открытие модального окна для добавления
    const openAddWorkerModal = async () => {
      console.log('🆕 Открытие модального окна для добавления работника')

      // Убеждаемся, что города загружены
      if (cities.value.length === 0) {
        console.log('🏙️ Города не загружены, загружаем...')
        await loadCities()
      }

      await nextTick()

      selectedWorker.value = null
      isEditing.value = false
      showModal.value = true

      console.log('🆕 Модальное окно для добавления открыто')
    }

    // Редактирование работника
    const handleEditWorker = async (worker) => {
      console.log('✏️ Начало редактирования работника:', worker.username)

      // Убеждаемся, что города загружены
      if (cities.value.length === 0) {
        console.log('🏙️ Города не загружены для редактирования, загружаем...')
        await loadCities()
      }

      await nextTick()

      // Создаем копию объекта работника для редактирования
      selectedWorker.value = { ...worker }
      isEditing.value = true
      showModal.value = true

      console.log('✏️ Модальное окно для редактирования открыто')
    }

    // Удаление работника
    const handleDeleteWorker = async (workerId) => {
      console.log('🗑️ Начало удаления работника:', workerId)

      if (!workerId) {
        console.error('❌ ID работника не предоставлен')
        showError('Ошибка: ID работника не найден')
        return
      }

      const worker = workers.value.find(w => w.id === workerId)
      const workerName = worker ?
        `${worker.first_name || ''} ${worker.last_name || ''}`.trim() || worker.username :
        `ID: ${workerId}`

      if (!confirm(`Вы уверены, что хотите удалить работника ${workerName}?`)) {
        return
      }

      try {
        await deleteWorker(workerId)
        showSuccess('Работник успешно удален')
        await loadWorkers()
        console.log('✅ Работник удален и список обновлен')
      } catch (error) {
        console.error('❌ Ошибка при удалении работника:', error)
        showError('Ошибка при удалении работника')
      }
    }

    // Переключение статуса работника
    const handleToggleStatus = async (workerId) => {
      console.log('🔄 Переключение статуса работника:', workerId)

      if (!workerId) {
        console.error('❌ ID работника не предоставлен')
        showError('Ошибка: ID работника не найден')
        return
      }

      const worker = workers.value.find(w => w.id === workerId)
      if (!worker) {
        console.error('❌ Работник не найден по ID:', workerId)
        showError('Ошибка: работник не найден')
        return
      }

      try {
        const currentStatus = worker.is_worker_active
        const newStatus = !currentStatus

        // Обновляем статус работника
        const updatedData = {
          is_worker_active: newStatus
        }

        await updateWorker(worker.id, updatedData)

        const statusText = newStatus ? 'активирован' : 'деактивирован'
        showSuccess(`Работник ${statusText}`)

        // Перезагружаем список работников
        await loadWorkers()

        console.log('✅ Статус работника обновлен')
      } catch (error) {
        console.error('❌ Ошибка при изменении статуса:', error)
        showError('Ошибка при изменении статуса')
      }
    }

    // Обработчик сохранения работника
    const handleWorkerSaved = async (workerData) => {
      console.log('💾 Обработка сохранения работника:', workerData)

      try {
        // Перезагружаем список работников
        await loadWorkers()

        const action = isEditing.value ? 'обновлен' : 'создан'
        showSuccess(`Работник успешно ${action}`)

        console.log('✅ Список работников обновлен после сохранения')

        // Закрываем модальное окно
        closeModal()

      } catch (error) {
        console.error('❌ Ошибка при обновлении списка работников:', error)
        showError('Ошибка при обновлении данных')
      }
    }

    // Закрытие модального окна
    const closeModal = () => {
      console.log('❌ Закрытие модального окна')
      showModal.value = false
      selectedWorker.value = null
      isEditing.value = false
      saving.value = false
    }

    // Функция обновления данных
    const refreshData = async () => {
      console.log('🔄 Обновление всех данных')
      isInitialLoading.value = true

      try {
        await Promise.all([
          loadWorkers(),
          loadCities(true) // Принудительно перезагружаем города
        ])
        showSuccess('Данные обновлены')
      } catch (error) {
        console.error('❌ Ошибка при обновлении данных:', error)
        showError('Ошибка при обновлении данных')
      } finally {
        isInitialLoading.value = false
      }
    }

    // Отслеживание изменений в модальном окне
    watch(showModal, (newValue) => {
      if (newValue) {
        console.log('👁️ Модальное окно открыто')
        console.log('📊 Статус:', {
          isEditing: isEditing.value,
          hasWorker: !!selectedWorker.value,
          citiesCount: cities.value.length
        })
      } else {
        console.log('👁️ Модальное окно закрыто')
      }
    })

    // Инициализация компонента
    onMounted(async () => {
      console.log('🚀 Инициализация WorkerManagement')

      try {
        // Параллельно загружаем данные
        await Promise.all([
          loadWorkers().catch(error => {
            console.error('❌ Ошибка загрузки работников:', error)
            showError('Ошибка при загрузке работников')
          }),
          loadCities().catch(error => {
            console.error('❌ Ошибка загрузки городов:', error)
            // Не критично, модальное окно будет работать с пустым списком
          })
        ])

        console.log('✅ Инициализация завершена успешно')
        console.log('📊 Загружено:', {
          workers: workers.value?.length || 0,
          cities: cities.value?.length || 0
        })

      } catch (error) {
        console.error('❌ Критическая ошибка инициализации:', error)
        showError('Критическая ошибка при загрузке')
      } finally {
        isInitialLoading.value = false
      }
    })

    return {
      // Состояние
      showDebug,
      showModal,
      selectedWorker,
      isEditing,
      saving,
      workersLoading,
      isInitialLoading,
      citiesLoading,
      globalMessage,

      // Данные
      workers,
      cities,
      debugInfo,

      // Вычисляемые свойства
      filteredWorkers,
      activeWorkersCount,
      inactiveWorkersCount,

      // Методы
      openAddWorkerModal,
      handleEditWorker,
      handleDeleteWorker,
      handleToggleStatus,
      handleWorkerSaved,
      closeModal,
      loadCities,
      refreshData,
      showGlobalMessage
    }
  }
}
</script>

<style scoped>
.worker-management {
  padding: 20px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 3rem;
  gap: 1rem;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.debug-panel {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.debug-info {
  background: #fff;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  padding: 0.5rem;
  margin: 0.5rem 0;
  font-family: monospace;
  font-size: 0.9rem;
}

.debug-info p {
  margin: 0.25rem 0;
}

.btn-hide-debug {
  background: #6c757d;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 0.5rem;
}

.btn-hide-debug:hover {
  background: #5a6268;
}

.modal-debug-info {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 10001;
  max-width: 350px;
}

.debug-modal {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  font-size: 0.9rem;
}

.debug-modal h4 {
  margin: 0 0 0.5rem 0;
  color: #856404;
}

.debug-modal p {
  margin: 0.25rem 0;
  color: #856404;
}

.global-message {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 1rem 2rem;
  border-radius: 8px;
  font-weight: 500;
  z-index: 10000;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  animation: slideDown 0.3s ease-out;
}

.global-message.info {
  background: #d1ecf1;
  color: #0c5460;
  border: 1px solid #b6d4da;
}

.global-message.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.global-message.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

/* Отзывчивость */
@media (max-width: 768px) {
  .worker-management {
    padding: 10px;
  }

  .modal-debug-info {
    top: 10px;
    right: 10px;
    max-width: 280px;
  }

  .global-message {
    left: 10px;
    right: 10px;
    transform: none;
    max-width: calc(100% - 20px);
  }
}
</style>