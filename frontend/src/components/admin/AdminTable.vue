<template>
  <div class="p-4">
    <h3 class="text-lg font-semibold mb-4 text-gray-700">Рыночные курсы валют</h3>

    <div v-if="loading" class="text-center py-4">
      <p class="text-gray-500">Загрузка...</p>
    </div>

    <div v-else-if="error" class="text-center py-4">
      <p class="text-red-600">{{ error }}</p>
      <button
        @click="fetchRates"
        class="mt-2 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        Повторить
      </button>
    </div>

    <div v-else-if="rates.length === 0" class="text-center py-4">
      <p class="text-gray-500">Нет данных о курсах</p>
    </div>

    <div v-else class="overflow-x-auto">
      <table class="w-full border-collapse border border-gray-300">
        <thead>
          <tr class="bg-gray-100">
            <th class="border border-gray-300 px-4 py-2 text-left">Валюта</th>
            <th class="border border-gray-300 px-4 py-2 text-left">Курс покупки</th>
            <th class="border border-gray-300 px-4 py-2 text-left">Курс продажи</th>
            <th class="border border-gray-300 px-4 py-2 text-left">Дата</th>
            <th class="border border-gray-300 px-4 py-2 text-left">Время</th>
            <th class="border border-gray-300 px-4 py-2 text-left">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="rate in rates" :key="rate.id" class="hover:bg-gray-50">
            <td class="border border-gray-300 px-4 py-2 font-semibold">
              {{ rate.currency }}
            </td>
            <td class="border border-gray-300 px-4 py-2">
              {{ formatRate(rate.buy) }}
            </td>
            <td class="border border-gray-300 px-4 py-2">
              {{ formatRate(rate.sell) }}
            </td>
            <td class="border border-gray-300 px-4 py-2">
              {{ formatDate(rate.date) }}
            </td>
            <td class="border border-gray-300 px-4 py-2">
              {{ formatTime(rate.time) }}
            </td>
            <td class="border border-gray-300 px-4 py-2">
              <button
                @click="deleteRate(rate.id)"
                class="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
                :disabled="deleting"
              >
                {{ deleting === rate.id ? 'Удаление...' : 'Удалить' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="mt-4 text-right">
      <button
        @click="fetchRates"
        class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
        :disabled="loading"
      >
        Обновить данные
      </button>
    </div>
  </div>
</template>

<script setup>
import '@/assets/styles/components/admin/AdminTable.css'
import { ref, onMounted } from 'vue'
import api from '../../services/api.js'

const rates = ref([])
const loading = ref(false)
const error = ref('')
const deleting = ref(null)

onMounted(() => {
  fetchRates()
})

const fetchRates = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await api.get('/market-exchange-rates/')
    console.log('[DEBUG] Received rates data:', response.data) // Добавляем отладку

    // Если ответ массив
    if (Array.isArray(response.data)) {
      rates.value = response.data
    }
    // Если ответ объект с полем results (DRF pagination)
    else if (response.data.results) {
      rates.value = response.data.results
    }
    // Иначе пустой массив
    else {
      rates.value = []
    }

  } catch (err) {
    console.error('Ошибка загрузки курсов:', err)
    error.value = 'Не удалось загрузить курсы валют'
    rates.value = []
  } finally {
    loading.value = false
  }
}

const deleteRate = async (rateId) => {
  if (!confirm('Вы уверены, что хотите удалить этот курс?')) {
    return
  }

  deleting.value = rateId

  try {
    await api.delete(`/market-exchange-rates/${rateId}/`)

    // Удаляем из локального массива
    rates.value = rates.value.filter(rate => rate.id !== rateId)

  } catch (err) {
    console.error('Ошибка удаления курса:', err)
    alert('Не удалось удалить курс')
  } finally {
    deleting.value = null
  }
}

const formatRate = (rate) => {
  return parseFloat(rate).toFixed(4)
}

// Улучшенная функция форматирования даты
const formatDate = (dateString) => {
  console.log('[DEBUG] Formatting date:', dateString) // Отладочная информация

  if (!dateString) {
    return 'Не указана'
  }

  try {
    // Проверяем, является ли dateString уже в формате ISO (YYYY-MM-DD)
    let date

    if (dateString.includes('-')) {
      // Формат ISO: 2025-06-14
      date = new Date(dateString)
    } else if (dateString.includes('.')) {
      // Европейский формат: 14.06.2025
      const [day, month, year] = dateString.split('.')
      date = new Date(year, month - 1, day) // month - 1 потому что месяцы в JS начинаются с 0
    } else {
      // Пытаемся создать дату как есть
      date = new Date(dateString)
    }

    // Проверяем, что дата валидна
    if (isNaN(date.getTime())) {
      console.error('[DEBUG] Invalid date created from:', dateString)
      return 'Неверная дата'
    }

    // Возвращаем дату в желаемом формате
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    })

  } catch (error) {
    console.error('[DEBUG] Error formatting date:', error, 'Input:', dateString)
    return 'Ошибка даты'
  }
}

// Отдельная функция для форматирования времени
const formatTime = (timeString) => {
  console.log('[DEBUG] Formatting time:', timeString) // Отладочная информация

  if (!timeString) {
    return 'Не указано'
  }

  try {
    // Время уже должно приходить в формате HH:MM
    if (typeof timeString === 'string' && timeString.includes(':')) {
      return timeString
    }

    // Если время пришло в другом формате, пытаемся его обработать
    const date = new Date(`2000-01-01T${timeString}`)
    if (!isNaN(date.getTime())) {
      return date.toLocaleTimeString('ru-RU', {
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    return timeString.toString()

  } catch (error) {
    console.error('[DEBUG] Error formatting time:', error, 'Input:', timeString)
    return 'Ошибка времени'
  }
}

// Методы для внешнего вызова
const refreshRates = () => {
  fetchRates()
}

// Экспортируем методы для родительского компонента
defineExpose({
  refreshRates
})
</script>