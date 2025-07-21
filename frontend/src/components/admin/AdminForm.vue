<template>
  <form @submit.prevent="submitForm" class="admin-form">
    <div class="admin-form__group">
      <label for="currency" class="admin-form__label">Валюта</label>
      <select
        id="currency"
        v-model="form.currency_id"
        class="admin-form__select"
        :disabled="loading"
      >
        <option value="">Выберите валюту</option>
        <option
          v-for="currency in currencies"
          :key="currency.id"
          :value="currency.id"
        >
          {{ currency.code }}
        </option>
      </select>
    </div>

    <div class="admin-form__group">
      <label for="buy" class="admin-form__label">Курс покупки</label>
      <input
        type="number"
        id="buy"
        v-model="form.buy"
        step="0.0001"
        class="admin-form__input"
        placeholder="Введите курс покупки"
        :disabled="loading"
      />
    </div>

    <div class="admin-form__group">
      <label for="sell" class="admin-form__label">Курс продажи</label>
      <input
        type="number"
        id="sell"
        v-model="form.sell"
        step="0.0001"
        class="admin-form__input"
        placeholder="Введите курс продажи"
        :disabled="loading"
      />
    </div>

    <button
      type="submit"
      class="admin-form__button"
      :disabled="loading"
    >
      {{ loading ? 'Добавление...' : 'Добавить курс' }}
    </button>

    <p v-if="message" class="admin-form__message admin-form__message--success">{{ message }}</p>
    <p v-if="error" class="admin-form__message admin-form__message--error">{{ error }}</p>
  </form>
</template>

<script setup>
import '@/assets/styles/components/admin/AdminForm.css'
</script>