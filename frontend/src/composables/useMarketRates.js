// frontend/src/composables/useMarketRates.js
import { ref, computed } from 'vue'
import { adminAPI } from '@/services/admin.js'
import { workerAPI } from '@/services/worker.js'

const marketRates = ref([])
const loading = ref(false)
const error = ref(null)

// Инициализация с пустым массивом для предотвращения ошибок
const initializeMarketRates = () => {
  if (!Array.isArray(marketRates.value)) {
    marketRates.value = []
  }
}

export function useMarketRates() {
  // Загрузка рыночных курсов с улучшенной обработкой ошибок
  const loadMarketRates = async (params = {}) => {
    loading.value = true
    error.value = null

    // Обеспечиваем, что marketRates всегда массив
    initializeMarketRates()

    try {
      console.log('📊 Загрузка рыночных курсов...')

      // Добавляем контроллер для отмены запроса
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 15000) // 15 секунд

      try {
        // Используем правильный API endpoint с увеличенным таймаутом
        const response = await adminAPI.getMarketRates({
          ...params,
          signal: controller.signal
        })

        clearTimeout(timeoutId)

        // Проверяем, что ответ содержит массив данных
        const data = response.data
        if (Array.isArray(data)) {
          marketRates.value = data
        } else if (data && Array.isArray(data.results)) {
          // Если данные приходят в формате пагинации
          marketRates.value = data.results
        } else {
          console.warn('Получены данные не в виде массива:', data)
          marketRates.value = []
        }

        console.log('✅ Рыночные курсы загружены:', marketRates.value.length)

      } catch (apiError) {
        clearTimeout(timeoutId)
        throw apiError
      }

    } catch (err) {
      console.error('❌ Ошибка загрузки рыночных курсов:', err)

      // Определяем тип ошибки
      let errorMessage = 'Ошибка загрузки данных'

      if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
        errorMessage = 'Превышено время ожидания ответа от сервера'
      } else if (err.code === 'ERR_NETWORK') {
        errorMessage = 'Ошибка сети. Проверьте подключение к интернету'
      } else if (err.response?.status === 404) {
        errorMessage = 'API endpoint не найден'
      } else if (err.response?.status === 500) {
        errorMessage = 'Внутренняя ошибка сервера'
      } else if (err.response?.status === 403) {
        errorMessage = 'Недостаточно прав доступа'
      }

      error.value = errorMessage

      // УБИРАЕМ ТЕСТОВЫЕ ДАННЫЕ - оставляем пустой массив
      marketRates.value = []
      console.log('❌ Данные не загружены, показываем пустой список')

    } finally {
      loading.value = false
    }
  }

  // Загрузка курсов для работников (только их город)
  const loadWorkerMarketRates = async (params = {}) => {
    loading.value = true
    error.value = null

    // Обеспечиваем, что marketRates всегда массив
    initializeMarketRates()

    try {
      console.log('📊 Загрузка курсов для работника...')

      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 15000)

      try {
        const response = await workerAPI.getMarketRates({
          ...params,
          signal: controller.signal
        })

        clearTimeout(timeoutId)

        // Проверяем, что ответ содержит массив данных
        const data = response.data
        if (Array.isArray(data)) {
          marketRates.value = data
        } else if (data && Array.isArray(data.results)) {
          marketRates.value = data.results
        } else {
          console.warn('Получены данные не в виде массива:', data)
          marketRates.value = []
        }

        console.log('✅ Курсы работника загружены:', marketRates.value.length)

      } catch (apiError) {
        clearTimeout(timeoutId)
        throw apiError
      }

    } catch (err) {
      console.error('❌ Ошибка загрузки курсов работника:', err)

      let errorMessage = 'Ошибка загрузки данных'
      if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
        errorMessage = 'Превышено время ожидания ответа от сервера'
      }

      error.value = errorMessage

      // УБИРАЕМ ТЕСТОВЫЕ ДАННЫЕ - оставляем пустой массив
      marketRates.value = []
      console.log('❌ Данные не загружены, показываем пустой список')

    } finally {
      loading.value = false
    }
  }

  // Создание нового курса с повторными попытками
  const createMarketRate = async (rateData, retries = 3) => {
    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        console.log(`📝 Создание нового курса (попытка ${attempt}):`, rateData)

        const response = await adminAPI.createMarketRate(rateData)

        // Обеспечиваем, что marketRates всегда массив
        initializeMarketRates()

        // Добавляем в локальный массив
        marketRates.value.unshift(response.data)

        console.log('✅ Курс создан успешно')
        return response.data

      } catch (err) {
        console.error(`❌ Ошибка создания курса (попытка ${attempt}):`, err)

        if (attempt === retries) {
          throw err
        }

        // Задержка перед повторной попыткой
        await new Promise(resolve => setTimeout(resolve, 1000 * attempt))
      }
    }
  }

  // Создание курса работником с повторными попытками
  const createWorkerMarketRate = async (rateData, retries = 3) => {
    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        console.log(`📝 Создание курса работником (попытка ${attempt}):`, rateData)

        const response = await workerAPI.createMarketRate(rateData)

        // Обеспечиваем, что marketRates всегда массив
        initializeMarketRates()

        // Добавляем в локальный массив
        marketRates.value.unshift(response.data)

        console.log('✅ Курс создан работником успешно')
        return response.data

      } catch (err) {
        console.error(`❌ Ошибка создания курса работником (попытка ${attempt}):`, err)

        if (attempt === retries) {
          throw err
        }

        // Задержка перед повторной попыткой
        await new Promise(resolve => setTimeout(resolve, 1000 * attempt))
      }
    }
  }

  // Обновление курса
  const updateMarketRate = async (rateId, rateData) => {
  try {
    console.log('🔧 updateMarketRate вызван с параметрами:')
    console.log('ID:', rateId)
    console.log('Data:', rateData)
    console.log('URL:', `/admin/market-exchange-rates/${rateId}/`)

    // Проверяем, что ID передан и это число
    if (!rateId || isNaN(rateId)) {
      throw new Error('ID курса не предоставлен или неверный формат')
    }

    // Валидируем данные перед отправкой
    if (!rateData.currency || typeof rateData.currency !== 'number') {
      throw new Error('ID валюты должен быть числом')
    }

    if (!rateData.buy || !rateData.sell) {
      throw new Error('Курсы покупки и продажи обязательны')
    }

    // Подготавливаем данные для API
    const apiPayload = {
      currency: parseInt(rateData.currency), // Убеждаемся, что это число
      buy: parseFloat(rateData.buy),
      sell: parseFloat(rateData.sell),
      is_active: Boolean(rateData.is_active),
      notes: rateData.notes || ''
    }

    console.log('📤 Отправляем в API:', apiPayload)

    // Отправляем запрос
    const response = await adminAPI.updateMarketRate(rateId, apiPayload)

    console.log('✅ Ответ от API:', response.data)

    // Обеспечиваем, что marketRates всегда массив
    initializeMarketRates()

    // Обновляем в локальном массиве
    const index = marketRates.value.findIndex(rate => rate.id === parseInt(rateId))
    if (index !== -1) {
      marketRates.value[index] = response.data
      console.log('🔄 Локальные данные обновлены')
    }

    return response.data

  } catch (err) {
    console.error('❌ Ошибка обновления курса:', err)

    // Логируем детали ошибки
    if (err.response) {
      console.error('📋 Статус ответа:', err.response.status)
      console.error('📋 Данные ответа:', err.response.data)
      console.error('📋 Заголовки ответа:', err.response.headers)
    }

    throw err
  }
}

  // Удаление курса
  const deleteMarketRate = async (rateId) => {
    try {
      console.log('🗑️ Удаление курса:', rateId)

      await adminAPI.deleteMarketRate(rateId)

      // Обеспечиваем, что marketRates всегда массив
      initializeMarketRates()

      // Удаляем из локального массива
      marketRates.value = marketRates.value.filter(rate => rate.id !== rateId)

      console.log('✅ Курс удален успешно')

    } catch (err) {
      console.error('❌ Ошибка удаления курса:', err)
      throw err
    }
  }

  // Получение курса по ID
  const getMarketRateById = (rateId) => {
    initializeMarketRates()
    return marketRates.value.find(rate => rate.id === rateId)
  }

  // Фильтрация курсов по городу
  const getMarketRatesByCity = (cityName) => {
    initializeMarketRates()
    return marketRates.value.filter(rate => rate.city_name === cityName)
  }

  // Получение курсов за определенный период
  const getMarketRatesByDateRange = (startDate, endDate) => {
    initializeMarketRates()
    const start = new Date(startDate)
    const end = new Date(endDate)
    end.setHours(23, 59, 59, 999)

    return marketRates.value.filter(rate => {
      const rateDate = new Date(rate.date || rate.created_at)
      return rateDate >= start && rateDate <= end
    })
  }

  // Повторная попытка загрузки с экспоненциальной задержкой
  const retryLoadMarketRates = async (params = {}, maxRetries = 3) => {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        await loadMarketRates(params)
        return // Успешно загружено
      } catch (err) {
        console.warn(`Попытка ${attempt} не удалась, повторяем...`)

        if (attempt === maxRetries) {
          throw err
        }

        // Экспоненциальная задержка: 2^attempt секунд
        const delay = Math.pow(2, attempt) * 1000
        await new Promise(resolve => setTimeout(resolve, delay))
      }
    }
  }

  // Проверка состояния соединения
  const checkConnection = async () => {
    try {
      const response = await fetch('/api/health', {
        method: 'GET',
        timeout: 5000
      })
      return response.ok
    } catch {
      return false
    }
  }

  // Вычисляемые свойства с защитой от ошибок
  const totalRates = computed(() => {
    return Array.isArray(marketRates.value) ? marketRates.value.length : 0
  })

  const todayRates = computed(() => {
    if (!Array.isArray(marketRates.value)) return []

    const today = new Date().toDateString()
    return marketRates.value.filter(rate => {
      const rateDate = new Date(rate.date || rate.created_at)
      return rateDate.toDateString() === today
    })
  })

  const uniqueCities = computed(() => {
    if (!Array.isArray(marketRates.value)) return []

    const cities = new Set(marketRates.value.map(rate => rate.city_name))
    return Array.from(cities).filter(Boolean)
  })

  const ratesByCity = computed(() => {
    if (!Array.isArray(marketRates.value)) return {}

    const grouped = {}
    marketRates.value.forEach(rate => {
      if (!grouped[rate.city_name]) {
        grouped[rate.city_name] = []
      }
      grouped[rate.city_name].push(rate)
    })
    return grouped
  })

  // Курсы введенные только работниками
  const workerMarketRates = computed(() => {
    if (!Array.isArray(marketRates.value)) return []

    return marketRates.value.filter(rate =>
      rate.added_by && rate.added_by.role === 'city_worker'
    )
  })

  // Флаг для определения, что данные не загружены
  const isDataEmpty = computed(() => {
    return !loading.value && Array.isArray(marketRates.value) && marketRates.value.length === 0
  })

  return {
    // Состояние
    marketRates,
    loading,
    error,
    isDataEmpty,

    // Методы
    loadMarketRates,
    loadWorkerMarketRates,
    createMarketRate,
    createWorkerMarketRate,
    updateMarketRate,
    deleteMarketRate,
    getMarketRateById,
    getMarketRatesByCity,
    getMarketRatesByDateRange,
    retryLoadMarketRates,
    checkConnection,
    initializeMarketRates,

    // Вычисляемые свойства
    totalRates,
    todayRates,
    uniqueCities,
    ratesByCity,
    workerMarketRates
  }
}