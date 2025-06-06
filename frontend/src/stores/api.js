import { defineStore } from 'pinia'
import axios from 'axios'
import { getApiBaseUrl } from '../config/api.js'

// API 기본 설정
const API_BASE_URL = getApiBaseUrl()

console.log('🌐 Final API Base URL:', API_BASE_URL)

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// 요청 인터셉터
api.interceptors.request.use(
  (config) => {
    console.log(`🔄 API 요청: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('❌ API 요청 에러:', error)
    return Promise.reject(error)
  }
)

// 응답 인터셉터
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API 응답: ${response.config.url} (${response.status})`)
    return response
  },
  (error) => {
    console.error(`❌ API 응답 에러: ${error.config?.url}`, error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export const useApiStore = defineStore('api', {
  state: () => ({
    // 연결 상태
    isConnected: false,
    lastUpdated: null,
    
    // 데이터베이스 통계
    stats: {
      stocks: 0,
      daily_prices: 0,
      sector_prices: 0,
      investor_trends: 0,
      unique_stocks_with_prices: 0,
      date_range: { start: null, end: null }
    },
    
    // 종목 데이터
    stocks: [],
    stocksTotal: 0,
    currentStock: null,
    
    // 섹터 데이터
    sectors: [],
    
    // 대시보드 데이터
    dashboardData: {},
    
    // 로딩 상태
    loading: {
      stats: false,
      stocks: false,
      stock: false,
      sectors: false,
      dashboard: false,
      prices: false,
      investors: false
    },
    
    // 에러 상태
    errors: {
      stats: null,
      stocks: null,
      stock: null,
      sectors: null,
      dashboard: null,
      prices: null,
      investors: null
    }
  }),
  
  getters: {
    // 연결 상태 확인
    isHealthy: (state) => state.isConnected,
    
    // 데이터 존재 여부
    hasData: (state) => state.stats.stocks > 0,
    
    // 종목 수
    totalStocks: (state) => state.stats.stocks,
    
    // 최신 업데이트 시간
    lastUpdateFormatted: (state) => {
      if (!state.lastUpdated) return '알 수 없음'
      return new Date(state.lastUpdated).toLocaleString('ko-KR')
    }
  },
  
  actions: {
    // 헬스 체크
    async checkHealth() {
      try {
        const response = await api.get('/api/health')
        this.isConnected = response.data.status === 'healthy'
        this.lastUpdated = response.data.timestamp
        return response.data
      } catch (error) {
        this.isConnected = false
        throw error
      }
    },
    
    // 데이터베이스 통계 조회
    async fetchStats() {
      this.loading.stats = true
      this.errors.stats = null
      
      try {
        const response = await api.get('/api/stats')
        this.stats = response.data
        return response.data
      } catch (error) {
        this.errors.stats = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading.stats = false
      }
    },
    
    // 종목 목록 조회
    async fetchStocks(params = {}) {
      this.loading.stocks = true
      this.errors.stocks = null
      
      try {
        const response = await api.get('/api/stocks', { params })
        this.stocks = response.data.stocks
        this.stocksTotal = response.data.total
        return response.data
      } catch (error) {
        this.errors.stocks = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading.stocks = false
      }
    },
    
    // 특정 종목 상세 정보
    async fetchStock(ticker) {
      this.loading.stock = true
      this.errors.stock = null
      
      try {
        const response = await api.get(`/api/stocks/${ticker}`)
        this.currentStock = response.data
        return response.data
      } catch (error) {
        this.errors.stock = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading.stock = false
      }
    },
    
    // 종목 주가 데이터
    async fetchStockPrices(ticker, params = {}) {
      this.loading.prices = true
      this.errors.prices = null
      
      try {
        const response = await api.get(`/api/stocks/${ticker}/prices`, { params })
        return response.data
      } catch (error) {
        this.errors.prices = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading.prices = false
      }
    },
    
    // 종목 투자자 동향
    async fetchStockInvestorTrends(ticker, params = {}) {
      this.loading.investors = true
      this.errors.investors = null
      
      try {
        const response = await api.get(`/api/stocks/${ticker}/investor-trends`, { params })
        return response.data
      } catch (error) {
        this.errors.investors = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading.investors = false
      }
    },
    
    // 종목 상세 정보 (Vue 컴포넌트에서 사용)
    async getStockDetail(ticker) {
      return await this.fetchStock(ticker)
    },

    // 섹터 목록 (Vue 컴포넌트에서 사용)
    async getSectors() {
      await this.fetchSectors()
      return this.sectors
    },
    
    // 섹터 데이터
    async fetchSectors() {
      this.loading.sectors = true
      this.errors.sectors = null
      
      try {
        const response = await api.get('/api/sectors')
        this.sectors = response.data.sectors
        return response.data
      } catch (error) {
        this.errors.sectors = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading.sectors = false
      }
    },
    
    // 대시보드 데이터
    async fetchDashboard() {
      this.loading.dashboard = true
      this.errors.dashboard = null
      
      try {
        const response = await api.get('/api/dashboard')
        this.dashboardData = response.data
        return response.data
      } catch (error) {
        this.errors.dashboard = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading.dashboard = false
      }
    },
    
    // 에러 초기화
    clearError(key) {
      if (key) {
        this.errors[key] = null
      } else {
        Object.keys(this.errors).forEach(k => {
          this.errors[k] = null
        })
      }
    },
    
    // 모든 데이터 새로고침
    async refreshAll() {
      try {
        await this.checkHealth()
        await this.fetchStats()
        return true
      } catch (error) {
        console.error('전체 새로고침 실패:', error)
        return false
      }
    }
  }
}) 