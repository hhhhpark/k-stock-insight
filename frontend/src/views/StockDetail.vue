<template>
  <div class="container mx-auto px-4 py-8">
    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>
    
    <div v-else-if="error" class="text-center py-8">
      <div class="text-red-600 mb-4">{{ error }}</div>
      <button @click="fetchStockDetail" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
        다시 시도
      </button>
    </div>
    
    <div v-else-if="stock" class="space-y-6">
      <!-- 종목 헤더 -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">{{ stock.name }}</h1>
            <p class="text-gray-600">{{ stock.ticker }} • {{ stock.market }}</p>
            <p v-if="stock.sector_name" class="text-sm text-gray-500">{{ stock.sector_name }}</p>
          </div>
          <div class="text-right">
            <div class="text-2xl font-bold text-gray-900">
              {{ formatNumber(latestPrice?.close) }}원
            </div>
            <div class="text-sm text-gray-500">
              {{ latestPrice?.date }}
            </div>
          </div>
        </div>
      </div>
      
      <!-- 주가 정보 -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">최근 주가 정보</h2>
        <div v-if="prices.length > 0" class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">날짜</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">시가</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">고가</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">저가</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">종가</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">거래량</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="price in prices" :key="price.date">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ price.date }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ formatNumber(price.open) }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ formatNumber(price.high) }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ formatNumber(price.low) }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ formatNumber(price.close) }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ formatNumber(price.volume) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useApiStore } from '../stores/api'

export default {
  name: 'StockDetail',
  data() {
    return {
      stock: null,
      prices: [],
      loading: true,
      error: null
    }
  },
  computed: {
    latestPrice() {
      return this.prices.length > 0 ? this.prices[0] : null
    }
  },
  async mounted() {
    await this.fetchStockDetail()
  },
  methods: {
    async fetchStockDetail() {
      const apiStore = useApiStore()
      const ticker = this.$route.params.ticker
      
      this.loading = true
      this.error = null
      
      try {
        // 종목 상세 정보 조회
        const stockResponse = await apiStore.getStockDetail(ticker)
        this.stock = stockResponse.stock
        this.prices = stockResponse.recent_prices || []
      } catch (error) {
        console.error('종목 상세 조회 실패:', error)
        this.error = '종목 정보를 불러오는데 실패했습니다.'
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