<template>
  <div class="stat-card" :class="cardClasses">
    <div class="flex items-center">
      <div class="flex-shrink-0">
        <div class="text-2xl">{{ icon }}</div>
      </div>
      <div class="ml-4 w-0 flex-1">
        <dl>
          <dt class="text-sm font-medium truncate" :class="titleClasses">
            {{ title }}
          </dt>
          <dd class="flex items-baseline">
            <div class="text-2xl font-semibold" :class="valueClasses">
              {{ formatValue(value) }}
            </div>
          </dd>
          <dd v-if="subtitle" class="text-xs mt-1" :class="subtitleClasses">
            {{ subtitle }}
          </dd>
        </dl>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [Number, String],
    required: true
  },
  icon: {
    type: String,
    default: '📊'
  },
  color: {
    type: String,
    default: 'blue',
    validator: (value) => ['blue', 'green', 'purple', 'orange', 'red'].includes(value)
  },
  subtitle: {
    type: String,
    default: ''
  }
})

// 색상별 클래스 정의
const colorVariants = {
  blue: {
    card: 'bg-blue-50 border-blue-200',
    title: 'text-blue-600',
    value: 'text-blue-900',
    subtitle: 'text-blue-500'
  },
  green: {
    card: 'bg-green-50 border-green-200',
    title: 'text-green-600',
    value: 'text-green-900',
    subtitle: 'text-green-500'
  },
  purple: {
    card: 'bg-purple-50 border-purple-200',
    title: 'text-purple-600',
    value: 'text-purple-900',
    subtitle: 'text-purple-500'
  },
  orange: {
    card: 'bg-orange-50 border-orange-200',
    title: 'text-orange-600',
    value: 'text-orange-900',
    subtitle: 'text-orange-500'
  },
  red: {
    card: 'bg-red-50 border-red-200',
    title: 'text-red-600',
    value: 'text-red-900',
    subtitle: 'text-red-500'
  }
}

// 계산된 속성
const cardClasses = computed(() => 
  `border rounded-lg p-5 ${colorVariants[props.color].card}`
)

const titleClasses = computed(() => colorVariants[props.color].title)
const valueClasses = computed(() => colorVariants[props.color].value)
const subtitleClasses = computed(() => colorVariants[props.color].subtitle)

// 값 포맷팅
const formatValue = (value) => {
  if (typeof value === 'number') {
    return value.toLocaleString('ko-KR')
  }
  return value
}
</script>

<style scoped>
.stat-card {
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
</style> 