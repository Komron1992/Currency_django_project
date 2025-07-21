// frontend/src/services/auth.js
import apiClient from './client.js'

export const authAPI = {
  /**
   * Проверка авторизации пользователя
   * @returns {boolean}
   */
  isAuthenticated() {
    return !!localStorage.getItem('access_token')
  },

  /**
   * Авторизация пользователя
   * @param {Object} credentials - Данные для входа
   * @param {string} credentials.username - Имя пользователя
   * @param {string} credentials.password - Пароль
   * @returns {Promise<Object>} Ответ сервера с токенами
   */
  async login(credentials) {
    try {
      const response = await apiClient.post('/auth/login/', credentials)

      // Сохраняем токены
      if (response.data.access) {
        localStorage.setItem('access_token', response.data.access)
      }
      if (response.data.refresh) {
        localStorage.setItem('refresh_token', response.data.refresh)
      }

      console.log('✅ Login successful')
      return response
    } catch (error) {
      console.error('❌ Login error:', error)
      throw error
    }
  },

  /**
   * Выход из системы
   */
  async logout() {
    const refreshToken = localStorage.getItem('refresh_token')
    if (refreshToken) {
      try {
        await apiClient.post('/auth/logout/', { refresh: refreshToken })
        console.log('✅ Logout successful')
      } catch (error) {
        console.error('❌ Logout error:', error)
      }
    }
    localStorage.clear()
  },

  /**
   * Регистрация нового пользователя
   * @param {Object} userData - Данные пользователя
   * @param {string} userData.username - Имя пользователя
   * @param {string} userData.email - Email
   * @param {string} userData.password - Пароль
   * @param {string} userData.password_confirm - Подтверждение пароля
   * @returns {Promise<Object>} Ответ сервера
   */
  async register(userData) {
    try {
      const response = await apiClient.post('/auth/register/', userData)
      console.log('✅ Registration successful')
      return response
    } catch (error) {
      console.error('❌ Register error:', error)
      throw error
    }
  },

  /**
   * Обновление токена доступа
   * @param {string} refreshToken - Refresh токен
   * @returns {Promise<Object>} Ответ сервера с новым токеном
   */
  async refreshToken(refreshToken) {
    try {
      const response = await apiClient.post('/token/refresh/', { refresh: refreshToken })
      console.log('✅ Token refresh successful')
      return response
    } catch (error) {
      console.error('❌ Refresh token error:', error)
      throw error
    }
  },

  /**
   * Получение данных текущего пользователя
   * @returns {Promise<Object>} Данные пользователя
   */
  async getCurrentUser() {
    try {
      const response = await apiClient.get('/auth/user/')
      return response
    } catch (error) {
      console.error('❌ Get current user error:', error)
      throw error
    }
  },

  /**
   * Изменение пароля
   * @param {Object} passwordData - Данные для смены пароля
   * @param {string} passwordData.old_password - Старый пароль
   * @param {string} passwordData.new_password - Новый пароль
   * @param {string} passwordData.new_password_confirm - Подтверждение нового пароля
   * @returns {Promise<Object>} Ответ сервера
   */
  async changePassword(passwordData) {
    try {
      const response = await apiClient.post('/auth/change-password/', passwordData)
      console.log('✅ Password changed successfully')
      return response
    } catch (error) {
      console.error('❌ Change password error:', error)
      throw error
    }
  },

  /**
   * Восстановление пароля
   * @param {Object} emailData - Email для восстановления
   * @param {string} emailData.email - Email пользователя
   * @returns {Promise<Object>} Ответ сервера
   */
  async forgotPassword(emailData) {
    try {
      const response = await apiClient.post('/auth/forgot-password/', emailData)
      console.log('✅ Password reset email sent')
      return response
    } catch (error) {
      console.error('❌ Forgot password error:', error)
      throw error
    }
  },

  /**
   * Подтверждение восстановления пароля
   * @param {Object} resetData - Данные для восстановления
   * @param {string} resetData.token - Токен восстановления
   * @param {string} resetData.password - Новый пароль
   * @param {string} resetData.password_confirm - Подтверждение пароля
   * @returns {Promise<Object>} Ответ сервера
   */
  async resetPassword(resetData) {
    try {
      const response = await apiClient.post('/auth/reset-password/', resetData)
      console.log('✅ Password reset successful')
      return response
    } catch (error) {
      console.error('❌ Reset password error:', error)
      throw error
    }
  }
}

export default authAPI