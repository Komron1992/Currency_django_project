<template>
  <div class="market-exchange-rates-management">
    <PageHeader
      title="Управление рыночными курсами"
      :show-debug="showDebug"
      @toggle-debug="showDebug = !showDebug"
      @refresh-rates="handleRefreshRates"
    />

    <!-- Диагностика API -->
    <div v-if="showDebug" class="debug-panel">
      <h3>Диагностика API:</h3>
      <div class="debug-info">
        <p><strong>API URL:</strong> {{ debugInfo.apiUrl }}</p>
        <p><strong>Заголовки:</strong> {{ JSON.stringify(debugInfo.headers) }}</p>
        <p><strong>Статус ответа:</strong> {{ debugInfo.responseStatus }}</p>
        <p><strong>Записей загружено:</strong> {{ marketRates?.length || 0 }}</p>
      </div>
      <button @click="showDebug = false" class="btn-hide-debug">Скрыть диагностику</button>
    </div>

    <!-- Фильтры -->
    <div class="filters-section">
      <div class="filters-grid">
        <div class="filter-group">
          <label>Город:</label>
          <select v-model="filters.city" @change="applyFilters">
            <option value="">Все города</option>
            <option v-for="city in cities" :key="city.id" :value="city.name">
              {{ city.name }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label>Работник:</label>
          <select v-model="filters.worker" @change="applyFilters">
            <option value="">Все работники</option>
            <option v-for="worker in workers" :key="worker.id" :value="worker.id">
              {{ worker.username }} ({{ worker.city_name }})
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label>Дата от:</label>
          <input
            type="date"
            v-model="filters.dateFrom"
            @change="applyFilters"
            class="date-input"
          />
        </div>

        <div class="filter-group">
          <label>Дата до:</label>
          <input
            type="date"
            v-model="filters.dateTo"
            @change="applyFilters"
            class="date-input"
          />
        </div>

        <div class="filter-group">
          <button @click="resetFilters" class="btn-reset">Сбросить фильтры</button>
        </div>
      </div>
    </div>

    <!-- Список курсов -->
    <MarketRatesList
      :rates="filteredMarketRates"
      :loading="ratesLoading"
      :cities="cities"
      @edit="handleEditRate"
      @delete="handleDeleteRate"
      @refresh="handleRefreshRates"
    />

    <!-- Модальное окно для редактирования -->
    <MarketRatesModal
      :is-open="showModal"
      :rate-data="selectedRate"
      :loading="modalLoading"
      @update-rate="handleSaveRate"
      @close="closeModal"
    />
  </div>
</template>

<script>
import '@/assets/styles/views/admin/MarketRatesManagement.css'
import { ref, computed, onMounted } from 'vue'
import { useMarketRates } from '@/composables/useMarketRates'
import { useNotifications } from '@/composables/useNotifications'
import { adminAPI } from '@/services/admin.js'

// Компоненты
import PageHeader from '@/components/admin/market-exchange-rates/PageHeader.vue'
import MarketRatesList from '@/components/admin/market-exchange-rates/MarketRatesList.vue'
import MarketRatesModal from '@/components/admin/market-exchange-rates/MarketRatesModal.vue'

export default {
  name: 'MarketRatesManagement',
  components: {
    PageHeader,
    MarketRatesList,
    MarketRatesModal
  },
  setup() {
    // Состояние компонента
    const showDebug = ref(false)
    const showModal = ref(false)
    const selectedRate = ref(null)
    const modalLoading = ref(false)
    const cities = ref([])
    const workers = ref([])

    // Фильтры
    const filters = ref({
      city: '',
      worker: '',
      dateFrom: '',
      dateTo: ''
    })

    // Композаблы
    const {
      marketRates,
      loading: ratesLoading,
      loadMarketRates,
      updateMarketRate,
      deleteMarketRate
    } = useMarketRates()

    const { showSuccess, showError } = useNotifications()

    // Отладочная информация
    const debugInfo = ref({
      apiUrl: '/admin/market-exchange-rates/',
      headers: {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + (localStorage.getItem('token') || 'no-token')
      },
      responseStatus: 200,
      responseType: 'api-response'
    })

    // Вычисляемые свойства
    const filteredMarketRates = computed(() => {
      let filtered = marketRates.value

      if (filters.value.city) {
        filtered = filtered.filter(rate => rate.city_name === filters.value.city)
      }

      if (filters.value.worker) {
        filtered = filtered.filter(rate => rate.added_by === parseInt(filters.value.worker))
      }

      if (filters.value.dateFrom) {
        filtered = filtered.filter(rate => new Date(rate.date) >= new Date(filters.value.dateFrom))
      }

      if (filters.value.dateTo) {
        const dateTo = new Date(filters.value.dateTo)
        dateTo.setHours(23, 59, 59, 999)
        filtered = filtered.filter(rate => new Date(rate.date) <= dateTo)
      }

      return filtered
    })

    const todayRatesCount = computed(() => {
      const today = new Date().toDateString()
      return marketRates.value.filter(rate =>
        new Date(rate.created_at).toDateString() === today
      ).length
    })

    const uniqueCitiesCount = computed(() => {
      const uniqueCities = new Set(marketRates.value.map(rate => rate.city_name))
      return uniqueCities.size
    })

    // Методы
    const loadCities = async () => {
      try {
        const response = await adminAPI.getCities()
        cities.value = response.data?.cities || []
      } catch (error) {
        console.error('Load cities error:', error)
        showError('Ошибка при загрузке городов')
      }
    }

    const loadWorkers = async () => {
      try {
        const response = await adminAPI.getWorkers()
        workers.value = response.data || []
      } catch (error) {
        console.error('Load workers error:', error)
        showError('Ошибка при загрузке работников')
      }
    }

    const applyFilters = () => {
      console.log('🔍 Применение фильтров:', filters.value)
    }

    const resetFilters = () => {
      filters.value = {
        city: '',
        worker: '',
        dateFrom: '',
        dateTo: ''
      }
      console.log('🔄 Фильтры сброшены')
    }

    const handleRefreshRates = async () => {
      try {
        await loadMarketRates()
        showSuccess('Данные обновлены')
      } catch (error) {
        showError('Ошибка при обновлении данных')
      }
    }

    const handleEditRate = (rate) => {
      console.log('✏️ Редактирование курса:', rate)
      // Сохраняем оригинальные данные курса
      selectedRate.value = {
        id: rate.id,
        currency: rate.currency, // ID валюты для API
        currency_code: rate.currency_code, // Код валюты для отображения
        buy: rate.buy,
        sell: rate.sell,
        is_active: rate.is_active,
        notes: rate.notes || '',
        // Добавляем все остальные поля, которые могут понадобиться
        city_name: rate.city_name,
        worker_id: rate.worker_id,
        created_at: rate.created_at
      }
      showModal.value = true
    }

    const handleDeleteRate = async (rateId) => {
      if (confirm('Вы уверены, что хотите удалить этот курс?')) {
        try {
          await deleteMarketRate(rateId)
          showSuccess('Курс успешно удален')
          await loadMarketRates()
        } catch (error) {
          showError('Ошибка при удалении курса')
          console.error('Delete rate error:', error)
        }
      }
    }

    const handleSaveRate = async (rateData) => {
      try {
        modalLoading.value = true
        console.log('💾 Обновление курса:', rateData)
        console.log('📋 Выбранный курс:', selectedRate.value)

        // Получаем ID из selectedRate или rateData
        const rateId = rateData.id

        if (!rateId) {
         throw new Error('ID курса не найден')
        }

        // Преобразуем данные для API
        const apiData = {
          currency: rateData.currency, // ID валюты (число)
          buy: parseFloat(rateData.buy), // Убеждаемся, что это число
          sell: parseFloat(rateData.sell), // Убеждаемся, что это число
          is_active: rateData.is_active,
          notes: rateData.notes || ''
        }
        console.log('📤 Отправляем данные в API:', apiData)
        console.log('🔗 URL:', `/admin/market-exchange-rates/${rateId}/`)

        await updateMarketRate(rateData.id, apiData)
        showSuccess('Курс обновлен')
        closeModal()
        await loadMarketRates()
      } catch (error) {
        showError('Ошибка при сохранении')
        console.error('Save rate error:', error)
      } finally {
        modalLoading.value = false
      }
    }

    const closeModal = () => {
      console.log('❌ Закрытие модального окна')
      showModal.value = false
      selectedRate.value = null
    }

    // Инициализация
    onMounted(async () => {
      try {
        await Promise.all([
          loadMarketRates(),
          loadCities(),
          loadWorkers()
        ])
      } catch (error) {
        console.error('Initialization error:', error)
        showError('Ошибка при загрузке данных')
      }
    })

    return {
      // Состояние
      showDebug,
      showModal,
      selectedRate,
      modalLoading,
      ratesLoading,
      filters,
      cities,
      workers,
      debugInfo,

      // Данные
      marketRates,

      // Вычисляемые свойства
      filteredMarketRates,
      todayRatesCount,
      uniqueCitiesCount,

      // Методы
      applyFilters,
      resetFilters,
      handleRefreshRates,
      handleEditRate,
      handleDeleteRate,
      handleSaveRate,
      closeModal
    }
  }
}
</script>