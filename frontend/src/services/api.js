// Экспорт всех сервисов
export { default as apiClient } from './client.js'
export { authAPI } from './auth.js'
export { adminAPI } from './admin.js'
export { workerAPI } from './worker.js'
export { publicAPI } from './public.js'  // ← Добавьте эту строку

// Для обратной совместимости
export { authAPI as apiService } from './auth.js'
export { authAPI as default } from './auth.js'