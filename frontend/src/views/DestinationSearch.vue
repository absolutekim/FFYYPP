<template>
  <div class="search-redirect">
    <div class="loading">
      <div class="spinner"></div>
      <p>Loading to Search Page...</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DestinationSearch',
  created() {
    // 검색 쿼리를 여행지 목록 페이지로 리다이렉트
    const query = this.$route.query.q || '';
    
    // replace 대신 push를 사용하여 브라우저 히스토리에 기록
    this.$router.push({
      path: '/destinations',
      query: { q: query }
    }).catch(err => {
      // 이미 /destinations 페이지에 있는 경우 에러가 발생할 수 있으므로 처리
      if (err.name !== 'NavigationDuplicated') {
        console.error('Navigation error:', err);
      }
    });
  }
};
</script>

<style scoped>
.search-redirect {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style> 