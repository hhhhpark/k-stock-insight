// API 설정 파일
export const API_CONFIG = {
  // 개발 환경
  development: {
    baseURL: 'http://localhost:8000',
    timeout: 30000,
  },
  
  // 프로덕션 환경
  production: {
    baseURL: 'https://k-stock-backend.onrender.com',
    timeout: 30000,
  }
}

// 현재 환경 감지
export const getCurrentEnvironment = () => {
  return import.meta.env.PROD ? 'production' : 'development'
}

// API 기본 URL 가져오기
export const getApiBaseUrl = () => {
  const env = getCurrentEnvironment()
  const envApiUrl = import.meta.env.VITE_API_BASE_URL
  
  console.log('🔧 API Config:', {
    environment: env,
    envVar: envApiUrl,
    fallback: API_CONFIG[env].baseURL
  })
  
  return envApiUrl || API_CONFIG[env].baseURL
}

export default API_CONFIG 