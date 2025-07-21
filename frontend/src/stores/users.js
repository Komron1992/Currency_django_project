// frontend/src/stores/users.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from '@/services/client.js'
import { adminAPI } from '@/services/admin.js'

export const useUsersStore = defineStore('users', () => {
  const users = ref([])
  const workers = ref([])
  const currentUser = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // ✅ Регистрация пользователя
  const register = async (userData) => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.post('/auth/register/', userData)
      currentUser.value = response.data
      return {
        success: true,
        message: 'Регистрация прошла успешно!'
      }
    } catch (err) {
      console.error('Register error:', err)
      error.value = err.response?.data?.detail || 'Ошибка регистрации'
      return {
        success: false,
        error: err.response?.data || 'Ошибка регистрации'
      }
    } finally {
      loading.value = false
    }
  }

  // ✅ Загрузка всех пользователей (только для админа)
  const fetchUsers = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await adminAPI.getUsers()
      users.value = response.data
    } catch (err) {
      console.error('Fetch users error:', err)
      error.value = 'Ошибка загрузки пользователей'
    } finally {
      loading.value = false
    }
  }

  // ✅ Загрузка сотрудников (через админ API)
  const fetchWorkers = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await adminAPI.getWorkers()
      workers.value = response.data
    } catch (err) {
      console.error('Fetch workers error:', err)
      error.value = 'Ошибка загрузки сотрудников'
    } finally {
      loading.value = false
    }
  }

  // ✅ Создание работника
  const createWorker = async (workerData) => {
    try {
      const response = await adminAPI.createWorker(workerData)
      workers.value.push(response.data)
      return { success: true, data: response.data }
    } catch (err) {
      console.error('Create worker error:', err)
      return {
        success: false,
        error: err.response?.data || 'Ошибка создания сотрудника'
      }
    }
  }

  // ✅ Обновление работника
  const updateWorker = async (workerId, workerData) => {
    try {
      const response = await adminAPI.updateWorker(workerId, workerData)
      const index = workers.value.findIndex(worker => worker.id === workerId)
      if (index !== -1) workers.value[index] = response.data
      return { success: true, data: response.data }
    } catch (err) {
      console.error('Update worker error:', err)
      return {
        success: false,
        error: err.response?.data || 'Ошибка обновления сотрудника'
      }
    }
  }

  // ✅ Удаление работника
  const deleteWorker = async (workerId) => {
    try {
      await adminAPI.deleteWorker(workerId)
      workers.value = workers.value.filter(worker => worker.id !== workerId)
      return { success: true }
    } catch (err) {
      console.error('Delete worker error:', err)
      return {
        success: false,
        error: err.response?.data?.detail || 'Ошибка удаления сотрудника'
      }
    }
  }

  // ✅ Переключение статуса работника
  const toggleWorkerStatus = async (workerId) => {
    try {
      const worker = workers.value.find(w => w.id === workerId)
      if (!worker) throw new Error('Работник не найден')

      const newStatus = !worker.is_worker_active
      const response = await adminAPI.updateWorker(workerId, {
        is_worker_active: newStatus
      })

      const index = workers.value.findIndex(worker => worker.id === workerId)
      if (index !== -1) {
        workers.value[index].is_worker_active = response.data.is_worker_active
      }

      return { success: true, data: response.data }
    } catch (err) {
      console.error('Toggle worker status error:', err)
      return {
        success: false,
        error: err.response?.data?.detail || 'Ошибка изменения статуса'
      }
    }
  }

  // ✅ Назначение банков работнику
  const assignBanksToWorker = async (workerId, bankNames) => {
    try {
      const response = await apiClient.post(`/admin/workers/${workerId}/assign-banks/`, {
        bank_names: bankNames
      })

      const index = workers.value.findIndex(worker => worker.id === workerId)
      if (index !== -1) workers.value[index] = response.data

      return { success: true, data: response.data }
    } catch (err) {
      console.error('Assign banks error:', err)
      return {
        success: false,
        error: err.response?.data?.detail || 'Ошибка назначения банков'
      }
    }
  }

  // ✅ Создание пользователя (через админ API)
  const createUser = async (userData) => {
    try {
      const response = await adminAPI.createUser(userData)
      users.value.push(response.data)
      return { success: true, data: response.data }
    } catch (err) {
      console.error('Create user error:', err)
      return {
        success: false,
        error: err.response?.data || 'Ошибка создания пользователя'
      }
    }
  }

  // ✅ Обновление пользователя
  const updateUser = async (userId, userData) => {
    try {
      const response = await adminAPI.updateUser(userId, userData)
      const index = users.value.findIndex(user => user.id === userId)
      if (index !== -1) users.value[index] = response.data
      return { success: true, data: response.data }
    } catch (err) {
      console.error('Update user error:', err)
      return {
        success: false,
        error: err.response?.data || 'Ошибка обновления пользователя'
      }
    }
  }

  // ✅ Удаление пользователя
  const deleteUser = async (userId) => {
    try {
      await adminAPI.deleteUser(userId)
      users.value = users.value.filter(user => user.id !== userId)
      return { success: true }
    } catch (err) {
      console.error('Delete user error:', err)
      return {
        success: false,
        error: err.response?.data?.detail || 'Ошибка удаления пользователя'
      }
    }
  }

  return {
    users,
    workers,
    currentUser,
    loading,
    error,
    register,
    fetchUsers,
    fetchWorkers,
    createWorker,
    updateWorker,
    deleteWorker,
    toggleWorkerStatus,
    assignBanksToWorker,
    createUser,
    updateUser,
    deleteUser
  }
})