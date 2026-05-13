<template>
  <Teleport to="body">
    <div
      v-if="visible"
      class="fixed inset-0 z-50 flex items-end sm:items-center justify-center"
      @click="onClose"
    >
      <div class="absolute inset-0 bg-black/50" />
      <div
        class="relative bg-white w-full sm:w-[600px] sm:rounded-2xl rounded-t-2xl max-h-[85vh] overflow-y-auto"
        @click.stop
      >
        <div class="sticky top-0 bg-white px-4 py-3 border-b border-gray-100 flex items-center justify-between z-10">
          <h3 class="text-base font-bold text-gray-800">{{ title }}</h3>
          <button
            class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 text-gray-500"
            @click="onClose"
          >
            ✕
          </button>
        </div>
        <div class="p-4">
          <slot />
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
interface Props {
  visible: boolean
  title: string
}

defineProps<Props>()
const emit = defineEmits<{ close: [] }>()

function onClose() {
  emit('close')
}
</script>
