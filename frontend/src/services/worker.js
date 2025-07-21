// frontend/src/services/worker.js
import apiClient from './client.js'

export const workerAPI = {
  // Управление курсами
  async getRates() {
    try {
      const response = await apiClient.get('/workers/rates/')
      return response
    } catch (error) {
      console.error('Get worker rates error:', error)
      throw error
    }
  },

  async createRate(data) {
    try {
      console.log('Отправка данных на сервер:', data)
      const response = await apiClient.post('/workers/rates/', data)
      console.log('Ответ сервера:', response.data)
      return response
    } catch (error) {
      console.error('Ошибка API createRate:', error)
      console.error('Детали ошибки:', error.response?.data)
      throw error
    }
  },

  async updateRate(id, data) {
    try {
      console.log('Обновление курса:', id, data)
      const response = await apiClient.patch(`/workers/rates/${id}/`, data)
      return response
    } catch (error) {
      console.error('Ошибка API updateRate:', error)
      throw error
    }
  },

  async deleteRate(id) {
    try {
      const response = await apiClient.delete(`/workers/rates/${id}/`)
      return response
    } catch (error) {
      console.error('Ошибка API deleteRate:', error)
      throw error
    }
  },

  // Валюты работников
  async getCurrencies() {
    try {
      const response = await apiClient.get('/workers/currencies/')
      return response
    } catch (error) {
      console.error('Get worker currencies error:', error)
      throw error
    }
  },

  // Профиль работника
  async getProfile() {
    try {
      const response = await apiClient.get('/workers/profile/')
      return response
    } catch (error) {
      console.error('Get worker profile error:', error)
      throw error
    }
  },

  async updateProfile(data) {
    try {
      const response = await apiClient.patch('/workers/profile/', data)
      return response
    } catch (error) {
      console.error('Update worker profile error:', error)
      throw error
    }
  },

  // Активность работника
  async getWorkerActivity(params = {}) {
    try {
      const response = await apiClient.get('/workers/activity/', { params })
      return response
    } catch (error) {
      console.error('Get worker activity error:', error)
      throw error
    }
  },

  // Статистика работника
  async getWorkerStats() {
    try {
      const response = await apiClient.get('/workers/stats/')
      return response
    } catch (error) {
      console.error('Get worker stats error:', error)
      throw error
    }
  },

  // Уведомления
  async getNotifications() {
    try {
      const response = await apiClient.get('/workers/notifications/')
      return response
    } catch (error) {
      console.error('Get notifications error:', error)
      throw error
    }
  },

  async markNotificationAsRead(id) {
    try {
      const response = await apiClient.patch(`/workers/notifications/${id}/`, { is_read: true })
      return response
    } catch (error) {
      console.error('Mark notification as read error:', error)
      throw error
    }
  }
}

export default workerAPI