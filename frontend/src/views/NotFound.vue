<template>
  <div class="container mx-auto px-4 py-16 text-center">
    <div class="text-6xl mb-4">🔍</div>
    <h1 class="text-4xl font-bold text-gray-900 mb-4">404</h1>
    <h2 class="text-xl font-semibold text-gray-700 mb-4">페이지를 찾을 수 없습니다</h2>
    <p class="text-gray-500 mb-8">요청하신 페이지가 존재하지 않거나 이동되었습니다.</p>
    
    <div class="space-x-4">
      <router-link to="/" class="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
        홈으로 돌아가기
      </router-link>
      <button @click="$router.go(-1)" class="inline-block px-6 py-3 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors">
        이전 페이지
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFound'
}
</script> 