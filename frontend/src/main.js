import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './style.css'

// Pinia 상태 관리 라이브러리 생성
const pinia = createPinia()

// Vue 앱 생성 및 설정
const app = createApp(App)

app.use(pinia)
app.use(router)

// 전역 에러 핸들러
app.config.errorHandler = (err, vm, info) => {
  console.error('Vue Global Error:', err, info)
}

// 앱 마운트
app.mount('#app') 