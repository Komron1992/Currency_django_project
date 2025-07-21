// composables/useNotifications.js
import { ref } from 'vue'

export function useNotifications() {
  // Состояние уведомлений
  const notifications = ref([])
  let notificationIdCounter = 0

  // Типы уведомлений
  const NOTIFICATION_TYPES = {
    SUCCESS: 'success',
    ERROR: 'error',
    WARNING: 'warning',
    INFO: 'info'
  }

  // Создание уведомления
  const createNotification = (message, type = NOTIFICATION_TYPES.INFO, duration = 5000) => {
    const notification = {
      id: ++notificationIdCounter,
      message,
      type,
      timestamp: new Date(),
      duration,
      visible: true
    }

    notifications.value.push(notification)

    // Автоматическое удаление через заданное время
    if (duration > 0) {
      setTimeout(() => {
        removeNotification(notification.id)
      }, duration)
    }

    return notification
  }

  // Показать уведомление
  const showNotification = (message, type = NOTIFICATION_TYPES.INFO, options = {}) => {
    const {
      duration = 5000,
      persistent = false,
      action = null
    } = options

    return createNotification(
      message,
      type,
      persistent ? 0 : duration
    )
  }

  // Удаление уведомления
  const removeNotification = (id) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  // Очистка всех уведомлений
  const clearAllNotifications = () => {
    notifications.value = []
  }

  // Специализированные методы для разных типов уведомлений
  const showSuccess = (message, options = {}) => {
    return showNotification(message, NOTIFICATION_TYPES.SUCCESS, {
      duration: 3000,
      ...options
    })
  }

  const showError = (message, options = {}) => {
    return showNotification(message, NOTIFICATION_TYPES.ERROR, {
      duration: 7000,
      ...options
    })
  }

  const showWarning = (message, options = {}) => {
    return showNotification(message, NOTIFICATION_TYPES.WARNING, {
      duration: 5000,
      ...options
    })
  }

  const showInfo = (message, options = {}) => {
    return showNotification(message, NOTIFICATION_TYPES.INFO, {
      duration: 4000,
      ...options
    })
  }

  // Показать уведомление с подтверждением
  const showConfirmation = (message, onConfirm, onCancel = null) => {
    return showNotification(message, NOTIFICATION_TYPES.WARNING, {
      persistent: true,
      action: {
        confirm: {
          text: 'Подтвердить',
          handler: onConfirm
        },
        cancel: {
          text: 'Отмена',
          handler: onCancel
        }
      }
    })
  }

  // Показать уведомление загрузки
  const showLoading = (message = 'Загрузка...') => {
    return showNotification(message, NOTIFICATION_TYPES.INFO, {
      persistent: true
    })
  }

  // Обновить существующее уведомление
  const updateNotification = (id, updates) => {
    const notification = notifications.value.find(n => n.id === id)
    if (notification) {
      Object.assign(notification, updates)
    }
  }

  // Получить количество уведомлений по типу
  const getNotificationCount = (type = null) => {
    if (type) {
      return notifications.value.filter(n => n.type === type).length
    }
    return notifications.value.length
  }

  // Проверить наличие уведомлений определенного типа
  const hasNotifications = (type = null) => {
    return getNotificationCount(type) > 0
  }

  // Получить последнее уведомление
  const getLastNotification = (type = null) => {
    const filtered = type
      ? notifications.value.filter(n => n.type === type)
      : notifications.value

    return filtered.length > 0 ? filtered[filtered.length - 1] : null
  }

  // Хелперы для работы с ошибками API
  const handleApiError = (error, context = '') => {
    let message = 'Произошла ошибка'

    if (error.response?.data) {
      if (typeof error.response.data === 'string') {
        message = error.response.data
      } else if (error.response.data.message) {
        message = error.response.data.message
      } else if (error.response.data.detail) {
        message = error.response.data.detail
      } else {
        // Обработка ошибок валидации
        const errors = Object.values(error.response.data).flat()
        message = errors.join(', ')
      }
    } else if (error.message) {
      message = error.message
    }

    if (context) {
      message = `${context}: ${message}`
    }

    return showError(message)
  }

  // Показать уведомление об успешном действии
  const showActionSuccess = (action, entity = '') => {
    const messages = {
      create: `${entity} успешно создан`,
      update: `${entity} успешно обновлен`,
      delete: `${entity} успешно удален`,
      save: `${entity} успешно сохранен`
    }

    const message = messages[action] || `Действие выполнено успешно`
    return showSuccess(message)
  }

  return {
    // Состояние
    notifications,
    NOTIFICATION_TYPES,

    // Основные методы
    showNotification,
    removeNotification,
    clearAllNotifications,
    updateNotification,

    // Специализированные методы
    showSuccess,
    showError,
    showWarning,
    showInfo,
    showConfirmation,
    showLoading,

    // Утилиты
    getNotificationCount,
    hasNotifications,
    getLastNotification,
    handleApiError,
    showActionSuccess
  }
}