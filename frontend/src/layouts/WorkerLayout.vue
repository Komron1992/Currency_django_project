<template>
  <div class="worker-layout">
    <WorkerNavbar />
    <div class="worker-content">
      <div class="container">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script>
import '@/assets/styles/layouts/WorkerLayout.css'
import WorkerNavbar from '@components/worker/WorkerNavbar.vue'

export default {
  name: 'WorkerLayout',
  components: {
    WorkerNavbar
  }
}
</script>
