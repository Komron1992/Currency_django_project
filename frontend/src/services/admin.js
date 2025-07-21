// frontend/src/services/admin.js
import apiClient from './client.js'

export const adminAPI = {
  // ==============================================
  // СТАТИСТИКА И ДАШБОРД
  // ==============================================

  /**
   * Получение общей статистики для админ панели
   * @returns {Promise<Object>} Статистика системы
   */
  async getStatistics() {
    try {
      const response = await apiClient.get('/admin/statistics/')
      return response
    } catch (error) {
      console.error('❌ Get statistics error:', error)
      throw error
    }
  },

  /**
   * Получение аналитики по активности
   * @param {Object} params - Параметры фильтрации
   * @param {string} params.period - Период (day, week, month)
   * @param {string} params.start_date - Начальная дата
   * @param {string} params.end_date - Конечная дата
   * @returns {Promise<Object>} Данные аналитики
   */
  async getAnalytics(params = {}) {
    try {
      const response = await apiClient.get('/admin/analytics/', { params })
      return response
    } catch (error) {
      console.error('❌ Get analytics error:', error)
      throw error
    }
  },

  // ==============================================
  // УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ
  // ==============================================

  /**
   * Получение списка всех пользователей
   * @param {Object} params - Параметры фильтрации
   * @param {number} params.page - Номер страницы
   * @param {number} params.limit - Количество записей на странице
   * @param {string} params.search - Поисковый запрос
   * @param {string} params.role - Роль пользователя
   * @returns {Promise<Object>} Список пользователей
   */
  async getUsers(params = {}) {
    try {
      const response = await apiClient.get('/admin/users/', { params })
      return response
    } catch (error) {
      console.error('❌ Get users error:', error)
      throw error
    }
  },

  /**
   * Создание нового пользователя
   * @param {Object} userData - Данные пользователя
   * @param {string} userData.username - Имя пользователя
   * @param {string} userData.email - Email
   * @param {string} userData.password - Пароль
   * @param {string} userData.first_name - Имя
   * @param {string} userData.last_name - Фамилия
   * @param {string} userData.role - Роль
   * @returns {Promise<Object>} Созданный пользователь
   */
  async createUser(userData) {
    try {
      const response = await apiClient.post('/admin/users/', userData)
      console.log('✅ User created successfully')
      return response
    } catch (error) {
      console.error('❌ Create user error:', error)
      throw error
    }
  },

  /**
   * Обновление данных пользователя
   * @param {number} userId - ID пользователя
   * @param {Object} userData - Обновленные данные
   * @returns {Promise<Object>} Обновленный пользователь
   */
  async updateUser(userId, userData) {
    try {
      const response = await apiClient.patch(`/admin/users/${userId}/`, userData)
      console.log('✅ User updated successfully')
      return response
    } catch (error) {
      console.error('❌ Update user error:', error)
      throw error
    }
  },

  /**
   * Удаление пользователя
   * @param {number} userId - ID пользователя
   * @returns {Promise<Object>} Результат удаления
   */
  async deleteUser(userId) {
    try {
      const response = await apiClient.delete(`/admin/users/${userId}/`)
      console.log('✅ User deleted successfully')
      return response
    } catch (error) {
      console.error('❌ Delete user error:', error)
      throw error
    }
  },

  /**
   * Блокировка/разблокировка пользователя
   * @param {number} userId - ID пользователя
   * @param {boolean} isActive - Активность пользователя
   * @returns {Promise<Object>} Результат операции
   */
  async toggleUserStatus(userId, isActive) {
    try {
      const response = await apiClient.patch(`/admin/users/${userId}/`, { is_active: isActive })
      console.log(`✅ User ${isActive ? 'activated' : 'deactivated'} successfully`)
      return response
    } catch (error) {
      console.error('❌ Toggle user status error:', error)
      throw error
    }
  },

  // ==============================================
  // УПРАВЛЕНИЕ РАБОТНИКАМИ
  // ==============================================

  /**
   * Получение списка работников
   * @param {Object} params - Параметры фильтрации
   * @param {number} params.page - Номер страницы
   * @param {string} params.search - Поиск
   * @param {string} params.city - Город
   * @param {boolean} params.is_active - Активность
   * @returns {Promise<Object>} Список работников
   */
  async getWorkers(params = {}) {
    try {
      const response = await apiClient.get('/admin/workers/', { params })
      return {
        data: response.data || [],
        ...response
      }
    } catch (error) {
      console.error('❌ Get workers error:', error)
      return { data: [] }
    }
  },

  /**
   * Создание нового работника
   * @param {Object} workerData - Данные работника
   * @param {string} workerData.username - Имя пользователя
   * @param {string} workerData.email - Email
   * @param {string} workerData.password - Пароль
   * @param {string} workerData.city_name - Название города
   * @returns {Promise<Object>} Созданный работник
   */
  async createWorker(workerData) {
    try {
      const payload = {
        username: workerData.username,
        email: workerData.email || '',
        first_name: workerData.first_name || '',
        last_name: workerData.last_name || '',
        phone: workerData.phone || '',
        password: workerData.password,
        password_confirm: workerData.password_confirm,
        city_name: workerData.city_name,
        is_worker_active: workerData.is_worker_active !== undefined ? workerData.is_worker_active : true
      }

      console.log('🚀 Creating worker with payload:', payload)
      const response = await apiClient.post('/admin/workers/', payload)
      console.log('✅ Worker created successfully:', response.data)
      return response
    } catch (error) {
      console.error('❌ Create worker error:', error)

      // Улучшенная обработка ошибок
      if (error.response) {
        console.error('📋 Error response data:', error.response.data)
        console.error('📋 Error response status:', error.response.status)
        console.error('📋 Error response headers:', error.response.headers)

        // Создаем более информативную ошибку
        const enhancedError = new Error('Ошибка создания работника')
        enhancedError.response = error.response
        enhancedError.data = error.response.data
        enhancedError.status = error.response.status

        throw enhancedError
      } else if (error.request) {
        console.error('📋 Error request:', error.request)
        throw new Error('Нет ответа от сервера')
      } else {
        console.error('📋 Error message:', error.message)
        throw error
      }
    }
  },

  /**
   * Обновление данных работника
   * @param {number} workerId - ID работника
   * @param {Object} workerData - Обновленные данные
   * @returns {Promise<Object>} Обновленный работник
   */
  async updateWorker(workerId, workerData) {
    try {
      const payload = {
        username: workerData.username,
        email: workerData.email || '',
        first_name: workerData.first_name || '',
        last_name: workerData.last_name || '',
        city_name: workerData.city_name,
        phone: workerData.phone || '',
        is_worker_active: workerData.is_worker_active
      }

      if (workerData.password) {
        payload.password = workerData.password
        payload.password_confirm = workerData.password_confirm
      }

      console.log('🚀 Updating worker with payload:', payload)
      const response = await apiClient.patch(`/admin/workers/${workerId}/`, payload)
      console.log('✅ Worker updated successfully:', response.data)
      return response
    } catch (error) {
      console.error('❌ Update worker error:', error)

      // Улучшенная обработка ошибок
      if (error.response) {
        console.error('📋 Error response data:', error.response.data)
        console.error('📋 Error response status:', error.response.status)

        const enhancedError = new Error('Ошибка обновления работника')
        enhancedError.response = error.response
        enhancedError.data = error.response.data
        enhancedError.status = error.response.status

        throw enhancedError
      } else if (error.request) {
        console.error('📋 Error request:', error.request)
        throw new Error('Нет ответа от сервера')
      } else {
        console.error('📋 Error message:', error.message)
        throw error
      }
    }
  },

  /**
   * Удаление работника
   * @param {number} workerId - ID работника
   * @returns {Promise<Object>} Результат удаления
   */
  async deleteWorker(workerId) {
    try {
      const response = await apiClient.delete(`/admin/workers/${workerId}/`)
      console.log('✅ Worker deleted successfully')
      return response
    } catch (error) {
      console.error('❌ Delete worker error:', error)
      throw error
    }
  },

  // ==============================================
  // УПРАВЛЕНИЕ ГОРОДАМИ
  // ==============================================

  /**
   * Получение списка городов
   * @returns {Promise<Object>} Список городов
   */
  async getCities() {
    try {
      const response = await apiClient.get('/cities/')
      return response
    } catch (error) {
      console.error('❌ Get cities error:', error)
      throw error
    }
  },

  /**
   * Создание нового города
   * @param {Object} cityData - Данные города
   * @param {string} cityData.name - Название города
   * @param {boolean} cityData.is_active - Активность
   * @returns {Promise<Object>} Созданный город
   */
  async createCity(cityData) {
    try {
      const response = await apiClient.post('/admin/cities/', cityData)
      console.log('✅ City created successfully')
      return response
    } catch (error) {
      console.error('❌ Create city error:', error)
      throw error
    }
  },

  /**
   * Обновление данных города
   * @param {number} cityId - ID города
   * @param {Object} cityData - Обновленные данные
   * @returns {Promise<Object>} Обновленный город
   */
  async updateCity(cityId, cityData) {
    try {
      const response = await apiClient.patch(`/admin/cities/${cityId}/`, cityData)
      console.log('✅ City updated successfully')
      return response
    } catch (error) {
      console.error('❌ Update city error:', error)
      throw error
    }
  },

  /**
   * Удаление города
   * @param {number} cityId - ID города
   * @returns {Promise<Object>} Результат удаления
   */
  async deleteCity(cityId) {
    try {
      const response = await apiClient.delete(`/admin/cities/${cityId}/`)
      console.log('✅ City deleted successfully')
      return response
    } catch (error) {
      console.error('❌ Delete city error:', error)
      throw error
    }
  },

  // ==============================================
  // БАНКОВСКИЕ КУРСЫ
  // ==============================================

  /**
   * Получение банковских курсов
   * @returns {Promise<Object>} Банковские курсы
   */
  async getBankRates() {
    try {
      const response = await apiClient.get('/public/bank-rates/')
      return response
    } catch (error) {
      console.error('❌ Get bank rates error:', error)
      throw error
    }
  },

  /**
   * Обновление банковских курсов
   * @returns {Promise<Object>} Результат обновления
   */
  async updateBankRates() {
    try {
      const response = await apiClient.post('/public/bank-rates/update/')
      console.log('✅ Bank rates updated successfully')
      return response
    } catch (error) {
      console.error('❌ Update bank rates error:', error)
      throw error
    }
  },

  // ==============================================
  // ЛОГИ И АКТИВНОСТЬ
  // ==============================================

  /**
   * Получение логов активности работников
   * @param {Object} params - Параметры фильтрации
   * @param {number} params.page - Номер страницы
   * @param {string} params.worker_id - ID работника
   * @param {string} params.date_from - Дата с
   * @param {string} params.date_to - Дата по
   * @returns {Promise<Object>} Логи активности
   */
  async getActivityLogs(params = {}) {
    try {
      const response = await apiClient.get('/admin/worker-activity/', { params })
      return response
    } catch (error) {
      console.error('❌ Get activity logs error:', error)
      throw error
    }
  },

  /**
   * Получение системных логов
   * @param {Object} params - Параметры фильтрации
   * @returns {Promise<Object>} Системные логи
   */
  async getSystemLogs(params = {}) {
    try {
      const response = await apiClient.get('/admin/system-logs/', { params })
      return response
    } catch (error) {
      console.error('❌ Get system logs error:', error)
      throw error
    }
  },

  // ==============================================
  // НАСТРОЙКИ СИСТЕМЫ
  // ==============================================

  /**
   * Получение настроек системы
   * @returns {Promise<Object>} Настройки системы
   */
  async getSettings() {
    try {
      const response = await apiClient.get('/admin/settings/')
      return response
    } catch (error) {
      console.error('❌ Get settings error:', error)
      throw error
    }
  },

  // ==============================================
  // РЫНОЧНЫЕ КУРСЫ
  // ==============================================

  /**
   * Получение рыночных курсов
   * @param {Object} params - Параметры фильтрации
   * @param {number} params.page - Номер страницы
   * @param {string} params.city - Город
   * @param {string} params.date - Дата
   * @returns {Promise<Object>} Рыночные курсы
   */
  async getMarketRates(params = {}) {
    try {
      const response = await apiClient.get('/admin/market-exchange-rates/', { params })
      return response
    } catch (error) {
      console.error('❌ Get market rates error:', error)
      throw error
    }
  },

  /**
   * Создание рыночного курса
   * @param {Object} rateData - Данные курса
   * @returns {Promise<Object>} Созданный курс
   */
  async createMarketRate(rateData) {
    try {
      const response = await apiClient.post('/admin/market-exchange-rates/', rateData)
      console.log('✅ Market rate created successfully')
      return response
    } catch (error) {
      console.error('❌ Create market rate error:', error)
      throw error
    }
  },

/**
 * Обновление рыночного курса
 * @param {number} rateId - ID курса
 * @param {Object} rateData - Данные курса
 * @returns {Promise<Object>} Обновленный курс
 */
async updateMarketRate(rateId, rateData) {
  try {
    // Подготавливаем только нужные поля для обновления
    const payload = {
      currency: rateData.currency, // ID валюты
      buy: rateData.buy,
      sell: rateData.sell,
      is_active: rateData.is_active,
      notes: rateData.notes || ''
    }

    // Удаляем неразрешённые или лишние поля
    const readonlyFields = ['date', 'time', 'added_by']
    readonlyFields.forEach(field => delete payload[field])

    // Удаляем undefined/null
    Object.keys(payload).forEach(key => {
      if (payload[key] === undefined || payload[key] === null) {
        delete payload[key]
      }
    })

    console.log('🚀 Updating market rate with payload:', payload)
    console.log('📍 Rate ID:', rateId)

    const response = await apiClient.patch(`/admin/market-exchange-rates/${rateId}/`, payload)
    console.log('✅ Market rate updated successfully:', response.data)
    return response
  } catch (error) {
    console.error('❌ Update market rate error:', error)

    // Подробная обработка ошибок
    if (error.response) {
      console.error('📋 Статус ответа:', error.response.status)
      console.error('📋 Данные ответа:', error.response.data)
      console.error('📋 Заголовки ответа:', error.response.headers)

      const enhancedError = new Error('Ошибка обновления рыночного курса')
      enhancedError.response = error.response
      enhancedError.data = error.response.data
      enhancedError.status = error.response.status
      throw enhancedError
    } else if (error.request) {
      console.error('📋 Нет ответа от сервера:', error.request)
      throw new Error('Нет ответа от сервера')
    } else {
      console.error('📋 Ошибка запроса:', error.message)
      throw error
    }
  }
},


  /**
   * Удаление рыночного курса
   * @param {number} rateId - ID курса
   * @returns {Promise<Object>} Результат удаления
   */
  async deleteMarketRate(rateId) {
    try {
      const response = await apiClient.delete(`/admin/market-exchange-rates/${rateId}/`)
      console.log('✅ Market rate deleted successfully')
      return response
    } catch (error) {
      console.error('❌ Delete market rate error:', error)
      throw error
    }
  },

  // ==============================================
  // БАНКОВСКИЕ КУРСЫ
  // ==============================================

  /**
   * Получение банковских курсов
   * @returns {Promise<Object>} Банковские курсы
   */
  async getBankRates() {
    try {
      const response = await apiClient.get('/public/bank-rates/')
      return response
    } catch (error) {
      console.error('❌ Get bank rates error:', error)
      throw error
    }
  },


  /**
   * Обновление настроек системы
   * @param {Object} settings - Настройки
   * @returns {Promise<Object>} Обновленные настройки
   */
  async updateSettings(settings) {
    try {
      const response = await apiClient.patch('/admin/settings/', settings)
      console.log('✅ Settings updated successfully')
      return response
    } catch (error) {
      console.error('❌ Update settings error:', error)
      throw error
    }
  }
}

export default adminAPI