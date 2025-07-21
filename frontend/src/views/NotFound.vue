<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 px-4">
    <div class="max-w-md w-full text-center animate-fade-in">
      <div class="mb-8">
        <h1 class="text-6xl sm:text-9xl font-bold text-gray-300 mb-4">404</h1>
        <h2 class="text-xl sm:text-2xl font-semibold text-gray-700 mb-4">
          Страница не найдена
        </h2>
        <p class="text-gray-500 mb-8 text-sm sm:text-base">
          К сожалению, запрашиваемая страница не существует или была перемещена.
        </p>
      </div>

      <div class="space-y-4">
        <router-link
          to="/"
          class="inline-block bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-6 rounded-lg transition duration-200"
        >
          Вернуться на главную
        </router-link>

        <div class="flex flex-wrap justify-center gap-2 sm:space-x-4 text-sm">
          <router-link
            to="/login"
            class="text-blue-600 hover:text-blue-800 transition duration-200 px-2 py-1"
          >
            Войти
          </router-link>
          <span class="text-gray-400 hidden sm:inline">|</span>
          <router-link
            to="/admin/login"
            class="text-blue-600 hover:text-blue-800 transition duration-200 px-2 py-1"
          >
            Админ
          </router-link>
          <span class="text-gray-400 hidden sm:inline">|</span>
          <router-link
            to="/worker/login"
            class="text-blue-600 hover:text-blue-800 transition duration-200 px-2 py-1"
          >
            Сотрудник
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFound',
  mounted() {
    // Устанавливаем заголовок страницы
    document.title = '404 - Страница не найдена | Currency Exchange'
  }
}
</script>

<style scoped>
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fadeIn 0.6s ease-out;
}

/* Дополнительные стили при необходимости */
</style>