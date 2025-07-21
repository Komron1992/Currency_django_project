// frontend/src/stores/auth.js
import { defineStore } from 'pinia'
import { authAPI } from '@/services/auth.js'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: null,
    refreshToken: null,
    isAuthenticated: false,
    isInitialized: false,
    loading: false,
    error: null
  }),

  getters: {
    hasToken: (state) => !!state.token,
    isAdmin: (state) =>
      state.user?.role === 'admin' || state.user?.is_superuser === true || state.user?.is_superuser === 1,
    isWorker: (state) => state.user?.role === 'city_worker',
    isSuperuser: (state) => !!state.user?.is_superuser,
    userName: (state) => state.user?.username || state.user?.email || 'User'
  },

  actions: {
    async initialize() {
      if (this.isInitialized) return

      const token = localStorage.getItem('access_token')
      const refreshToken = localStorage.getItem('refresh_token')
      const userData = localStorage.getItem('user_data')

      if (token && refreshToken) {
        this.token = token
        this.refreshToken = refreshToken

        try {
          this.user = JSON.parse(userData)
          this.isAuthenticated = true
        } catch {
          this.clearAuthData()
          return
        }

        const valid = await this.validateToken()
        if (!valid) this.clearAuthData()
      }

      this.isInitialized = true
    },

    async login(credentials) {
      this.loading = true
      this.error = null

      try {
        const res = await authAPI.login(credentials)
        const { access, refresh, user } = res.data

        this.token = access
        this.refreshToken = refresh
        this.user = user
        this.isAuthenticated = true

        localStorage.setItem('access_token', access)
        localStorage.setItem('refresh_token', refresh)
        localStorage.setItem('user_data', JSON.stringify(user))

        return { success: true }
      } catch (err) {
        const msg =
          err.response?.data?.message ||
          err.response?.data?.detail ||
          err.response?.data?.error ||
          'Ошибка входа'
        this.error = msg
        return { success: false, error: msg }
      } finally {
        this.loading = false
      }
    },

    async register(userData) {
      this.loading = true
      this.error = null
      try {
        const res = await authAPI.register(userData)
        return { success: true, data: res.data }
      } catch (err) {
        const msg =
          err.response?.data?.message ||
          err.response?.data?.detail ||
          err.response?.data?.error ||
          'Ошибка регистрации'
        this.error = msg
        return { success: false, error: msg }
      } finally {
        this.loading = false
      }
    },

    async validateToken() {
      if (!this.token) return false

      try {
        const res = await authAPI.getCurrentUser()
        this.user = res.data
        this.isAuthenticated = true
        localStorage.setItem('user_data', JSON.stringify(this.user))
        return true
      } catch {
        return await this.refreshAccessToken()
      }
    },

    async refreshAccessToken() {
      if (!this.refreshToken) return false

      try {
        const res = await authAPI.refreshToken(this.refreshToken)
        const { access } = res.data
        this.updateToken(access)
        return true
      } catch {
        this.clearAuthData()
        return false
      }
    },

    async logout() {
      try {
        await authAPI.logout()
      } catch (err) {
        console.warn('[AuthStore] Logout error (ignored)', err)
      }
      this.clearAuthData()
    },

    updateToken(newToken) {
      this.token = newToken
      localStorage.setItem('access_token', newToken)
    },

    clearAuthData() {
      this.user = null
      this.token = null
      this.refreshToken = null
      this.isAuthenticated = false
      this.error = null
      this.isInitialized = true
      localStorage.clear()
    },

    updateUser(userData) {
      this.user = { ...this.user, ...userData }
      localStorage.setItem('user_data', JSON.stringify(this.user))
    },

    hasRole(role) {
      if (!this.user) return false
      if (role === 'admin') {
        return this.user.role === 'admin' || this.user.is_superuser === true || this.user.is_superuser === 1
      }
      return this.user.role === role
    }
  }
})