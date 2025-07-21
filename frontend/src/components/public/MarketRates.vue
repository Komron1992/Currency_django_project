<template>
  <div id="market-rates-container" class="market-exchange-rates">
    <h2 class="mr-title">Рыночные курсы валют по городам</h2>

    <div v-if="loading" class="mr-loading-state">
      <div class="mr-loading-spinner"></div>
      <p>Загрузка курсов валют...</p>
    </div>

    <div v-else-if="error" class="mr-error-state">
      <div class="error-icon">⚠️</div>
      <p>{{ error }}</p>
      <button @click="loadMarketRates" class="mr-retry-btn">Повторить</button>
    </div>

    <div v-else-if="groupedCities.length === 0" class="mr-empty-state">
      <p>Нет данных о рыночных курсах</p>
      <button @click="loadMarketRates" class="mr-retry-btn">Загрузить</button>
    </div>

    <div v-else class="mr-cities-grid">
      <div v-for="city in groupedCities" :key="city.name" class="mr-city-card">
        <div class="mr-city-header">
          <h3 class="mr-city-name">{{ city.name }}</h3>
        </div>

        <div class="mr-rates-table">
          <div class="mr-table-header">
            <span class="mr-header-cell">ВАЛЮТА</span>
            <span class="mr-header-cell">ПОКУПКА</span>
            <span class="mr-header-cell">ПРОДАЖА</span>
          </div>

          <div class="mr-table-body">
            <div v-for="rate in city.rates" :key="rate.id" class="mr-rate-row">
              <span class="mr-currency-cell">{{ rate.currency_code }}</span>
              <span class="mr-buy-cell">{{ formatRate(rate.buy_rate) }}</span>
              <span class="mr-sell-cell">{{ formatRate(rate.sell_rate) }}</span>
            </div>
          </div>
        </div>

        <div class="mr-city-info">
          <div class="currencies-info">
            Валюты: {{ getCurrencyIds(city.rates) }}
          </div>
          <div class="mr-update-time" v-if="city.rates.length > 0">
            Обновлено: {{ formatDate(city.rates[0].updated_at) }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import '@/assets/styles/components/public/MarketRates.css'
import { publicAPI } from '@/services/api'

export default {
  name: 'MarketRates',
  data() {
    return {
      rates: [],
      loading: false,
      error: null,
      refreshInterval: null
    }
  },
  computed: {
    groupedCities() {
      if (!Array.isArray(this.rates) || this.rates.length === 0) return []

      // Группируем курсы по городу
      const map = new Map()

      this.rates.forEach(rate => {
        // Предполагается, что в API есть поле city_name
        const cityName = rate.city_name || 'Неизвестный город'

        if (!map.has(cityName)) {
          map.set(cityName, {
            name: cityName,
            rates: []
          })
        }

        map.get(cityName).rates.push(rate)
      })

      // Сортируем курсы в каждом городе по валютам (USD, EUR, RUB)
      const currencyOrder = ['USD', 'RUB', 'EUR']

      return Array.from(map.values()).map(city => ({
        ...city,
        rates: city.rates.sort((a, b) => {
          const aIndex = currencyOrder.indexOf(a.currency_code)
          const bIndex = currencyOrder.indexOf(b.currency_code)

          if (aIndex !== -1 && bIndex !== -1) return aIndex - bIndex
          if (aIndex !== -1) return -1
          if (bIndex !== -1) return 1
          return a.currency_code.localeCompare(b.currency_code)
        })
      }))
    }
  },
  methods: {
    async loadMarketRates(silent = false) {
      if (!silent) this.loading = true
      this.error = null

      try {
        const response = await publicAPI.getRates()
        this.rates = Array.isArray(response.data)
          ? response.data.map(rate => ({
              id: rate.id,
              city_name: rate.city_name,  // Обязательно должно приходить с API
              currency_code: rate.currency_code,
              buy_rate: parseFloat(rate.buy),
              sell_rate: parseFloat(rate.sell),
              updated_at: rate.date + 'T' + rate.time
            }))
          : []

        if (this.rates.length === 0) {
          this.error = 'Нет данных о рыночных курсах'
        }
      } catch (error) {
        if (error.response) {
          switch (error.response.status) {
            case 401:
              this.error = 'Необходима авторизация для просмотра курсов'
              break
            case 403:
              this.error = 'Недостаточно прав для просмотра курсов'
              break
            case 404:
              this.error = 'Сервис курсов валют временно недоступен'
              break
            case 500:
              this.error = 'Ошибка сервера. Попробуйте позже'
              break
            default:
              this.error = `Ошибка загрузки данных (${error.response.status})`
          }
        } else if (error.code === 'ECONNABORTED') {
          this.error = 'Превышено время ожидания. Проверьте подключение к интернету'
        } else if (error.code === 'NETWORK_ERROR') {
          this.error = 'Ошибка сети. Проверьте подключение к интернету'
        } else {
          this.error = 'Неожиданная ошибка. Попробуйте обновить страницу'
        }
      } finally {
        this.loading = false
      }
    },
    formatRate(rate) {
      if (rate === null || rate === undefined || isNaN(rate)) return '-'
      return rate.toFixed(4)
    },
    formatDate(dateString) {
      if (!dateString) return '-'
      try {
        const date = new Date(dateString)
        return date.toLocaleDateString('ru-RU', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        })
      } catch {
        return dateString
      }
    },
    getCurrencyIds(ratesArray) {
      if (!ratesArray || !Array.isArray(ratesArray)) return 'Нет валют'
      return ratesArray
        .map(rate => rate.currency_code)
        .filter((v, i, a) => a.indexOf(v) === i)
        .join(', ')
    }
  },
  mounted() {
    this.loadMarketRates()

    this.refreshInterval = setInterval(() => {
      this.loadMarketRates(true)
    }, 5 * 60 * 1000)
  },
  beforeUnmount() {
    if (this.refreshInterval) clearInterval(this.refreshInterval)
  }
}
</script>