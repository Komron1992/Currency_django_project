<!-- frontend/src/views/admin/AdminLogin.vue -->
<template>
  <div class="login-container">
    <!-- Animated background elements -->
    <div class="background-overlay">
      <div class="bg-circle bg-circle-1"></div>
      <div class="bg-circle bg-circle-2"></div>
      <div class="bg-circle bg-circle-3"></div>
      <div class="bg-gradient"></div>
    </div>

    <div class="login-wrapper">
      <!-- Logo and Header -->
      <div class="header-section">
        <div class="logo-container">
          <svg class="logo-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
          </svg>
        </div>
        <h2 class="title">Админ Панель</h2>
        <p class="subtitle">Добро пожаловать в систему управления</p>
      </div>

      <!-- Login Form Card -->
      <div class="login-card">
        <!-- Success Message -->
        <div v-if="successMessage" class="success-message">
          <svg class="success-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <span>{{ successMessage }}</span>
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="error-message">
          <svg class="error-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
          </svg>
          <span>{{ errorMessage }}</span>
        </div>

        <!-- Login Form -->
        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-fields">
            <!-- Username Field -->
            <div class="field-group">
              <label for="username" class="field-label">
                Логин администратора
              </label>
              <div class="input-wrapper">
                <div class="input-icon">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                  </svg>
                </div>
                <input
                  id="username"
                  v-model="credentials.username"
                  name="username"
                  type="text"
                  required
                  class="form-input"
                  placeholder="Введите логин"
                  :disabled="isLoading"
                  autocomplete="username"
                />
              </div>
            </div>

            <!-- Password Field -->
            <div class="field-group">
              <label for="password" class="field-label">
                Пароль
              </label>
              <div class="input-wrapper">
                <div class="input-icon">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
                  </svg>
                </div>
                <input
                  id="password"
                  v-model="credentials.password"
                  name="password"
                  :type="showPassword ? 'text' : 'password'"
                  required
                  class="form-input password-input"
                  placeholder="Введите пароль"
                  :disabled="isLoading"
                  autocomplete="current-password"
                />
                <button
                  type="button"
                  @click="togglePassword"
                  class="password-toggle"
                  :disabled="isLoading"
                >
                  <svg v-if="showPassword" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"></path>
                  </svg>
                  <svg v-else fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                  </svg>
                </button>
              </div>
            </div>

            <!-- Remember Me -->
            <div class="field-group checkbox-group">
              <div class="checkbox-wrapper">
                <input
                  id="remember"
                  v-model="rememberMe"
                  type="checkbox"
                  class="checkbox-input"
                  :disabled="isLoading"
                />
                <label for="remember" class="checkbox-label">
                  <div class="checkbox-custom">
                    <svg class="checkbox-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                  </div>
                  Запомнить меня
                </label>
              </div>
            </div>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="isLoading || !isFormValid"
            class="submit-button"
          >
            <span v-if="isLoading" class="loading-spinner">
              <svg class="spinner-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="spinner-circle" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="spinner-path" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </span>
            <span class="button-content">
              <span>{{ isLoading ? 'Авторизация...' : 'Войти в систему' }}</span>
              <svg v-if="!isLoading" class="button-arrow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path>
              </svg>
            </span>
          </button>
        </form>

        <!-- Additional Links -->
        <div class="additional-links">
          <router-link to="/forgot-password" class="link">
            Забыли пароль?
          </router-link>
          <span class="link-separator">•</span>
          <router-link to="/" class="link">
            На главную
          </router-link>
        </div>
      </div>

      <!-- Footer -->
      <div class="footer">
        <p class="footer-text">
          © 2024 Система управления валютными курсами
        </p>
        <div class="footer-links">
          <a href="#" class="footer-link">Политика конфиденциальности</a>
          <span class="footer-separator">•</span>
          <a href="#" class="footer-link">Условия использования</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'AdminLogin',
  data() {
    return {
      credentials: {
        username: '',
        password: ''
      },
      errorMessage: '',
      successMessage: '',
      isLoading: false,
      showPassword: false,
      rememberMe: false,
      loginAttempts: 0,
      maxAttempts: 5,
      lockoutTime: 15 * 60 * 1000 // 15 minutes
    }
  },

  computed: {
    isFormValid() {
      return this.credentials.username.trim() &&
             this.credentials.password.trim() &&
             this.credentials.username.length >= 3 &&
             this.credentials.password.length >= 6
    }
  },

  async mounted() {
    await this.initializeAuth()
    this.checkLockout()
  },

  methods: {
    async initializeAuth() {
      try {
        const authStore = useAuthStore()
        await authStore.initialize()

        if (authStore.isAuthenticated) {
          this.checkAdminAccess()
        }
      } catch (error) {
        console.error('Ошибка инициализации:', error)
      }
    },

    checkAdminAccess() {
      const authStore = useAuthStore()
      const user = authStore.user

      if (user && (user.role === 'admin' || user.is_superuser)) {
        this.successMessage = 'Добро пожаловать!'
        setTimeout(() => {
          this.$router.push('/admin/dashboard')
        }, 1000)
      } else {
        authStore.logout()
        this.errorMessage = 'У вас нет прав доступа к админ панели'
      }
    },

    async handleLogin() {
      if (!this.isFormValid) {
        this.errorMessage = 'Пожалуйста, заполните все поля корректно'
        return
      }

      if (this.isLockedOut()) {
        this.errorMessage = 'Слишком много неудачных попыток. Попробуйте позже.'
        return
      }

      this.clearMessages()
      this.isLoading = true

      try {
        const authStore = useAuthStore()
        const result = await authStore.login(this.credentials)

        if (result && result.success) {
          this.loginAttempts = 0
          localStorage.removeItem('loginAttempts')
          localStorage.removeItem('lockoutTime')

          const user = result.user || authStore.user || result.data?.user || result.data

          if (user && (user.role === 'admin' || user.is_superuser)) {
            this.successMessage = 'Авторизация успешна! Перенаправление...'

            setTimeout(() => {
              this.$router.push('/admin/dashboard')
            }, 1500)
          } else {
            await authStore.logout()
            this.errorMessage = 'У вас нет прав доступа к админ панели'
            this.handleFailedLogin()
          }
        } else {
          this.handleFailedLogin()
          this.errorMessage = result?.error || result?.message || 'Неверный логин или пароль'
        }
      } catch (error) {
        console.error('Ошибка входа:', error)
        this.handleFailedLogin()
        this.errorMessage = 'Произошла ошибка при входе в систему'
      } finally {
        this.isLoading = false
      }
    },

    handleFailedLogin() {
      this.loginAttempts++
      localStorage.setItem('loginAttempts', this.loginAttempts.toString())

      if (this.loginAttempts >= this.maxAttempts) {
        const lockoutTime = Date.now() + this.lockoutTime
        localStorage.setItem('lockoutTime', lockoutTime.toString())
        this.errorMessage = `Слишком много неудачных попыток. Попробуйте через 15 минут.`
      } else {
        const remaining = this.maxAttempts - this.loginAttempts
        this.errorMessage += ` Осталось попыток: ${remaining}`
      }
    },

    isLockedOut() {
      const lockoutTime = localStorage.getItem('lockoutTime')
      if (lockoutTime && Date.now() < parseInt(lockoutTime)) {
        return true
      }
      return false
    },

    checkLockout() {
      const attempts = localStorage.getItem('loginAttempts')
      const lockoutTime = localStorage.getItem('lockoutTime')

      if (attempts) {
        this.loginAttempts = parseInt(attempts)
      }

      if (lockoutTime && Date.now() < parseInt(lockoutTime)) {
        const remainingTime = Math.ceil((parseInt(lockoutTime) - Date.now()) / 60000)
        this.errorMessage = `Аккаунт заблокирован. Попробуйте через ${remainingTime} минут.`
      } else if (lockoutTime) {
        localStorage.removeItem('loginAttempts')
        localStorage.removeItem('lockoutTime')
        this.loginAttempts = 0
      }
    },

    togglePassword() {
      this.showPassword = !this.showPassword
    },

    clearMessages() {
      this.errorMessage = ''
      this.successMessage = ''
    },

    // Обработка клавиши Enter
    handleKeyPress(event) {
      if (event.key === 'Enter' && !this.isLoading && this.isFormValid) {
        this.handleLogin()
      }
    }
  },

  // Очистка сообщений при изменении формы
  watch: {
    'credentials.username'() {
      this.clearMessages()
    },
    'credentials.password'() {
      this.clearMessages()
    }
  },

  // Добавляем обработчик клавиатуры
  created() {
    document.addEventListener('keydown', this.handleKeyPress)
  },

  beforeUnmount() {
    document.removeEventListener('keydown', this.handleKeyPress)
  }
}
</script>

<style scoped>
/* Main Container */
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  position: relative;
  overflow: hidden;
}

/* Background Animation */
.background-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  z-index: 0;
}

.bg-gradient {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg,
    rgba(102, 126, 234, 0.1) 0%,
    rgba(118, 75, 162, 0.1) 100%);
  animation: gradientShift 10s ease-in-out infinite alternate;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 6s ease-in-out infinite;
}

.bg-circle-1 {
  width: 200px;
  height: 200px;
  top: 20%;
  left: 10%;
  animation-delay: 0s;
}

.bg-circle-2 {
  width: 150px;
  height: 150px;
  top: 60%;
  right: 20%;
  animation-delay: 2s;
}

.bg-circle-3 {
  width: 100px;
  height: 100px;
  bottom: 20%;
  left: 60%;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(180deg); }
}

@keyframes gradientShift {
  0% { opacity: 0.5; }
  100% { opacity: 0.8; }
}

/* Login Wrapper */
.login-wrapper {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 440px;
}

/* Header Section */
.header-section {
  text-align: center;
  margin-bottom: 2rem;
}

.logo-container {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 50%;
  margin-bottom: 1.5rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.logo-icon {
  width: 40px;
  height: 40px;
  color: white;
}

.title {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  margin: 0 0 0.5rem 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.subtitle {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  font-weight: 300;
}

/* Login Card */
.login-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 2.5rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  margin-bottom: 2rem;
}

/* Messages */
.error-message, .success-message {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  font-weight: 500;
  animation: slideIn 0.3s ease-out;
}

.error-message {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.success-message {
  background: #f0fdf4;
  color: #16a34a;
  border: 1px solid #bbf7d0;
}

.error-icon, .success-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Form */
.login-form {
  width: 100%;
}

.form-fields {
  margin-bottom: 2rem;
}

.field-group {
  margin-bottom: 1.5rem;
}

.field-label {
  display: block;
  font-size: 0.9rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
  z-index: 1;
}

.input-icon svg {
  width: 20px;
  height: 20px;
}

.form-input {
  width: 100%;
  padding: 1rem 1rem 1rem 3rem;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: white;
  box-sizing: border-box;
}

.password-input {
  padding-right: 3.5rem !important;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-input:disabled {
  background: #f9fafb;
  cursor: not-allowed;
}

/* Кнопка показа/скрытия пароля */
.password-toggle {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 6px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  min-height: 32px;
  z-index: 10;
}

.password-toggle:hover {
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
}

.password-toggle:focus {
  outline: none;
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.password-toggle:active {
  transform: translateY(-50%) scale(0.95);
}

.password-toggle:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: transparent;
}

.password-toggle:disabled:hover {
  color: #9ca3af;
  background: transparent;
}

.password-toggle svg {
  width: 18px;
  height: 18px;
  transition: all 0.2s ease;
}

/* Checkbox */
.checkbox-group {
  margin-bottom: 1rem;
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
}

.checkbox-input {
  display: none;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 0.9rem;
  color: #6b7280;
  gap: 0.75rem;
}

.checkbox-custom {
  width: 20px;
  height: 20px;
  border: 2px solid #d1d5db;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.checkbox-input:checked + .checkbox-label .checkbox-custom {
  background: #667eea;
  border-color: #667eea;
}

.checkbox-icon {
  width: 12px;
  height: 12px;
  color: white;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.checkbox-input:checked + .checkbox-label .checkbox-icon {
  opacity: 1;
}

/* Submit Button */
.submit-button {
  width: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 1rem 2rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
}

.submit-button:active {
  transform: translateY(0);
}

.submit-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.button-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.button-arrow {
  width: 18px;
  height: 18px;
  transition: transform 0.2s ease;
}

.submit-button:hover .button-arrow {
  transform: translateX(4px);
}

.loading-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner-icon {
  width: 20px;
  height: 20px;
  animation: spin 1s linear infinite;
}

.spinner-circle {
  opacity: 0.25;
}

.spinner-path {
  opacity: 0.75;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Additional Links */
.additional-links {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.link {
  color: #667eea;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  transition: color 0.2s ease;
}

.link:hover {
  color: #4f46e5;
  text-decoration: underline;
}

.link-separator {
  color: #d1d5db;
}

/* Footer */
.footer {
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
}

.footer-text {
  font-size: 0.9rem;
  margin: 0 0 0.5rem 0;
}

.footer-links {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.footer-link {
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  font-size: 0.8rem;
  transition: color 0.2s ease;
}

.footer-link:hover {
  color: white;
}

.footer-separator {
  color: rgba(255, 255, 255, 0.5);
}

/* Responsive Design */
@media (max-width: 768px) {
  .login-container {
    padding: 1rem;
  }

  .login-card {
    padding: 2rem;
  }

  .title {
    font-size: 2rem;
  }

  .subtitle {
    font-size: 1rem;
  }

  .additional-links {
    flex-direction: column;
    gap: 0.5rem;
  }

  .footer-links {
    gap: 0.5rem;
  }
}

@media (max-width: 480px) {
  .login-card {
    padding: 1.5rem;
  }

  .title {
    font-size: 1.8rem;
  }

  .form-input {
    padding: 0.875rem 0.875rem 0.875rem 2.75rem;
  }

  .password-input {
    padding-right: 3rem !important;
  }

  .password-toggle {
    right: 0.75rem;
    padding: 0.4rem;
    min-width: 28px;
    min-height: 28px;
  }

  .password-toggle svg {
    width: 16px;
    height: 16px;
  }
}
</style>