<template>
  <div class="dashboard">
    <!-- 헤더 -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">📊 K-Stock Insight 대시보드</h1>
      <p class="text-gray-600">한국 주식 시장 데이터 분석 및 종목 발굴 플랫폼</p>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="apiStore.loading.dashboard" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      <span class="ml-3 text-gray-600">대시보드 데이터 로딩 중...</span>
    </div>

    <!-- 에러 상태 -->
    <div v-else-if="apiStore.errors.dashboard" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">데이터 로드 오류</h3>
          <p class="mt-1 text-sm text-red-700">{{ apiStore.errors.dashboard }}</p>
        </div>
      </div>
    </div>

    <!-- 메인 대시보드 내용 -->
    <div v-else>
      <!-- 통계 카드 섹션 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="전체 종목 수"
          :value="apiStore.stats.stocks"
          icon="📈"
          color="blue"
          :subtitle="`KOSPI: ${dashboardData.market_stats?.kospi_stocks || 0}, KOSDAQ: ${dashboardData.market_stats?.kosdaq_stocks || 0}`"
        />
        <StatCard
          title="수집된 시세 데이터"
          :value="apiStore.stats.daily_prices"
          icon="💹"
          color="green"
          subtitle="일별 OHLCV 데이터"
        />
        <StatCard
          title="투자자 동향 데이터"
          :value="apiStore.stats.investor_trends"
          icon="👥"
          color="purple"
          subtitle="외국인, 기관, 개인별"
        />
        <StatCard
          title="업종별 시세"
          :value="apiStore.stats.sector_prices"
          icon="🏢"
          color="orange"
          subtitle="KOSPI 업종 지수"
        />
      </div>

      <!-- 메인 콘텐츠 그리드 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- 거래량 상위 종목 -->
        <div class="bg-white rounded-lg shadow-sm border p-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            🔥 최근 거래량 상위 종목
            <span class="ml-2 text-sm font-normal text-gray-500">(최신 거래일 기준)</span>
          </h2>
          
          <div v-if="dashboardData.top_volume_stocks?.length" class="space-y-3">
            <div
              v-for="(stock, index) in dashboardData.top_volume_stocks.slice(0, 8)"
              :key="stock.ticker"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
              @click="viewStockDetail(stock.ticker)"
            >
              <div class="flex items-center space-x-3">
                <span class="flex-shrink-0 w-6 h-6 bg-blue-500 text-white text-xs font-bold rounded-full flex items-center justify-center">
                  {{ index + 1 }}
                </span>
                <div>
                  <p class="font-medium text-gray-900">{{ stock.name }}</p>
                  <p class="text-sm text-gray-500">{{ stock.ticker }}</p>
                </div>
              </div>
              <div class="text-right">
                <p class="font-semibold text-gray-900">{{ formatNumber(stock.close) }}원</p>
                <p class="text-sm text-gray-500">{{ formatVolume(stock.volume) }}</p>
              </div>
            </div>
          </div>
          
          <div v-else class="text-center py-8 text-gray-500">
            거래량 데이터를 불러오는 중...
          </div>
        </div>

        <!-- 투자자 순매수 상위 종목 -->
        <div class="bg-white rounded-lg shadow-sm border p-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            💰 투자자 순매수 상위
            <span class="ml-2 text-sm font-normal text-gray-500">(최근 7일)</span>
          </h2>
          
          <div v-if="dashboardData.top_net_purchases?.length" class="space-y-3">
            <div
              v-for="(purchase, index) in dashboardData.top_net_purchases.slice(0, 8)"
              :key="`${purchase.ticker}-${purchase.investor_type}`"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
              @click="viewStockDetail(purchase.ticker)"
            >
              <div class="flex items-center space-x-3">
                <span class="flex-shrink-0 w-6 h-6 bg-green-500 text-white text-xs font-bold rounded-full flex items-center justify-center">
                  {{ index + 1 }}
                </span>
                <div>
                  <p class="font-medium text-gray-900">{{ purchase.name }}</p>
                  <p class="text-sm text-gray-500">{{ purchase.ticker }} · {{ purchase.investor_type }}</p>
                </div>
              </div>
              <div class="text-right">
                <p class="font-semibold text-green-600">+{{ formatNumber(purchase.total_net_value) }}원</p>
              </div>
            </div>
          </div>
          
          <div v-else class="text-center py-8 text-gray-500">
            투자자 동향 데이터를 불러오는 중...
          </div>
        </div>
      </div>

      <!-- 빠른 접근 메뉴 -->
      <div class="mt-8 bg-white rounded-lg shadow-sm border p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">🚀 빠른 접근</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <QuickAccessCard
            title="종목 검색"
            description="개별 종목 분석"
            icon="🔍"
            @click="$router.push('/stocks')"
          />
          <QuickAccessCard
            title="섹터 분석"
            description="업종별 동향"
            icon="🏢"
            @click="$router.push('/sectors')"
          />
          <QuickAccessCard
            title="투자자 동향"
            description="매매 주체 분석"
            icon="👥"
            @click="$router.push('/investors')"
          />
          <QuickAccessCard
            title="조건 검색"
            description="맞춤 종목 탐색"
            icon="⚙️"
            @click="$router.push('/search')"
          />
        </div>
      </div>

      <!-- 데이터 현황 -->
      <div class="mt-8 bg-blue-50 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-blue-900 mb-3">📊 데이터 수집 현황</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <p class="text-blue-800">
              <span class="font-semibold">수집 기간:</span> 
              {{ apiStore.stats.date_range?.start }} ~ {{ apiStore.stats.date_range?.end }}
            </p>
            <p class="text-blue-800">
              <span class="font-semibold">업데이트:</span> 
              {{ apiStore.lastUpdateFormatted }}
            </p>
          </div>
          <div>
            <p class="text-blue-800">
              <span class="font-semibold">데이터 소스:</span> 
              한국거래소(KRX) via pykrx
            </p>
            <p class="text-blue-800">
              <span class="font-semibold">업데이트 주기:</span> 
              일 1회 (거래일 기준)
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useApiStore } from '../stores/api'
import StatCard from '../components/StatCard.vue'
import QuickAccessCard from '../components/QuickAccessCard.vue'

const router = useRouter()
const apiStore = useApiStore()

// 반응성 데이터
const dashboardData = ref({})

// 계산된 속성
const isLoading = computed(() => apiStore.loading.dashboard || apiStore.loading.stats)

// 컴포넌트 마운트 시 데이터 로드
onMounted(async () => {
  try {
    await apiStore.fetchStats()
    dashboardData.value = await apiStore.fetchDashboard()
  } catch (error) {
    console.error('대시보드 데이터 로드 실패:', error)
  }
})

// 메서드
const formatNumber = (number) => {
  if (typeof number !== 'number') return '0'
  return number.toLocaleString('ko-KR')
}

const formatVolume = (volume) => {
  if (typeof volume !== 'number') return '0'
  
  if (volume >= 100000000) {
    return `${(volume / 100000000).toFixed(1)}억주`
  } else if (volume >= 10000) {
    return `${(volume / 10000).toFixed(1)}만주`
  } else {
    return `${volume.toLocaleString()}주`
  }
}

const viewStockDetail = (ticker) => {
  router.push(`/stocks/${ticker}`)
}
</script>

<style scoped>
.dashboard {
  @apply max-w-7xl mx-auto;
}
</style> 