<template>
  <div 
    class="quick-access-card bg-white border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-md transition-all duration-200 cursor-pointer"
    @click="$emit('click')"
  >
    <div class="flex items-center space-x-3">
      <div class="flex-shrink-0">
        <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center text-xl">
          {{ icon }}
        </div>
      </div>
      <div class="flex-1 min-w-0">
        <p class="text-sm font-medium text-gray-900 truncate">
          {{ title }}
        </p>
        <p class="text-xs text-gray-500 truncate">
          {{ description }}
        </p>
      </div>
      <div class="flex-shrink-0">
        <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    default: '🔗'
  }
})

defineEmits(['click'])
</script>

<style scoped>
.quick-access-card:hover {
  transform: translateY(-1px);
}
</style> 