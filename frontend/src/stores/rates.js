// frontend/src/stores/rates.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/services/client.js'
import { adminAPI } from '@/services/admin.js'

export const useRatesStore = defineStore('rates', () => {
  const bankRates = ref([])
  const marketRates = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Банковские курсы (через админ API)
  const fetchBankRates = async () => {
    loading.value = true
    error.value = null

    try {
      console.log('[DEBUG Store] Fetching bank rates...')

      const response = await adminAPI.getBankRates()

      console.log('[DEBUG Store] Bank rates response:', response.data)

      if (Array.isArray(response.data)) {
        bankRates.value = response.data
        console.log('[DEBUG Store] Bank rates set:', bankRates.value)
      } else {
        console.warn('[DEBUG Store] Unexpected bank rates format:', response.data)
        bankRates.value = []
      }

    } catch (err) {
      error.value = 'Ошибка загрузки курсов банков'
      console.error('[DEBUG Store] Fetch bank rates error:', err)

      if (err.response) {
        console.error('[DEBUG Store] Error response:', err.response.status, err.response.data)
      }
    } finally {
      loading.value = false
    }
  }

  const updateBankRate = async (id, rateData) => {
    try {
      const response = await apiClient.patch(`/public/bank-rates/${id}/`, rateData)

      // Обновляем локальный стейт
      const index = bankRates.value.findIndex(rate => rate.id === id)
      if (index !== -1) {
        bankRates.value[index] = response.data
      } else {
        bankRates.value.push(response.data)
      }

      return { success: true, data: response.data }
    } catch (err) {
      console.error('Update bank rate error:', err)
      return {
        success: false,
        error: err.response?.data?.detail || 'Ошибка обновления курса'
      }
    }
  }

  // Рыночные курсы (публичный API)
  const fetchMarketRates = async () => {
    loading.value = true
    error.value = null

    try {
      console.log('[DEBUG Store] Fetching market rates...')

      // Используем публичный эндпоинт для рыночных курсов
      const response = await apiClient.get('/public/rates/')

      console.log('[DEBUG Store] Market rates response:', response.data)

      if (Array.isArray(response.data)) {
        marketRates.value = response.data
      } else {
        console.warn('[DEBUG Store] Unexpected market rates format:', response.data)
        marketRates.value = []
      }

    } catch (err) {
      error.value = 'Ошибка загрузки рыночных курсов'
      console.error('[DEBUG Store] Fetch market rates error:', err)
    } finally {
      loading.value = false
    }
  }

  const deleteMarketRate = async (id) => {
    try {
      await apiClient.delete(`/public/rates/${id}/`)
      marketRates.value = marketRates.value.filter(rate => rate.id !== id)
      return { success: true }
    } catch (err) {
      console.error('Delete market rate error:', err)
      return {
        success: false,
        error: err.response?.data?.detail || 'Ошибка удаления курса'
      }
    }
  }

  // Computed свойства для группировки банковских курсов
  const groupedBankRates = computed(() => {
    console.log('[DEBUG Store] Computing grouped bank rates:', bankRates.value)
    
    const grouped = {}
    bankRates.value.forEach(rate => {
      const bankName = rate.bank_name || rate.bank?.name || 'Неизвестный банк'
      
      if (!grouped[bankName]) {
        grouped[bankName] = {
          id: rate.bank?.id || bankName,
          name: bankName,
          bank_image: rate.bank_image || rate.bank?.image,
          rates: []
        }
      }
      grouped[bankName].rates.push({
        id: rate.id,
        currency: rate.currency_code || rate.currency?.code || rate.currency,
        value: `${rate.buy || rate.buy_rate || 0} / ${rate.sell || rate.sell_rate || 0}`,
        buy: rate.buy || rate.buy_rate,
        sell: rate.sell || rate.sell_rate,
        date: rate.date,
        time: rate.time
      })
    })
    
    const result = Object.values(grouped)
    console.log('[DEBUG Store] Grouped bank rates result:', result)
    return result
  })

  const latestRates = computed(() => {
    const latest = {}
    bankRates.value.forEach(rate => {
      const key = `${rate.bank_name || rate.bank?.name}-${rate.currency_code || rate.currency?.code}`
      if (!latest[key] || new Date(rate.created_at || rate.date) > new Date(latest[key].created_at || latest[key].date)) {
        latest[key] = rate
      }
    })
    return Object.values(latest)
  })

  return {
    bankRates,
    marketRates,
    loading,
    error,
    groupedBankRates,
    latestRates,
    fetchBankRates,
    updateBankRate,
    fetchMarketRates,
    deleteMarketRate
  }
})