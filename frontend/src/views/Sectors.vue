<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">섹터 분석</h1>
      <p class="text-gray-600">업종별 시장 동향을 분석합니다</p>
    </div>

    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="error" class="text-center py-8">
      <div class="text-red-600 mb-4">{{ error }}</div>
      <button @click="fetchSectors" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
        다시 시도
      </button>
    </div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
      <div v-for="sector in sectors" :key="sector.sector_name" 
           class="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
        <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ sector.sector_name }}</h3>
        <div class="space-y-2">
          <div class="flex justify-between">
            <span class="text-gray-600">최근 가격:</span>
            <span class="font-medium">{{ formatNumber(sector.latest_price) }}원</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">업데이트:</span>
            <span class="text-sm text-gray-500">{{ sector.latest_date }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useApiStore } from '../stores/api'

export default {
  name: 'Sectors',
  data() {
    return {
      sectors: [],
      loading: true,
      error: null
    }
  },
  async mounted() {
    await this.fetchSectors()
  },
  methods: {
    async fetchSectors() {
      const apiStore = useApiStore()
      
      this.loading = true
      this.error = null
      
      try {
        this.sectors = await apiStore.getSectors()
      } catch (error) {
        console.error('섹터 조회 실패:', error)
        this.error = '섹터 정보를 불러오는데 실패했습니다.'
      } finally {
        this.loading = false
      }
    },
    formatNumber(num) {
      if (!num) return '0'
      return new Intl.NumberFormat('ko-KR').format(num)
    }
  }
}
</script> 