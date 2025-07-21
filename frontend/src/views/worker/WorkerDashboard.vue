<template>
  <div class="worker-dashboard">
    <div class="dashboard-container">
      <!-- Основной контент -->
      <div class="main-content">
        <!-- Форма добавления курса -->
        <div class="add-rate-card">
          <h2 class="card-title">Добавить курс валют</h2>
          <form @submit.prevent="addRate" class="rate-form">
            <div class="form-row">
              <div class="form-group">
                <label for="currency" class="form-label">Выберите валюту</label>
                <select
                  id="currency"
                  v-model="rateForm.currency"
                  required
                  class="form-select"
                  :disabled="currenciesLoading"
                >
                  <option value="">{{ currenciesLoading ? 'Загрузка...' : 'Выберите валюту' }}</option>
                  <option
                    v-for="currency in currencies"
                    :key="currency.id"
                    :value="currency.id"
                  >
                    {{ currency.code }} - {{ currency.name }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label for="buy_rate" class="form-label">Курс покупки</label>
                <input
                  id="buy_rate"
                  type="number"
                  step="0.0001"
                  v-model="rateForm.buy"
                  required
                  class="form-input"
                  placeholder="0.00"
                />
              </div>

              <div class="form-group">
                <label for="sell_rate" class="form-label">Курс продажи</label>
                <input
                  id="sell_rate"
                  type="number"
                  step="0.0001"
                  v-model="rateForm.sell"
                  required
                  class="form-input"
                  placeholder="0.00"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="notes" class="form-label">Примечание (опционально)</label>
                <textarea
                  id="notes"
                  v-model="rateForm.notes"
                  class="form-textarea"
                  placeholder="Дополнительная информация..."
                  rows="3"
                ></textarea>
              </div>
            </div>

            <div class="form-actions">
              <button
                type="submit"
                class="btn btn-primary"
                :disabled="isSubmitting"
              >
                <span v-if="isSubmitting">
                  {{ editingRate ? 'Обновление...' : 'Добавление...' }}
                </span>
                <span v-else-if="editingRate">
                  Обновить курс
                </span>
                <span v-else>
                  Добавить курс
                </span>
              </button>
              <button
                v-if="editingRate"
                type="button"
                class="btn btn-secondary"
                @click="cancelEdit"
              >
                Отменить
              </button>
            </div>
          </form>
        </div>

        <!-- Последние курсы -->
        <div class="rates-card">
          <div class="rates-header">
            <h2 class="card-title">Последние курсы</h2>
            <button @click="loadRecentRates" class="btn btn-secondary">
              Обновить
            </button>
          </div>

          <div v-if="loading" class="loading-state">
            <div class="loading-spinner"></div>
            <p class="loading-text">Загрузка...</p>
          </div>

          <div v-else-if="recentRates.length > 0" class="rates-list">
            <div
              v-for="(rate, index) in recentRates.slice(0, 5)"
              :key="rate.id"
              class="rate-item"
              :class="{ 'editing': editingRate && editingRate.id === rate.id }"
              :style="{ 'animation-delay': `${index * 0.1}s` }"
              :data-rate-id="rate.id"
            >
              <div class="rate-info">
                <div class="currency-icon">
                  <span class="currency-code">{{ rate.currency_code }}</span>
                  <div class="currency-status"></div>
                </div>
                <div class="rate-details">
                  <p class="currency-name">{{ rate.currency_name }}</p>
                  <p class="rate-time">
                    <span class="time-indicator"></span>
                    {{ formatDateTime(rate.date, rate.time) }}
                  </p>
                </div>
              </div>
              <div class="rate-values">
                <p class="rate-buy">Покупка: {{ rate.buy }}</p>
                <p class="rate-sell">Продажа: {{ rate.sell }}</p>
              </div>
              <div v-if="rate.notes" class="rate-notes">
                <p>{{ rate.notes }}</p>
              </div>
              <div class="rate-actions">
                <button
                  @click="editRate(rate)"
                  class="btn-icon btn-edit"
                  title="Редактировать"
                  :disabled="isSubmitting"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708L8.207 11.5 5.5 12.5l1-2.707L13.146.146zM11.207 2.5 13.5 4.793 12.793 5.5 10.5 3.207 11.207 2.5zM10.5 3.207 12.793 5.5l-6.646 6.647-.793-.793L12 4.707 10.5 3.207z"/>
                  </svg>
                </button>
                <button
                  @click="deleteRate(rate)"
                  class="btn-icon btn-delete"
                  title="Удалить"
                  :disabled="isSubmitting"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                    <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <div v-else class="empty-state">
            <div class="empty-icon">📊</div>
            <p class="empty-title">Пока нет добавленных курсов</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import '@/assets/styles/views/worker/WorkerDashboard.css'
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { workerAPI } from '../../services/api.js'

const authStore = useAuthStore()

const recentRates = ref([])
const loading = ref(true)
const editingRate = ref(null)

// Данные для формы
const currencies = ref([])
const currenciesLoading = ref(true)
const isSubmitting = ref(false)

const rateForm = ref({
  currency: '',
  buy: '',
  sell: '',
  notes: ''
})

onMounted(async () => {
  await Promise.all([
    loadRecentRates(),
    loadCurrencies()
  ])
})

const loadCurrencies = async () => {
  try {
    currenciesLoading.value = true
    const response = await workerAPI.getCurrencies()
    currencies.value = response.data || []
  } catch (error) {
    console.error('Ошибка загрузки валют:', error)
  } finally {
    currenciesLoading.value = false
  }
}

const addRate = async () => {
  console.log('🔄 [DEBUG] Начало функции addRate, время:', new Date().toISOString())

  try {
    isSubmitting.value = true
    console.log('🔄 [DEBUG] isSubmitting установлен в true')

    // Базовая валидация на фронтенде
    if (!rateForm.value.currency) {
      console.log('❌ [DEBUG] Валюта не выбрана')
      alert('Выберите валюту')
      return
    }

    const buyRate = parseFloat(rateForm.value.buy)
    const sellRate = parseFloat(rateForm.value.sell)

    console.log('🔄 [DEBUG] Валидация курсов:', { buyRate, sellRate })

    if (isNaN(buyRate) || buyRate <= 0) {
      console.log('❌ [DEBUG] Неверный курс покупки:', buyRate)
      alert('Курс покупки должен быть положительным числом')
      return
    }

    if (isNaN(sellRate) || sellRate <= 0) {
      console.log('❌ [DEBUG] Неверный курс продажи:', sellRate)
      alert('Курс продажи должен быть положительным числом')
      return
    }

    // Получаем текущую дату и время в разных форматах
    const now = new Date()
    const currentDate = now.toISOString().split('T')[0] // YYYY-MM-DD формат
    const currentTime = now.toTimeString().split(' ')[0] // HH:MM:SS формат
    const isoDateTime = now.toISOString() // Полный ISO формат
    const timestamp = Math.floor(now.getTime() / 1000) // Unix timestamp

    console.log('🕐 [DEBUG] Различные форматы времени:', {
      currentDate,
      currentTime,
      isoDateTime,
      timestamp
    })

    // Правильные названия полей согласно сериализатору
    const rateData = {
      currency: rateForm.value.currency,
      buy: buyRate,
      sell: sellRate,
      notes: rateForm.value.notes || '',
      // Пробуем разные варианты полей времени
      date: currentDate,
      time: currentTime,
      // Альтернативные варианты названий полей
      created_at: isoDateTime,
      updated_at: isoDateTime,
      timestamp: timestamp,
      datetime: `${currentDate} ${currentTime}`
    }

    console.log('📤 [DEBUG] Отправляемые данные:', rateData)
    console.log('📤 [DEBUG] Режим редактирования:', !!editingRate.value)

    if (editingRate.value) {
      console.log('✏️ [DEBUG] Обновление существующего курса ID:', editingRate.value.id)
      await workerAPI.updateRate(editingRate.value.id, rateData)
      console.log('✅ [DEBUG] Курс успешно обновлен с новым временем')
      alert('Курс успешно обновлен!')
      editingRate.value = null
    } else {
      console.log('➕ [DEBUG] Создание нового курса')
      const result = await workerAPI.createRate(rateData)
      console.log('✅ [DEBUG] Курс успешно создан, результат:', result)
      alert('Курс успешно добавлен!')
    }

    // Сбрасываем форму
    rateForm.value = {
      currency: '',
      buy: '',
      sell: '',
      notes: ''
    }
    console.log('🔄 [DEBUG] Форма сброшена')

    // Обновляем список курсов
    console.log('🔄 [DEBUG] Обновление списка курсов')
    await loadRecentRates()
    console.log('✅ [DEBUG] Список курсов обновлен')

  } catch (error) {
    console.log('🚨 [ERROR] Перехвачена ошибка:', error)
    console.log('🚨 [ERROR] Время ошибки:', new Date().toISOString())

    // Детальное логирование ошибки
    console.group('🔍 ДЕТАЛЬНАЯ ИНФОРМАЦИЯ ОБ ОШИБКЕ')
    console.log('Тип ошибки:', error.constructor.name)
    console.log('Сообщение:', error.message)
    console.log('Полный объект ошибки:', error)

    if (error.response) {
      console.log('📨 ОТВЕТ СЕРВЕРА:')
      console.log('  Статус:', error.response.status)
      console.log('  Статус текст:', error.response.statusText)
      console.log('  Заголовки:', error.response.headers)
      console.log('  Данные:', error.response.data)
      console.log('  Тип данных:', typeof error.response.data)

      if (error.response.data) {
        console.log('  Данные как строка:', String(error.response.data))
        console.log('  Данные как JSON:', JSON.stringify(error.response.data, null, 2))
      }
    }

    if (error.request) {
      console.log('📡 ЗАПРОС:', error.request)
    }

    console.log('⚙️ КОНФИГУРАЦИЯ ЗАПРОСА:', error.config)
    console.groupEnd()

    // Упрощенная обработка ошибок
    if (error.response) {
      const status = error.response.status
      const errorData = error.response.data

      console.log('🔄 [DEBUG] Обработка ошибки со статусом:', status)

      if (status === 500) {
        console.log('🚨 [ERROR] Ошибка сервера 500')
        alert('Ошибка сервера: ' + errorData)
      } else if (status === 400) {
        console.log('🚨 [ERROR] Ошибка валидации 400')
        // Ошибка валидации
        let errorMessage = 'Ошибка валидации:\n'

        if (typeof errorData === 'object' && errorData !== null) {
          Object.entries(errorData).forEach(([field, messages]) => {
            if (Array.isArray(messages)) {
              errorMessage += `${field}: ${messages.join(', ')}\n`
            } else {
              errorMessage += `${field}: ${messages}\n`
            }
          })
        } else {
          errorMessage += errorData
        }

        alert(errorMessage)
      } else {
        console.log('🚨 [ERROR] Другая ошибка HTTP:', status)
        alert(`Ошибка ${status}: ${JSON.stringify(errorData)}`)
      }
    } else if (error.request) {
      console.log('🚨 [ERROR] Ошибка сети')
      alert('Не удалось связаться с сервером. Проверьте подключение.')
    } else {
      console.log('🚨 [ERROR] Неизвестная ошибка')
      alert('Произошла неизвестная ошибка: ' + error.message)
    }
  } finally {
    console.log('🏁 [DEBUG] Завершение функции addRate')
    isSubmitting.value = false
  }
}

const editRate = (rate) => {
  console.log('✏️ [DEBUG] Начало редактирования курса:', rate)

  editingRate.value = rate
  rateForm.value = {
    currency: rate.currency_id || rate.currency,
    buy: rate.buy,
    sell: rate.sell,
    notes: rate.notes || ''
  }

  console.log('✏️ [DEBUG] Форма заполнена данными:', rateForm.value)

  // Прокручиваем к форме
  const formElement = document.querySelector('.add-rate-card')
  if (formElement) {
    formElement.scrollIntoView({ behavior: 'smooth' })
  }

  // Визуально выделяем редактируемую строку
  const rateElements = document.querySelectorAll('.rate-item')
  rateElements.forEach(el => el.classList.remove('editing'))

  // Находим и выделяем редактируемую строку
  setTimeout(() => {
    const editingElement = document.querySelector(`[data-rate-id="${rate.id}"]`)
    if (editingElement) {
      editingElement.classList.add('editing')
      console.log('✏️ [DEBUG] Строка выделена для редактирования')
    }
  }, 100)
}

const cancelEdit = () => {
  console.log('❌ [DEBUG] Отмена редактирования')

  editingRate.value = null
  rateForm.value = {
    currency: '',
    buy: '',
    sell: '',
    notes: ''
  }

  // Убираем выделение со всех строк
  const rateElements = document.querySelectorAll('.rate-item')
  rateElements.forEach(el => el.classList.remove('editing'))
}

const deleteRate = async (rate) => {
  if (!confirm(`Вы уверены, что хотите удалить курс ${rate.currency_code}?`)) {
    return
  }

  try {
    isSubmitting.value = true
    console.log('🗑️ [DEBUG] Удаление курса ID:', rate.id)

    await workerAPI.deleteRate(rate.id)

    console.log('✅ [DEBUG] Курс успешно удален')
    alert('Курс успешно удален!')

    await loadRecentRates()
  } catch (error) {
    console.error('❌ [ERROR] Ошибка удаления курса:', error)
    alert('Произошла ошибка при удалении курса')
  } finally {
    isSubmitting.value = false
  }
}

const loadRecentRates = async () => {
  try {
    loading.value = true
    console.log('🔄 [DEBUG] Загрузка последних курсов')

    const ratesResponse = await workerAPI.getRates()
    const ratesData = ratesResponse.data || {}

    // Получаем все курсы
    const allRates = ratesData.results || ratesData || []

    console.log('✅ [DEBUG] Получено курсов:', allRates.length)

    // Сохраняем курсы для отображения
    recentRates.value = allRates.slice(0, 10)

  } catch (error) {
    console.error('❌ [ERROR] Ошибка загрузки курсов:', error)
  } finally {
    loading.value = false
  }
}

const formatDateTime = (dateString, timeString) => {
  if (!dateString || !timeString) return ''

  try {
    const date = new Date(`${dateString}T${timeString}`)

    return date.toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    console.error('❌ [ERROR] Ошибка форматирования даты:', error)
    return `${dateString} ${timeString}`
  }
}

// Утилитарная функция для получения текущего времени в нужном формате
const getCurrentDateTime = () => {
  const now = new Date()

  // Получаем компоненты даты и времени
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')

  return {
    date: `${year}-${month}-${day}`,
    time: `${hours}:${minutes}:${seconds}`,
    datetime: `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
  }
}
</script>