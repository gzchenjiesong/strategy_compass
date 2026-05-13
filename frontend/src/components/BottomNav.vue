<template>
  <nav class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-20">
    <div class="max-w-3xl mx-auto flex justify-around h-14 items-center">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        :class="[
          'flex flex-col items-center justify-center w-16 text-xs',
          $route.path === item.path ? 'text-blue-600' : 'text-gray-500'
        ]"
      >
        <span class="text-lg mb-0.5">{{ item.icon }}</span>
        <span>{{ item.label }}</span>
      </router-link>
    </div>
  </nav>
</template>

<script setup lang="ts">
const navItems = [
  { path: '/market', label: '市场', icon: '📊' },
  { path: '/news', label: '资讯', icon: '📰' },
  { path: '/watch', label: '关注', icon: '⭐' },
  { path: '/strategy', label: '策略', icon: '🎯' },
]
</script>
