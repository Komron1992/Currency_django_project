<template>
  <div class="min-h-screen bg-gray-50">
    <div class="container mx-auto px-4 py-6">
      <h1 class="text-2xl font-bold mb-4">Управление пользователями</h1>

      <!-- Поиск -->
      <input
        v-model="search"
        type="text"
        placeholder="Поиск по имени, email или телефону"
        class="mb-4 p-2 border rounded w-full max-w-md"
      />

      <div v-if="loading" class="text-gray-500">Загрузка пользователей...</div>
      <div v-else-if="error" class="text-red-500">Ошибка: {{ error }}</div>

      <div v-else class="w-full overflow-x-auto">
        <table class="w-full border-collapse mt-2 min-w-full table-fixed">
          <thead>
            <tr class="bg-gray-100 text-left">
              <th class="p-1 border text-sm w-16">ID</th>
              <th class="p-1 border text-sm w-48">Имя</th>
              <th class="p-1 border text-sm w-56">Email</th>
              <th class="p-1 border text-sm w-32">Телефон</th>
              <th class="p-1 border text-sm w-24">Роль</th>
              <th class="p-1 border text-sm w-32">Город</th>
              <th class="p-1 border text-sm w-24">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="user in filteredUsers"
              :key="user.id"
              class="hover:bg-gray-50 text-sm"
            >
              <td class="p-1 border text-xs">{{ user.id }}</td>
              <td class="p-1 border text-xs truncate">
                {{ user.first_name }} {{ user.last_name }}
              </td>
              <td class="p-1 border text-xs truncate">{{ user.email }}</td>
              <td class="p-1 border text-xs">{{ user.phone || '-' }}</td>
              <td class="p-1 border text-xs">{{ user.role }}</td>
              <td class="p-1 border text-xs truncate">{{ user.city_name || '-' }}</td>
              <td class="p-1 border">
                <div class="flex space-x-1 justify-center">
                  <button
                    @click="openEditModal(user)"
                    class="text-blue-600 hover:bg-blue-50 p-1 rounded text-xs"
                    title="Редактировать"
                  >
                    ✏️
                  </button>
                  <button
                    @click="confirmDelete(user)"
                    class="text-red-600 hover:bg-red-50 p-1 rounded text-xs"
                    title="Удалить"
                  >
                    🗑️
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 🧩 TELEPORT: модальное окно ВНЕШНЕ -->
    <teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click="closeModal">
        <div class="modal-content" @click.stop>
          <h2 class="text-xl font-bold mb-4">Редактировать пользователя</h2>
          <form v-if="editUser" @submit.prevent="saveUser">
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-1">Имя</label>
              <input
                v-model="editUser.first_name"
                type="text"
                class="p-2 border rounded w-full focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-1">Фамилия</label>
              <input
                v-model="editUser.last_name"
                type="text"
                class="p-2 border rounded w-full focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                v-model="editUser.email"
                type="email"
                class="p-2 border rounded w-full focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-1">Телефон</label>
              <input
                v-model="editUser.phone"
                type="tel"
                class="p-2 border rounded w-full focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-1">Роль</label>
              <select
                v-model="editUser.role"
                class="p-2 border rounded w-full focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="user">Пользователь</option>
                <option value="admin">Администратор</option>
                <option value="city_worker">Работник</option>
              </select>
            </div>

            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-1">Город</label>
              <input
                v-model="editUser.city_name"
                type="text"
                class="p-2 border rounded w-full focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div class="flex justify-end mt-6 space-x-2">
              <button
                type="button"
                @click="closeModal"
                class="bg-gray-300 hover:bg-gray-400 px-4 py-2 rounded"
              >
                Отмена
              </button>
              <button
                type="submit"
                class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
                :disabled="saving"
              >
                {{ saving ? 'Сохранение...' : 'Сохранить' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import adminAPI from '@/services/admin.js'

const users = ref([])
const search = ref('')
const loading = ref(false)
const error = ref(null)
const saving = ref(false)

const showModal = ref(false)
const editUser = ref(null)

const loadUsers = async () => {
  loading.value = true
  try {
    const res = await adminAPI.getUsers()
    users.value = res.data
  } catch (err) {
    error.value = err?.response?.data?.detail || 'Ошибка загрузки'
  } finally {
    loading.value = false
  }
}

const filteredUsers = computed(() => {
  const term = search.value.toLowerCase()
  return users.value.filter(
    u =>
      u.first_name.toLowerCase().includes(term) ||
      u.last_name.toLowerCase().includes(term) ||
      u.email.toLowerCase().includes(term) ||
      (u.phone || '').toLowerCase().includes(term)
  )
})

const openEditModal = (user) => {
  editUser.value = { ...user }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editUser.value = null
}

const saveUser = async () => {
  if (!editUser.value) return
  saving.value = true
  try {
    await adminAPI.updateUser(editUser.value.id, editUser.value)
    await loadUsers()
    closeModal()
  } catch (err) {
    alert('Ошибка при сохранении пользователя')
  } finally {
    saving.value = false
  }
}

const confirmDelete = async (user) => {
  if (confirm(`Удалить пользователя ${user.email}?`)) {
    try {
      await adminAPI.deleteUser(user.id)
      await loadUsers()
    } catch {
      alert('Ошибка при удалении')
    }
  }
}

onMounted(loadUsers)
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10000;
}

.modal-content {
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 28rem;
  max-height: 90vh;
  overflow-y: auto;
  animation: fade-in 0.2s ease-out;
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
