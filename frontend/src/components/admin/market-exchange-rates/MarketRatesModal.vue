<template>
  <div v-if="isOpen" class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2 class="modal-title">
          {{ isEditMode ? 'Редактировать курс' : 'Добавить новый курс' }}
        </h2>
        <button @click="closeModal" class="close-button">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="modal-body">
        <div class="form-group">
          <label for="currency" class="form-label">Валюта</label>
          <input
            id="currency"
            v-model="form.currency_code"
            type="text"
            class="form-input"
            :class="{ error: errors.currency }"
            :readonly="isEditMode"
            placeholder="Код валюты"
            required
          />
          <span v-if="errors.currency" class="error-message">{{ errors.currency }}</span>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="buyRate" class="form-label">Курс покупки</label>
            <input
              id="buyRate"
              v-model="form.buyRate"
              type="number"
              step="0.0001"
              class="form-input"
              :class="{ error: errors.buyRate }"
              placeholder="0.0000"
              required
            />
            <span v-if="errors.buyRate" class="error-message">{{ errors.buyRate }}</span>
          </div>

          <div class="form-group">
            <label for="sellRate" class="form-label">Курс продажи</label>
            <input
              id="sellRate"
              v-model="form.sellRate"
              type="number"
              step="0.0001"
              class="form-input"
              :class="{ error: errors.sellRate }"
              placeholder="0.0000"
              required
            />
            <span v-if="errors.sellRate" class="error-message">{{ errors.sellRate }}</span>
          </div>
        </div>

        <div class="form-group">
          <label for="status" class="form-label">Статус</label>
          <select
            id="status"
            v-model="form.status"
            class="form-select"
            :class="{ error: errors.status }"
            required
          >
            <option value="active">Активный</option>
            <option value="inactive">Неактивный</option>
          </select>
          <span v-if="errors.status" class="error-message">{{ errors.status }}</span>
        </div>

        <div class="form-group">
          <label for="notes" class="form-label">Примечания</label>
          <textarea
            id="notes"
            v-model="form.notes"
            class="form-textarea"
            rows="3"
            placeholder="Дополнительная информация..."
          ></textarea>
        </div>

        <div class="modal-footer">
          <button type="button" @click="closeModal" class="btn btn-secondary">
            Отмена
          </button>
          <button type="submit" class="btn btn-primary" :disabled="loading">
            <span v-if="loading" class="loading-spinner"></span>
            {{ isEditMode ? 'Сохранить изменения' : 'Создать' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MarketRatesModal',
  props: {
    isOpen: {
      type: Boolean,
      default: false
    },
    rateData: {
      type: Object,
      default: null
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      form: {
        currency_code: '',
        currency_id: null, // ID валюты для API
        buyRate: '',
        sellRate: '',
        status: 'active',
        notes: ''
      },
      errors: {}
    }
  },
  computed: {
    isEditMode() {
      return this.rateData && this.rateData.id
    }
  },
  watch: {
    isOpen(newVal) {
      if (newVal) {
        this.initForm()
      }
    },
    rateData: {
      handler(newVal) {
        if (this.isOpen && newVal) {
          this.fillForm(newVal)
        }
      },
      deep: true,
      immediate: true
    }
  },
  methods: {
    initForm() {
      if (this.isEditMode && this.rateData) {
        this.fillForm(this.rateData)
      } else {
        this.resetForm()
      }
    },

    fillForm(data) {
      console.log('🔄 Заполнение формы данными:', data)

      this.form = {
        currency_code: data.currency_code || '',
        currency_id: data.currency || null, // ID валюты для API
        buyRate: data.buy || '',
        sellRate: data.sell || '',
        status: data.is_active ? 'active' : 'inactive',
        notes: data.notes || ''
      }

      this.errors = {}

      this.$nextTick(() => {
        console.log('✅ Форма заполнена:', this.form)
        console.log('🆔 ID курса:', data.id)
        console.log('💱 ID валюты:', data.currency)
      })
    },

    resetForm() {
      this.form = {
        currency_code: '',
        currency_id: null,
        buyRate: '',
        sellRate: '',
        status: 'active',
        notes: ''
      }
      this.errors = {}
    },

    validateForm() {
      this.errors = {}

      if (!this.form.currency_code) {
        this.errors.currency = 'Введите код валюты'
      }

      if (!this.form.buyRate || parseFloat(this.form.buyRate) <= 0) {
        this.errors.buyRate = 'Введите корректный курс покупки'
      }

      if (!this.form.sellRate || parseFloat(this.form.sellRate) <= 0) {
        this.errors.sellRate = 'Введите корректный курс продажи'
      }

      if (this.form.buyRate && this.form.sellRate) {
        if (parseFloat(this.form.buyRate) >= parseFloat(this.form.sellRate)) {
          this.errors.sellRate = 'Курс продажи должен быть больше курса покупки'
        }
      }

      return Object.keys(this.errors).length === 0
    },

    handleSubmit() {
      if (!this.validateForm()) return

      if (this.isEditMode) {
        // Редактирование - отправляем только необходимые поля без city_name
        const updateData = {
          id: this.rateData.id,
          currency: this.form.currency_id, // Используем ID валюты
          buy: parseFloat(this.form.buyRate),
          sell: parseFloat(this.form.sellRate),
          is_active: this.form.status === 'active',
          notes: this.form.notes || ''
        }

        console.log('📤 Отправляем на обновление:', updateData)
        this.$emit('update-rate', updateData)
      } else {
        // Создание нового курса
        const formData = {
          currency_code: this.form.currency_code,
          buy: parseFloat(this.form.buyRate),
          sell: parseFloat(this.form.sellRate),
          is_active: this.form.status === 'active',
          notes: this.form.notes || ''
        }

        console.log('📤 Отправляем на создание:', formData)
        this.$emit('create-rate', formData)
      }
    },

    closeModal() {
      this.resetForm()
      this.$emit('close')
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #eee;
}

.modal-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #333;
}

.close-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.close-button:hover {
  background-color: #f3f4f6;
}

.close-button svg {
  width: 1.5rem;
  height: 1.5rem;
}

.modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
}

.form-input, .form-select, .form-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-input:focus, .form-select:focus, .form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input.error, .form-select.error, .form-textarea.error {
  border-color: #ef4444;
}

.form-input:read-only {
  background-color: #f9fafb;
  color: #6b7280;
}

.error-message {
  color: #ef4444;
  font-size: 0.75rem;
  margin-top: 0.25rem;
  display: block;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-secondary {
  background-color: #6b7280;
  color: white;
}

.btn-secondary:hover {
  background-color: #4b5563;
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 640px) {
  .form-row {
    grid-template-columns: 1fr;
  }

  .modal-content {
    width: 95%;
    margin: 1rem;
  }
}
</style>