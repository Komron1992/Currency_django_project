// frontend/src/services/public.js
import apiClient from './client.js'

export const publicAPI = {
  // Получение рыночных курсов валют
  async getRates() {
    try {
      const response = await apiClient.get('/public/rates/')
      return response
    } catch (error) {
      console.error('Get public rates error:', error)
      throw error
    }
  },

  // Получение информации о банках
  async getBanks() {
    try {
      const response = await apiClient.get('/public/banks/')
      return response
    } catch (error) {
      console.error('Get banks error:', error)
      throw error
    }
  },

  // Получение курсов конкретного банка
  async getBankRates(bankId) {
    try {
      const response = await apiClient.get(`/public/banks/${bankId}/rates/`)
      return response
    } catch (error) {
      console.error('Get bank rates error:', error)
      throw error
    }
  },

  // Получение статистики по валютам
  async getCurrencyStats(currencyCode, days = 30) {
    try {
      const response = await apiClient.get(`/public/currencies/${currencyCode}/stats/`, {
        params: { days }
      })
      return response
    } catch (error) {
      console.error('Get currency stats error:', error)
      throw error
    }
  }
}

export default publicAPI