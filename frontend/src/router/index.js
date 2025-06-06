import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Stocks from '../views/Stocks.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: {
      title: '대시보드'
    }
  },
  {
    path: '/stocks',
    name: 'Stocks',
    component: Stocks,
    meta: {
      title: '종목 검색'
    }
  },
  {
    path: '/stocks/:ticker',
    name: 'StockDetail',
    component: () => import('../views/StockDetail.vue'),
    meta: {
      title: '종목 상세'
    }
  },
  {
    path: '/sectors',
    name: 'Sectors',
    component: () => import('../views/Sectors.vue'),
    meta: {
      title: '섹터 분석'
    }
  },
  {
    path: '/investors',
    name: 'Investors',
    component: () => import('../views/Investors.vue'),
    meta: {
      title: '투자자 동향'
    }
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('../views/Search.vue'),
    meta: {
      title: '조건 검색'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue'),
    meta: {
      title: '페이지를 찾을 수 없음'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 네비게이션 가드 - 페이지 타이틀 설정
router.beforeEach((to, from, next) => {
  const title = to.meta.title || 'K-Stock Insight'
  document.title = `${title} - K-Stock Insight`
  next()
})

export default router 