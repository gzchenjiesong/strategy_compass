<template>
  <div class="min-h-screen pb-16">
    <header class="sticky top-0 z-10 bg-white shadow-sm">
      <div class="max-w-3xl mx-auto px-4 h-12 flex items-center justify-between">
        <h1 class="text-lg font-bold text-gray-800">策略罗盘</h1>
        <span v-if="authStore.user" class="text-sm text-gray-500">
          {{ authStore.user.nickname }}
        </span>
      </div>
    </header>
    <main class="max-w-3xl mx-auto px-4 py-4">
      <slot />
    </main>
    <BottomNav />
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import BottomNav from './BottomNav.vue'

const authStore = useAuthStore()
</script>
