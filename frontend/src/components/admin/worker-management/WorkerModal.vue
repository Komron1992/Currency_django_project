<template>
  <div v-if="isVisible" class="worker-modal-overlay" @click="handleOverlayClick">
    <div class="worker-modal" @click.stop>
      <div class="modal-header">
        <h3>{{ isEditing ? 'Редактирование работника' : 'Добавление работника' }}</h3>
        <button @click="$emit('close')" class="close-btn">✕</button>
      </div>

      <form @submit.prevent="handleSubmit" class="modal-body">
        <!-- Отображение ошибок -->
        <div v-if="errors.length > 0" class="error-messages">
          <div v-for="error in errors" :key="error" class="error-message">
            {{ error }}
          </div>
        </div>

        <!-- Основная информация -->
        <div class="form-section">
          <h4>Основная информация</h4>

          <div class="form-group">
            <label for="username">Имя пользователя *</label>
            <input
              id="username"
              v-model="formData.username"
              type="text"
              required
              placeholder="Введите имя пользователя"
              :class="{ 'error': formErrors.username }"
              @blur="validateUsername"
            />
            <small v-if="formErrors.username" class="error-text">{{ formErrors.username }}</small>
          </div>

          <div class="form-group">
            <label for="email">Email *</label>
            <input
              id="email"
              v-model="formData.email"
              type="email"
              required
              placeholder="example@mail.com"
              :class="{ 'error': formErrors.email }"
              @blur="validateEmail"
            />
            <small v-if="formErrors.email" class="error-text">{{ formErrors.email }}</small>
          </div>

          <div class="form-group">
            <label for="first_name">Имя</label>
            <input
              id="first_name"
              v-model="formData.first_name"
              type="text"
              placeholder="Введите имя"
              :class="{ 'error': formErrors.first_name }"
              @blur="validateFirstName"
            />
            <small v-if="formErrors.first_name" class="error-text">{{ formErrors.first_name }}</small>
          </div>

          <div class="form-group">
            <label for="last_name">Фамилия</label>
            <input
              id="last_name"
              v-model="formData.last_name"
              type="text"
              placeholder="Введите фамилию"
              :class="{ 'error': formErrors.last_name }"
              @blur="validateLastName"
            />
            <small v-if="formErrors.last_name" class="error-text">{{ formErrors.last_name }}</small>
          </div>

          <div class="form-group">
            <label for="phone">Телефон</label>
            <input
              id="phone"
              v-model="formData.phone"
              type="tel"
              placeholder="Введите телефон (например: +992123456789)"
              :class="{ 'error': formErrors.phone }"
              @input="handlePhoneInput"
              @blur="validatePhone"
              maxlength="15"
            />
            <small class="form-help">Формат: +992123456789 или 985010922</small>
            <small v-if="formErrors.phone" class="error-text">{{ formErrors.phone }}</small>
          </div>

          <div v-if="!isEditing" class="form-group">
            <label for="password">Пароль *</label>
            <input
              id="password"
              v-model="formData.password"
              type="password"
              required
              placeholder="Введите пароль"
              minlength="8"
              :class="{ 'error': formErrors.password }"
              @blur="validatePassword"
            />
            <small class="form-help">Минимум 8 символов</small>
            <small v-if="formErrors.password" class="error-text">{{ formErrors.password }}</small>
          </div>

          <div v-if="!isEditing" class="form-group">
            <label for="password_confirm">Подтверждение пароля *</label>
            <input
              id="password_confirm"
              v-model="formData.password_confirm"
              type="password"
              required
              placeholder="Повторите пароль"
              minlength="8"
              :class="{ 'error': passwordMismatch }"
              @blur="validatePasswordConfirm"
            />
            <small v-if="passwordMismatch" class="error-text">Пароли не совпадают</small>
          </div>
        </div>

        <!-- Рабочая информация -->
        <div class="form-section">
          <h4>Рабочая информация</h4>

          <div class="form-group">
            <label for="city_name">Город *</label>
            <select
              id="city_name"
              v-model="formData.city_name"
              required
              :class="{ 'error': formErrors.city_name }"
              @change="validateCity"
            >
              <option value="">Выберите город</option>
              <option
                v-for="city in cities"
                :key="city.id || city.name"
                :value="city.name"
              >
                {{ city.name }}
              </option>
            </select>
            <small v-if="formErrors.city_name" class="error-text">{{ formErrors.city_name }}</small>
          </div>

          <div class="form-group">
            <label class="checkbox-label">
              <input
                type="checkbox"
                v-model="formData.is_worker_active"
              />
              Активный работник
            </label>
          </div>
        </div>

        <!-- Кнопки -->
        <div class="modal-footer">
          <button type="button" @click="$emit('close')" class="btn btn-secondary">
            Отмена
          </button>
          <button
            type="submit"
            class="btn btn-primary"
            :disabled="loading || !isFormValid"
          >
            <span v-if="loading">⏳ Сохранение...</span>
            <span v-else>{{ isEditing ? 'Обновить' : 'Создать' }}</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import '@/assets/styles/components/admin/worker-management/WorkerModal.css'
import { ref, computed, watch, inject, nextTick } from 'vue'
import { adminAPI } from '@/services/api.js'

export default {
  name: 'WorkerModal',
  props: {
    isVisible: {
      type: Boolean,
      default: false
    },
    worker: {
      type: Object,
      default: null
    },
    cities: {
      type: Array,
      default: () => []
    },
    isEditing: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'worker-saved'],
  setup(props, { emit }) {
    const loading = ref(false)
    const errors = ref([])
    const formErrors = ref({})

    // Inject сервисы с fallback
    const $services = inject('$services', null)

    // Данные формы - используем reactive объект для лучшей реактивности
    const formData = ref({
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      phone: '',
      password: '',
      password_confirm: '',
      city_name: '',
      is_worker_active: true
    })

    // Создаем локальный сервис администрирования
    const getAdminService = () => {
      if ($services && $services.admin) {
        return $services.admin
      }
      return adminAPI
    }

    // Улучшенная нормализация телефона
    const normalizePhone = (phone) => {
      if (!phone) return ''

      // Убираем все символы кроме цифр и знака +
      let cleanPhone = phone.replace(/[^\d+]/g, '')

      console.log('📱 Нормализация телефона:', phone, '→', cleanPhone)

      // Если номер начинается с 0, заменяем на +992
      if (cleanPhone.startsWith('0')) {
        cleanPhone = '+992' + cleanPhone.substring(1)
      }
      // Если номер начинается с 992, но без +, добавляем +
      else if (cleanPhone.startsWith('992') && !cleanPhone.startsWith('+992')) {
        cleanPhone = '+' + cleanPhone
      }
      // Если номер из 9 цифр, добавляем +992
      else if (/^\d{9}$/.test(cleanPhone)) {
        cleanPhone = '+992' + cleanPhone
      }
      // Если уже есть +992, оставляем как есть
      else if (cleanPhone.startsWith('+992')) {
        // Проверяем, что после +992 идет ровно 9 цифр
        const numberPart = cleanPhone.substring(4)
        if (numberPart.length === 9 && /^\d{9}$/.test(numberPart)) {
          cleanPhone = '+992' + numberPart
        }
      }

      console.log('📱 Результат нормализации:', cleanPhone)
      return cleanPhone
    }

    // Обработчик ввода телефона
    const handlePhoneInput = (event) => {
      const value = event.target.value
      console.log('📱 Ввод телефона:', value)

      // Позволяем пользователю вводить телефон в любом формате
      formData.value.phone = value

      // Очищаем ошибки при вводе
      if (formErrors.value.phone) {
        delete formErrors.value.phone
      }
    }

    // Методы валидации
    const validateUsername = () => {
      const username = formData.value.username?.trim() || ''
      if (!username) {
        formErrors.value.username = 'Имя пользователя обязательно'
        return false
      }
      if (username.length < 3) {
        formErrors.value.username = 'Имя пользователя должно содержать минимум 3 символа'
        return false
      }
      if (!/^[a-zA-Z0-9_]+$/.test(username)) {
        formErrors.value.username = 'Имя пользователя может содержать только буквы, цифры и знак подчеркивания'
        return false
      }
      delete formErrors.value.username
      return true
    }

    const validateEmail = () => {
      const email = formData.value.email?.trim() || ''
      if (!email) {
        formErrors.value.email = 'Email обязателен'
        return false
      }
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(email)) {
        formErrors.value.email = 'Неверный формат email'
        return false
      }
      delete formErrors.value.email
      return true
    }

    const validateFirstName = () => {
      const firstName = formData.value.first_name?.trim() || ''
      if (firstName && firstName.length < 2) {
        formErrors.value.first_name = 'Имя должно содержать минимум 2 символа'
        return false
      }
      delete formErrors.value.first_name
      return true
    }

    const validateLastName = () => {
      const lastName = formData.value.last_name?.trim() || ''
      if (lastName && lastName.length < 2) {
        formErrors.value.last_name = 'Фамилия должна содержать минимум 2 символа'
        return false
      }
      delete formErrors.value.last_name
      return true
    }

    const validatePhone = () => {
      const phone = formData.value.phone?.trim() || ''
      console.log('📱 Валидация телефона:', phone)

      if (!phone) {
        delete formErrors.value.phone
        return true
      }

      // Нормализуем телефон для проверки
      const normalizedPhone = normalizePhone(phone)

      // Проверяем формат +992XXXXXXXXX (всего 13 символов)
      const phoneRegex = /^\+992\d{9}$/

      if (!phoneRegex.test(normalizedPhone)) {
        formErrors.value.phone = 'Неверный формат телефона. Используйте формат: +992123456789 или 985010922'
        return false
      }

      delete formErrors.value.phone
      return true
    }

    const validatePassword = () => {
      const password = formData.value.password || ''
      if (!props.isEditing && !password) {
        formErrors.value.password = 'Пароль обязателен'
        return false
      }
      if (!props.isEditing && password.length < 8) {
        formErrors.value.password = 'Пароль должен содержать минимум 8 символов'
        return false
      }
      delete formErrors.value.password
      return true
    }

    const validatePasswordConfirm = () => {
      if (!props.isEditing && formData.value.password !== formData.value.password_confirm) {
        formErrors.value.password_confirm = 'Пароли не совпадают'
        return false
      }
      delete formErrors.value.password_confirm
      return true
    }

    const validateCity = () => {
      if (!formData.value.city_name) {
        formErrors.value.city_name = 'Выберите город'
        return false
      }
      delete formErrors.value.city_name
      return true
    }

    // Валидация всей формы
    const validateForm = () => {
      let isValid = true

      isValid = validateUsername() && isValid
      isValid = validateEmail() && isValid
      isValid = validateFirstName() && isValid
      isValid = validateLastName() && isValid
      isValid = validatePhone() && isValid
      isValid = validateCity() && isValid

      if (!props.isEditing) {
        isValid = validatePassword() && isValid
        isValid = validatePasswordConfirm() && isValid
      }

      return isValid
    }

    // Валидация пароля
    const passwordMismatch = computed(() => {
      return !props.isEditing &&
             formData.value.password &&
             formData.value.password_confirm &&
             formData.value.password !== formData.value.password_confirm
    })

    // Проверка валидности формы
    const isFormValid = computed(() => {
      const basic = formData.value.username?.trim() &&
                   formData.value.email?.trim() &&
                   formData.value.city_name &&
                   Object.keys(formErrors.value).length === 0

      if (props.isEditing) {
        return basic
      } else {
        return basic &&
               formData.value.password &&
               formData.value.password_confirm &&
               formData.value.password.length >= 8 &&
               !passwordMismatch.value
      }
    })

    // Очистка формы
    const resetForm = () => {
      console.log('🔄 Сброс формы')
      formData.value = {
        username: '',
        email: '',
        first_name: '',
        last_name: '',
        phone: '',
        password: '',
        password_confirm: '',
        city_name: '',
        is_worker_active: true
      }

      errors.value = []
      formErrors.value = {}
    }

    // Исправленная функция заполнения формы
    const fillFormData = (worker) => {
      console.log('🔄 Заполняем форму данными работника:', worker)

      if (!worker) {
        console.log('⚠️ Нет данных работника для заполнения')
        return
      }

      // Используем Object.assign для правильного обновления реактивных данных
      Object.assign(formData.value, {
        username: worker.username || '',
        email: worker.email || '',
        first_name: worker.first_name || '',
        last_name: worker.last_name || '',
        phone: worker.phone || '', // Здесь телефон передается как есть
        password: '',
        password_confirm: '',
        city_name: worker.city_name || '',
        is_worker_active: worker.is_worker_active !== undefined ? worker.is_worker_active : true
      })

      console.log('📋 Данные формы после заполнения:', formData.value)
      console.log('📱 Телефон в форме:', formData.value.phone)

      // Очищаем ошибки
      errors.value = []
      formErrors.value = {}
    }

    // Нормализация данных перед отправкой
    const normalizeFormData = () => {
      const data = {
        username: formData.value.username?.trim() || '',
        email: formData.value.email?.trim() || '',
        first_name: formData.value.first_name?.trim() || '',
        last_name: formData.value.last_name?.trim() || '',
        city_name: formData.value.city_name || '',
        is_worker_active: Boolean(formData.value.is_worker_active)
      }

      // Обработка телефона
      const phone = formData.value.phone?.trim() || ''
      if (phone) {
        data.phone = normalizePhone(phone)
      } else {
        data.phone = ''
      }

      // Добавляем пароли только при создании
      if (!props.isEditing) {
        data.password = formData.value.password || ''
        data.password_confirm = formData.value.password_confirm || ''
      }

      console.log('📤 Нормализованные данные для отправки:', data)
      return data
    }

    // Отслеживание изменений worker с улучшенной логикой
    watch(() => [props.worker, props.isEditing, props.isVisible], async ([newWorker, isEditing, isVisible]) => {
      if (isVisible && newWorker && isEditing) {
        console.log('👁️ Обновление формы для редактирования работника')
        console.log('📱 Телефон работника:', newWorker.phone)
        await nextTick()
        fillFormData(newWorker)
      } else if (isVisible && !isEditing) {
        console.log('👁️ Сброс формы для добавления работника')
        await nextTick()
        resetForm()
      }
    }, { immediate: true, deep: true })

    // Методы
    const handleOverlayClick = () => {
      emit('close')
    }

    // Основной метод отправки формы с улучшенной обработкой ошибок
    const handleSubmit = async () => {
      console.log('🚀 Начинаем отправку формы')
      console.log('📝 Режим редактирования:', props.isEditing)
      console.log('📋 Исходные данные формы:', formData.value)

      if (!validateForm() || !isFormValid.value) {
        console.log('❌ Валидация не пройдена')
        console.log('🔍 Ошибки валидации:', formErrors.value)
        return
      }

      loading.value = true
      errors.value = []

      try {
        const dataToSend = normalizeFormData()
        console.log('📤 Данные для отправки:', dataToSend)

        const adminService = getAdminService()
        console.log('🔧 Используемый сервис:', adminService)

        if (!adminService) {
          throw new Error('Сервис администрирования не доступен')
        }

        let response
        if (props.isEditing) {
          console.log('🔄 Обновляем работника с ID:', props.worker.id)
          if (!adminService.updateWorker) {
            throw new Error('Метод updateWorker не найден в сервисе')
          }
          response = await adminService.updateWorker(props.worker.id, dataToSend)
        } else {
          console.log('➕ Создаем нового работника')
          if (!adminService.createWorker) {
            throw new Error('Метод createWorker не найден в сервисе')
          }
          console.log('🔍 Вызываем adminService.createWorker с данными:', dataToSend)
          response = await adminService.createWorker(dataToSend)
        }

        console.log('✅ Успешный ответ от сервера:', response)

        // Эмитим событие с результатом
        emit('worker-saved', response.data || response)

        // Сбрасываем форму и закрываем модальное окно
        resetForm()

      } catch (error) {
        console.error('❌ Полная информация об ошибке:', {
          message: error.message,
          stack: error.stack,
          response: error.response,
          request: error.request,
          config: error.config,
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data
        })

        setErrors(error)
      } finally {
        loading.value = false
      }
    }

    // Улучшенный метод для установки ошибок с бэкенда
    const setErrors = (error) => {
      console.log('🔍 Обработка ошибки:', error)

      // Очищаем предыдущие ошибки
      errors.value = []
      formErrors.value = {}

      // Если есть ответ от сервера
      if (error.response) {
        const { status, data } = error.response
        console.log('🔍 Ответ сервера:', { status, data })

        // Обработка различных статусов ошибок
        switch (status) {
          case 400:
            // Ошибки валидации
            if (typeof data === 'object' && data !== null) {
              // Если data - это объект с полями ошибок
              if (data.errors) {
                // Формат: { errors: { field: [messages] } }
                Object.entries(data.errors).forEach(([field, messages]) => {
                  const messageArray = Array.isArray(messages) ? messages : [messages]
                  formErrors.value[field] = messageArray.join(', ')
                })
                errors.value = ['Пожалуйста, исправьте ошибки в форме']
              } else {
                // Формат: { field: [messages] }
                Object.entries(data).forEach(([field, messages]) => {
                  if (Array.isArray(messages)) {
                    formErrors.value[field] = messages.join(', ')
                  } else if (typeof messages === 'string') {
                    formErrors.value[field] = messages
                  }
                })
                errors.value = ['Пожалуйста, исправьте ошибки в форме']
              }
            } else {
              errors.value = [data || 'Ошибка валидации данных']
            }
            break

          case 401:
            errors.value = ['Ошибка авторизации. Пожалуйста, войдите в систему']
            break

          case 403:
            errors.value = ['У вас нет прав для выполнения этого действия']
            break

          case 404:
            errors.value = ['Ресурс не найден']
            break

          case 409:
            errors.value = ['Конфликт данных. Возможно, пользователь с таким именем или email уже существует']
            break

          case 422:
            // Ошибки валидации Laravel
            if (data && data.errors) {
              Object.entries(data.errors).forEach(([field, messages]) => {
                formErrors.value[field] = Array.isArray(messages) ? messages.join(', ') : messages
              })
              errors.value = ['Пожалуйста, исправьте ошибки в форме']
            } else {
              errors.value = [data?.message || 'Ошибка валидации данных']
            }
            break

          case 500:
            errors.value = ['Внутренняя ошибка сервера. Пожалуйста, попробуйте позже']
            break

          default:
            errors.value = [data?.message || `Ошибка сервера (${status})`]
        }
      } else if (error.request) {
        // Ошибка сети
        console.log('🔍 Ошибка сети:', error.request)
        errors.value = ['Ошибка сети. Проверьте подключение к интернету']
      } else {
        // Другие ошибки
        console.log('🔍 Другая ошибка:', error.message)
        errors.value = [error.message || 'Неизвестная ошибка']
      }

      console.log('📋 Установленные ошибки:', errors.value)
      console.log('📋 Ошибки полей:', formErrors.value)
    }

    return {
      loading,
      errors,
      formErrors,
      formData,
      passwordMismatch,
      isFormValid,
      handleOverlayClick,
      handleSubmit,
      handlePhoneInput,
      validatePhone,
      validateUsername,
      validateEmail,
      validateFirstName,
      validateLastName,
      validatePassword,
      validatePasswordConfirm,
      validateCity,
      resetForm,
      normalizePhone
    }
  }
}
</script>