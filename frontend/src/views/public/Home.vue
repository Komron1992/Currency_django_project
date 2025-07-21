<template>
  <div class="home-page">
    <div class="content">
      <!-- Секция: рыночные курсы -->
      <section class="section-block">
        <MarketRates />
      </section>

      <!-- Секция: банковские курсы -->
      <section class="section-block">
        <BankRates />
      </section>
    </div>
  </div>
</template>

<script>
import '@/assets/styles/views/public/Home.css'
import BankRates from '../../components/public/BankCurrencyRates.vue'
import MarketRates from '../../components/public/MarketRates.vue'

export default {
  components: {
    BankRates,
    MarketRates
  },
  mounted() {
    console.log('[DEBUG] Home.vue loaded with market rates')
  }
}
</script>
