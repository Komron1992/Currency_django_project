// composables/useWorkers.js
import { ref } from 'vue'
import { adminAPI } from '../services/api'

export function useWorkers() {
  // Reactive state
  const workers = ref([])
  const cities = ref([])
  const loading = ref(false)
  const error = ref('')
  const saving = ref(false)

  // Load workers
  const loadWorkers = async () => {
    loading.value = true
    error.value = ''

    try {
      const response = await adminAPI.getWorkers()
      workers.value = response.data
      return response.data
    } catch (err) {
      console.error('Error loading workers:', err)

      // Better error handling
      if (err.response?.status === 401) {
        error.value = 'Нет доступа. Войдите в систему как администратор'
      } else if (err.response?.status === 403) {
        error.value = 'Недостаточно прав для просмотра работников'
      } else if (err.response?.status >= 500) {
        error.value = 'Ошибка сервера. Попробуйте позже'
      } else {
        error.value = err.response?.data?.detail || 'Не удалось загрузить список работников'
      }

      throw err
    } finally {
      loading.value = false
    }
  }

  // Load cities
  const loadCities = async () => {
    try {
      const response = await adminAPI.getCities()
      cities.value = response.data
      return response.data
    } catch (err) {
      console.error('Error loading cities:', err)
      // Don't set main error for cities, as it's secondary data
      throw err
    }
  }

  // Create worker
  const createWorker = async (workerData) => {
    saving.value = true

    try {
      // Validate required fields
      const requiredFields = ['username', 'email', 'first_name', 'last_name', 'password']
      for (const field of requiredFields) {
        if (!workerData[field] || workerData[field].trim() === '') {
          throw new Error(`Поле ${field} обязательно для заполнения`)
        }
      }

      const response = await adminAPI.createWorker(workerData)
      workers.value.push(response.data)
      return response.data
    } catch (err) {
      console.error('Error creating worker:', err)
      throw err
    } finally {
      saving.value = false
    }
  }

  // Update worker
  const updateWorker = async (workerId, workerData) => {
    saving.value = true

    try {
      // Remove empty password for update
      const dataToSend = { ...workerData }
      if (!dataToSend.password || dataToSend.password.trim() === '') {
        delete dataToSend.password
      }

      const response = await adminAPI.updateWorker(workerId, dataToSend)

      // Update worker in the list
      const index = workers.value.findIndex(w => w.id === workerId)
      if (index !== -1) {
        workers.value[index] = response.data
      }

      return response.data
    } catch (err) {
      console.error('Error updating worker:', err)
      throw err
    } finally {
      saving.value = false
    }
  }

  // Toggle worker status
  const toggleStatus = async (workerId, newStatus) => {
    try {
      const response = await adminAPI.updateWorker(workerId, {
        is_worker_active: newStatus
      })

      // Update status in the list
      const worker = workers.value.find(w => w.id === workerId)
      if (worker) {
        worker.is_worker_active = newStatus
      }

      return response.data
    } catch (err) {
      console.error('Error toggling worker status:', err)
      throw err
    }
  }

  // Delete worker
  const deleteWorker = async (workerId) => {
    try {
      await adminAPI.deleteWorker(workerId)

      // Remove from list
      const index = workers.value.findIndex(w => w.id === workerId)
      if (index !== -1) {
        workers.value.splice(index, 1)
      }

      return true
    } catch (err) {
      console.error('Error deleting worker:', err)
      throw err
    }
  }

  // Get worker by ID
  const getWorkerById = (workerId) => {
    return workers.value.find(w => w.id === workerId)
  }

  // Get workers statistics
  const getWorkersStats = () => {
    const total = workers.value.length
    const active = workers.value.filter(w => w.is_worker_active).length
    const inactive = total - active

    return {
      total,
      active,
      inactive,
      activePercentage: total ? Math.round((active / total) * 100) : 0
    }
  }

  // Group workers by city
  const getWorkersByCity = () => {
    const grouped = {}

    workers.value.forEach(worker => {
      const cityName = worker.city ? worker.city.name : 'Без города'
      if (!grouped[cityName]) {
        grouped[cityName] = []
      }
      grouped[cityName].push(worker)
    })

    return grouped
  }

  // Validate worker data
  const validateWorkerData = (workerData, isUpdate = false) => {
    const errors = []

    // Required fields
    if (!workerData.username?.trim()) {
      errors.push('Имя пользователя обязательно')
    }

    if (!workerData.email?.trim()) {
      errors.push('Email обязателен')
    } else {
      // Basic email validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(workerData.email)) {
        errors.push('Некорректный формат email')
      }
    }

    if (!workerData.first_name?.trim()) {
      errors.push('Имя обязательно')
    }

    if (!workerData.last_name?.trim()) {
      errors.push('Фамилия обязательна')
    }

    // Password validation (only for creation or when provided)
    if (!isUpdate && !workerData.password) {
      errors.push('Пароль обязателен')
    } else if (workerData.password && workerData.password.length < 6) {
      errors.push('Пароль должен содержать минимум 6 символов')
    }

    return errors
  }

  return {
    // State
    workers,
    cities,
    loading,
    error,
    saving,

    // Methods
    loadWorkers,
    loadCities,
    createWorker,
    updateWorker,
    toggleStatus,
    deleteWorker,
    getWorkerById,
    getWorkersStats,
    getWorkersByCity,
    validateWorkerData
  }
}