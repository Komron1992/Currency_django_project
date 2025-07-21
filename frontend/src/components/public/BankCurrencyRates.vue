<!-- frontend/src/components/public/BankCurrencyRates.vue -->
<template>
  <div class="bank-currency-rates">
    <h2>Курсы валют по банкам</h2>

    <!-- Состояние загрузки -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Загрузка курсов банков...</p>
    </div>

    <!-- Ошибка -->
    <div v-else-if="error" class="error-state">
      <svg class="error-icon" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
        <path d="M12 9v4"/>
        <path d="m12 17 .01 0"/>
      </svg>
      <p>{{ error }}</p>
      <button @click="loadBankRates" class="retry-btn">Повторить</button>
    </div>

    <!-- Нет данных -->
    <div v-else-if="groupedBanks.length === 0" class="empty-state">
      <svg class="empty-icon" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <ellipse cx="12" cy="5" rx="9" ry="3"/>
        <path d="M3 5v14c0 3 4.5 4 9 4s9-1 9-4V5"/>
        <path d="M3 12c0 3 4.5 4 9 4s9-1 9-4"/>
      </svg>
      <p>Нет данных о курсах банков</p>
      <button @click="loadBankRates" class="retry-btn">Загрузить</button>
    </div>

    <!-- Список банков -->
    <div v-else class="banks-grid">
      <div v-for="bank in groupedBanks" :key="bank.id" class="bank-card">
        <!-- Логотип банка -->
        <div class="bank-logo">
          <div class="logo-placeholder">
            <img
              v-if="getBankLogo(bank.name)"
              :src="getBankLogo(bank.name)"
              :alt="bank.name"
              class="bank-logo-img"
              @error="onImageError"
            />
            <svg
              v-else
              class="bank-icon"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
              <polyline points="9,22 9,12 15,12 15,22"/>
            </svg>
          </div>
        </div>

        <!-- Название банка -->
        <h3 class="bank-name">{{ bank.name }}</h3>

        <!-- Курсы валют -->
        <div class="rates-table">
          <div class="table-header">
            <span class="header-cell">Валюта</span>
            <span class="header-cell">Покупка</span>
            <span class="header-cell">Продажа</span>
          </div>

          <div v-if="bank.rates && bank.rates.length > 0" class="table-body">
            <div v-for="rate in bank.rates" :key="rate.id" class="rate-row">
              <span class="currency-cell">{{ rate.currency_code }}</span>
              <span class="buy-cell">{{ formatRate(rate.buy) }}</span>
              <span class="sell-cell">{{ formatRate(rate.sell) }}</span>
            </div>
          </div>

          <div v-else class="no-rates">
            <span>Нет доступных курсов</span>
          </div>
        </div>

        <!-- Дополнительная информация -->
        <div class="bank-info">
          <small class="currencies-info">
            Валюты: {{ getCurrencyIds(bank.rates) }}
          </small>
          <small class="update-time" v-if="bank.rates && bank.rates.length > 0">
            Обновлено: {{ formatDate(bank.rates[0].date, bank.rates[0].time) }}
          </small>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import '@/assets/styles/components/public/BankCurrencyRates.css'
import { onMounted, computed } from 'vue'
import { useRatesStore } from '@/stores/rates'
import { getBankLogo } from '@/utils/bankLogos'

const ratesStore = useRatesStore()

const loading = computed(() => ratesStore.loading)
const error = computed(() => ratesStore.error)

// Валюты, которые нужны
const neededCurrencies = ['USD', 'RUB', 'EUR']

const groupedBanks = computed(() => {
  const bankRates = ratesStore.bankRates || []
  if (!Array.isArray(bankRates) || bankRates.length === 0) return []

  // Группируем курсы по банкам
  const banksMap = new Map()

  bankRates.forEach(rate => {
    const bankId = rate.bank
    const bankName = rate.bank_name

    if (!banksMap.has(bankId)) {
      banksMap.set(bankId, {
        id: bankId,
        name: bankName,
        rates: []
      })
    }
    banksMap.get(bankId).rates.push(rate)
  })

  // Для каждого банка фильтруем курсы, оставляя только последние по валютам USD, RUB, EUR
  const result = []
  for (const bank of banksMap.values()) {
    // Для нужных валют берем самый последний курс (по дате и времени)
    const filteredRates = []

    neededCurrencies.forEach(curr => {
      // Отфильтровать курсы с нужной валютой
      const filteredByCurrency = bank.rates.filter(r => r.currency_code === curr)

      if (filteredByCurrency.length > 0) {
        // Найти последний по дате и времени
        filteredByCurrency.sort((a, b) => {
          const dateA = new Date(a.date + 'T' + a.time)
          const dateB = new Date(b.date + 'T' + b.time)
          return dateB - dateA
        })

        filteredRates.push(filteredByCurrency[0]) // самый последний
      }
    })

    // Отсортировать валюты в нужном порядке USD, EUR, RUB
    filteredRates.sort((a, b) => neededCurrencies.indexOf(a.currency_code) - neededCurrencies.indexOf(b.currency_code))

    result.push({
      id: bank.id,
      name: bank.name,
      rates: filteredRates
    })
  }

  return result
})

async function loadBankRates() {
  await ratesStore.fetchBankRates()
}

onMounted(() => {
  loadBankRates()
})

function getCurrencyIds(ratesArray) {
  if (!ratesArray || !Array.isArray(ratesArray)) {
    return 'Нет данных'
  }
  return ratesArray
    .map(rateObj => rateObj.currency_code)
    .filter((val, idx, self) => self.indexOf(val) === idx)
    .join(', ') || 'Нет валют'
}

function formatRate(rate) {
  if (!rate || rate === '' || rate === null || rate === undefined) return '-'

  if (typeof rate === 'string') {
    rate = rate.replace(',', '.')
    const numRate = parseFloat(rate)
    if (isNaN(numRate)) return rate
    return numRate.toFixed(4)
  }

  if (typeof rate === 'number') {
    if (isNaN(rate)) return '-'
    return rate.toFixed(4)
  }

  return rate.toString()
}

function formatDate(dateString, timeString) {
  if (!dateString) return ''

  try {
    const date = new Date(dateString + (timeString ? 'T' + timeString : ''))
    return date.toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return dateString + (timeString ? ' ' + timeString.slice(0, 5) : '')
  }
}

function onImageError(event) {
  console.warn('Не удалось загрузить логотип банка:', event.target.src)
}
</script>
