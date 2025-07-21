<template>
  <div class="market-rates-list">
    <div class="list-header">
      <h3>Рыночные курсы валют</h3>
      <div class="header-actions">
        <button @click="$emit('refresh')" class="btn-refresh" :disabled="loading">
          {{ loading ? 'Загрузка...' : 'Обновить' }}
        </button>
      </div>
    </div>

    <!-- Состояние загрузки -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Загрузка курсов...</p>
    </div>

    <!-- Ошибка -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <p>{{ error }}</p>
      <button @click="$emit('refresh')" class="btn-retry">Попробовать снова</button>
    </div>

    <!-- Пустой список -->
    <div v-else-if="!rates || rates.length === 0" class="empty-state">
      <div class="empty-icon">📊</div>
      <p>Нет данных о курсах валют</p>
      <button @click="$emit('refresh')" class="btn-refresh">Загрузить данные</button>
    </div>

    <!-- Таблица курсов -->
    <div v-else class="rates-table">
      <table>
        <thead>
          <tr>
            <th>Валюта</th>
            <th>Город</th>
            <th>Покупка</th>
            <th>Продажа</th>
            <th>Дата</th>
            <th>Время</th>
            <th>Добавил</th>
            <th>Статус</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="rate in rates" :key="rate.id" :class="{ inactive: !rate.is_active }">
            <td>
              <div class="currency-cell">
                <span class="currency-code">{{ rate.currency_code }}</span>
                <small class="currency-name">{{ getCurrencyName(rate.currency_code) }}</small>
              </div>
            </td>
            <td>{{ rate.city_name }}</td>
            <td class="price-cell buy">{{ formatPrice(rate.buy) }}</td>
            <td class="price-cell sell">{{ formatPrice(rate.sell) }}</td>
            <td>{{ formatDate(rate.date) }}</td>
            <td>{{ rate.time }}</td>
            <td>{{ rate.added_by_name }}</td>
            <td>
              <span :class="['status-badge', { active: rate.is_active, inactive: !rate.is_active }]">
                {{ rate.is_active ? 'Активный' : 'Неактивный' }}
              </span>
            </td>
            <td>
              <div class="action-buttons">
                <button @click="handleEdit(rate)" class="btn-edit" title="Редактировать">✏️</button>
                <button @click="$emit('delete', rate.id)" class="btn-delete" title="Удалить">🗑️</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MarketRatesList',
  props: {
    rates: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    error: {
      type: String,
      default: null
    },
    cities: {
      type: Array,
      default: () => []
    }
  },
  emits: ['edit', 'delete', 'refresh'],
  methods: {
    getCurrencyName(code) {
      const currencies = {
        'USD': 'Доллар США',
        'EUR': 'Евро',
        'RUB': 'Российский рубль',
        'CNY': 'Китайский юань',
        'GBP': 'Фунт стерлингов',
        'JPY': 'Японская иена',
        'CHF': 'Швейцарский франк',
        'CAD': 'Канадский доллар',
        'AUD': 'Австралийский доллар'
      }
      return currencies[code] || code
    },

    formatPrice(price) {
      if (!price) return '—'
      return parseFloat(price).toFixed(4)
    },

    formatDate(dateString) {
      if (!dateString) return '—'
      const date = new Date(dateString)
      return date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      })
    },

    handleEdit(rate) {
      this.$emit('edit', rate)
    }
  }
}
</script>

<style scoped>
.market-rates-list {
  padding: 1rem;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.list-header h3 {
  margin: 0;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-refresh, .btn-retry {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s;
}

.btn-refresh {
  background-color: #007bff;
  color: white;
}

.btn-refresh:hover {
  background-color: #0056b3;
}

.btn-refresh:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.btn-retry {
  background-color: #dc3545;
  color: white;
}

.btn-retry:hover {
  background-color: #c82333;
}

/* Состояния загрузки и ошибок */
.loading-state, .error-state, .empty-state {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon, .empty-icon {
  font-size: 2rem;
  margin-bottom: 1rem;
}

/* Таблица */
.rates-table {
  overflow-x: auto;
  margin-top: 1rem;
}

.rates-table table {
  width: 100%;
  border-collapse: collapse;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.rates-table th,
.rates-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.rates-table th {
  background-color: #f8f9fa;
  font-weight: bold;
  color: #333;
}

.rates-table tr:hover {
  background-color: #f8f9fa;
}

.rates-table tr.inactive {
  opacity: 0.6;
}

.currency-cell {
  display: flex;
  flex-direction: column;
}

.currency-cell .currency-code {
  font-weight: bold;
  color: #007bff;
}

.currency-cell .currency-name {
  font-size: 0.8rem;
  color: #666;
}

.price-cell {
  font-weight: bold;
  text-align: right;
}

.price-cell.buy {
  color: #28a745;
}

.price-cell.sell {
  color: #dc3545;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
}

.status-badge.active {
  background-color: #d4edda;
  color: #155724;
}

.status-badge.inactive {
  background-color: #f8d7da;
  color: #721c24;
}

.action-buttons {
  display: flex;
  gap: 0.25rem;
}

.btn-edit, .btn-delete {
  padding: 0.25rem 0.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: background-color 0.2s;
}

.btn-edit {
  background-color: #ffc107;
  color: black;
}

.btn-edit:hover {
  background-color: #e0a800;
}

.btn-delete {
  background-color: #dc3545;
  color: white;
}

.btn-delete:hover {
  background-color: #c82333;
}

/* Адаптивность */
@media (max-width: 768px) {
  .rates-table {
    font-size: 0.9rem;
  }
}
</style>