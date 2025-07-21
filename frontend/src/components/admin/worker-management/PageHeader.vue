<template>
  <div class="page-header">
    <div class="header-content">
      <div class="header-text">
        <h1>{{ title }}</h1>
        <p v-if="subtitle">{{ subtitle }}</p>
      </div>
      <button
        v-if="showAddButton"
        @click="$emit('add-worker')"
        class="add-btn"
      >
        <span class="icon">+</span>
        Добавить работника
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  },
  showAddButton: {
    type: Boolean,
    default: true
  }
})

defineEmits(['add-worker'])
</script>

<style scoped>
.page-header {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.header-text h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #1a202c;
}

.header-text p {
  margin: 0;
  color: #64748b;
  font-size: 16px;
}

.add-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #667eea;
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.add-btn:hover {
  background: #5a6fd8;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.add-btn .icon {
  font-size: 20px;
  font-weight: bold;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-text h1 {
    font-size: 24px;
  }

  .add-btn {
    align-self: stretch;
    justify-content: center;
  }
}
</style>