<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- 상단 네비게이션 -->
    <nav class="bg-white shadow-lg border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <!-- 로고 -->
            <router-link to="/" class="flex items-center">
              <div class="flex-shrink-0">
                <h1 class="text-2xl font-bold text-blue-600">K-Stock Insight</h1>
                <p class="text-xs text-gray-500">한국 주식 시장 분석</p>
              </div>
            </router-link>
          </div>
          
          <!-- 네비게이션 메뉴 -->
          <div class="hidden md:flex items-center space-x-8">
            <router-link 
              to="/" 
              class="text-gray-900 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              :class="{ 'text-blue-600 bg-blue-50': $route.path === '/' }"
            >
              대시보드
            </router-link>
            <router-link 
              to="/stocks" 
              class="text-gray-900 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              :class="{ 'text-blue-600 bg-blue-50': $route.path.startsWith('/stocks') }"
            >
              종목 분석
            </router-link>
            <router-link 
              to="/sectors" 
              class="text-gray-900 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              :class="{ 'text-blue-600 bg-blue-50': $route.path === '/sectors' }"
            >
              섹터 분석
            </router-link>
            <router-link 
              to="/investors" 
              class="text-gray-900 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              :class="{ 'text-blue-600 bg-blue-50': $route.path === '/investors' }"
            >
              투자자 동향
            </router-link>
          </div>
          
          <!-- 모바일 메뉴 버튼 -->
          <div class="md:hidden flex items-center">
            <button 
              @click="mobileMenuOpen = !mobileMenuOpen"
              class="text-gray-500 hover:text-gray-600 focus:outline-none focus:text-gray-600"
            >
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
      
      <!-- 모바일 메뉴 -->
      <div v-show="mobileMenuOpen" class="md:hidden">
        <div class="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-gray-50">
          <router-link 
            to="/" 
            @click="mobileMenuOpen = false"
            class="block px-3 py-2 rounded-md text-base font-medium text-gray-900 hover:text-blue-600 hover:bg-gray-100"
          >
            대시보드
          </router-link>
          <router-link 
            to="/stocks" 
            @click="mobileMenuOpen = false"
            class="block px-3 py-2 rounded-md text-base font-medium text-gray-900 hover:text-blue-600 hover:bg-gray-100"
          >
            종목 분석
          </router-link>
          <router-link 
            to="/sectors" 
            @click="mobileMenuOpen = false"
            class="block px-3 py-2 rounded-md text-base font-medium text-gray-900 hover:text-blue-600 hover:bg-gray-100"
          >
            섹터 분석
          </router-link>
          <router-link 
            to="/investors" 
            @click="mobileMenuOpen = false"
            class="block px-3 py-2 rounded-md text-base font-medium text-gray-900 hover:text-blue-600 hover:bg-gray-100"
          >
            투자자 동향
          </router-link>
        </div>
      </div>
    </nav>

    <!-- 연결 상태 표시 -->
    <div v-if="!isConnected" class="bg-red-500 text-white px-4 py-2 text-sm text-center">
      ⚠️ 서버와의 연결이 끊어졌습니다. 새로고침해주세요.
    </div>

    <!-- 메인 콘텐츠 -->
    <main class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <!-- 로딩 상태 -->
      <div v-if="isLoading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <span class="ml-3 text-gray-600">데이터를 불러오는 중...</span>
      </div>
      
      <!-- 라우터 뷰 -->
      <router-view v-else />
    </main>

    <!-- 푸터 -->
    <footer class="bg-white border-t mt-auto">
      <div class="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center">
          <p class="text-gray-500 text-sm">
            © 2025 K-Stock Insight. 한국 주식 시장 데이터 분석 플랫폼.
          </p>
          <div class="flex items-center space-x-4 text-sm text-gray-500">
            <span>Last Updated: {{ lastUpdated }}</span>
            <div class="flex items-center">
              <div class="w-2 h-2 bg-green-500 rounded-full mr-1" v-if="isConnected"></div>
              <div class="w-2 h-2 bg-red-500 rounded-full mr-1" v-else></div>
              <span>{{ isConnected ? 'Connected' : 'Disconnected' }}</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useApiStore } from './stores/api'
import { format } from 'date-fns'

const router = useRouter()
const apiStore = useApiStore()

// 반응성 데이터
const mobileMenuOpen = ref(false)
const isLoading = ref(false)

// 계산된 속성
const isConnected = computed(() => apiStore.isConnected)
const lastUpdated = computed(() => {
  return apiStore.lastUpdated ? format(new Date(apiStore.lastUpdated), 'yyyy-MM-dd HH:mm:ss') : '알 수 없음'
})

// 앱 초기화
onMounted(async () => {
  try {
    isLoading.value = true
    await apiStore.checkHealth()
    await apiStore.fetchStats()
  } catch (error) {
    console.error('앱 초기화 실패:', error)
  } finally {
    isLoading.value = false
  }
})

// 페이지 이동시 모바일 메뉴 닫기
router.afterEach(() => {
  mobileMenuOpen.value = false
})
</script>

<style>
/* 전역 스타일 */
#app {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* 커스텀 스크롤바 */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 테이블 반응형 */
.table-responsive {
  overflow-x: auto;
}

/* 차트 컨테이너 */
.chart-container {
  position: relative;
  height: 400px;
  margin: 1rem 0;
}

/* 애니메이션 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* 카드 호버 효과 */
.card-hover {
  transition: all 0.3s ease;
}

.card-hover:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}
</style> 