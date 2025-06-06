<template>
  <div class="stocks-page">
    <!-- 헤더 -->
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">🔍 종목 검색</h1>
      <p class="text-gray-600">개별 종목을 검색하고 분석하세요</p>
    </div>

    <!-- 검색 및 필터 영역 -->
    <div class="bg-white rounded-lg shadow-sm border p-6 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- 검색어 입력 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">종목명/코드 검색</label>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="예: 삼성전자, 005930"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            @input="handleSearch"
          />
        </div>

        <!-- 시장 필터 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">시장 구분</label>
          <select
            v-model="selectedMarket"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            @change="handleSearch"
          >
            <option value="">전체</option>
            <option value="KOSPI">KOSPI</option>
            <option value="KOSDAQ">KOSDAQ</option>
          </select>
        </div>

        <!-- 검색 버튼 -->
        <div class="flex items-end">
          <button
            @click="handleSearch"
            class="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
            :disabled="apiStore.loading.stocks"
          >
            <span v-if="apiStore.loading.stocks">검색 중...</span>
            <span v-else>🔍 검색</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 검색 결과 -->
    <div class="bg-white rounded-lg shadow-sm border">
      <!-- 결과 헤더 -->
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-gray-900">
            검색 결과
            <span v-if="apiStore.stocksTotal" class="text-sm font-normal text-gray-500">
              (총 {{ apiStore.stocksTotal.toLocaleString() }}개)
            </span>
          </h2>
          
          <!-- 페이지 크기 선택 -->
          <div class="flex items-center space-x-2">
            <label class="text-sm text-gray-600">페이지당:</label>
            <select
              v-model="pageSize"
              @change="handleSearch"
              class="px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option :value="20">20개</option>
              <option :value="50">50개</option>
              <option :value="100">100개</option>
            </select>
          </div>
        </div>
      </div>

      <!-- 로딩 상태 -->
      <div v-if="apiStore.loading.stocks" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span class="ml-3 text-gray-600">검색 중...</span>
      </div>

      <!-- 에러 상태 -->
      <div v-else-if="apiStore.errors.stocks" class="p-6">
        <div class="bg-red-50 border border-red-200 rounded-lg p-4">
          <p class="text-red-700">{{ apiStore.errors.stocks }}</p>
        </div>
      </div>

      <!-- 종목 리스트 -->
      <div v-else-if="apiStore.stocks.length" class="divide-y divide-gray-200">
        <div
          v-for="stock in apiStore.stocks"
          :key="stock.ticker"
          class="p-6 hover:bg-gray-50 transition-colors cursor-pointer"
          @click="viewStockDetail(stock.ticker)"
        >
          <div class="flex items-center justify-between">
            <div class="flex-1">
              <div class="flex items-center space-x-3">
                <h3 class="text-lg font-semibold text-gray-900">{{ stock.name }}</h3>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                      :class="stock.market === 'KOSPI' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'">
                  {{ stock.market }}
                </span>
              </div>
              <div class="mt-1 flex items-center space-x-4 text-sm text-gray-500">
                <span>{{ stock.ticker }}</span>
                <span v-if="stock.sector">{{ stock.sector }}</span>
              </div>
            </div>
            
            <div class="flex items-center space-x-4">
              <!-- 최근 데이터 표시 (있다면) -->
              <div class="text-right">
                <div class="text-sm text-gray-500">상세 정보</div>
              </div>
              
              <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- 검색 결과 없음 -->
      <div v-else class="p-6 text-center">
        <div class="text-gray-500">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-2.34 0-4.469-.967-6-2.525M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <p class="mt-2 text-sm">검색 결과가 없습니다.</p>
          <p class="text-xs text-gray-400">다른 검색어를 입력해보세요.</p>
        </div>
      </div>

      <!-- 페이지네이션 -->
      <div v-if="apiStore.stocks.length && totalPages > 1" class="px-6 py-4 border-t border-gray-200">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-700">
            {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, apiStore.stocksTotal) }}개 
            / 총 {{ apiStore.stocksTotal.toLocaleString() }}개
          </div>
          
          <div class="flex items-center space-x-1">
            <button
              @click="goToPage(currentPage - 1)"
              :disabled="currentPage <= 1"
              class="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              이전
            </button>
            
            <template v-for="page in visiblePages" :key="page">
              <button
                v-if="page === '...'"
                disabled
                class="px-3 py-1 text-sm text-gray-400"
              >
                ...
              </button>
              <button
                v-else
                @click="goToPage(page)"
                :class="[
                  'px-3 py-1 text-sm border border-gray-300 rounded',
                  page === currentPage 
                    ? 'bg-blue-600 text-white border-blue-600' 
                    : 'hover:bg-gray-50'
                ]"
              >
                {{ page }}
              </button>
            </template>
            
            <button
              @click="goToPage(currentPage + 1)"
              :disabled="currentPage >= totalPages"
              class="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              다음
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useApiStore } from '../stores/api'

const router = useRouter()
const apiStore = useApiStore()

// 반응성 데이터
const searchQuery = ref('')
const selectedMarket = ref('')
const currentPage = ref(1)
const pageSize = ref(50)

// 계산된 속성
const totalPages = computed(() => Math.ceil(apiStore.stocksTotal / pageSize.value))

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  
  if (start > 1) {
    pages.push(1)
    if (start > 2) pages.push('...')
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  if (end < totalPages.value) {
    if (end < totalPages.value - 1) pages.push('...')
    pages.push(totalPages.value)
  }
  
  return pages
})

// 메서드
const handleSearch = async () => {
  currentPage.value = 1
  await searchStocks()
}

const searchStocks = async () => {
  try {
    await apiStore.fetchStocks({
      limit: pageSize.value,
      offset: (currentPage.value - 1) * pageSize.value,
      market: selectedMarket.value || undefined,
      search: searchQuery.value.trim() || undefined
    })
  } catch (error) {
    console.error('종목 검색 실패:', error)
  }
}

const goToPage = async (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    await searchStocks()
  }
}

const viewStockDetail = (ticker) => {
  router.push(`/stocks/${ticker}`)
}

// 컴포넌트 마운트 시 초기 검색
onMounted(() => {
  handleSearch()
})
</script>

<style scoped>
.stocks-page {
  @apply max-w-6xl mx-auto;
}
</style> 