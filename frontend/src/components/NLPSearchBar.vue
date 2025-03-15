<template>
  <div class="nlp-search-container">
    <div class="search-header">
      <h3>감정 분석 기반 여행지 검색</h3>
      <p class="search-description">
        검색어의 감정과 의미를 분석하여 최적의 여행지를 추천해드립니다.
        <br>
        예: "조용한 휴식이 필요해", "신나는 액티비티를 즐기고 싶어", "아이들과 함께 즐길 수 있는 곳"
      </p>
    </div>
    
    <div class="search-form">
      <div class="search-input-container">
        <input 
          type="text" 
          v-model="searchQuery" 
          @keyup.enter="performSearch"
          placeholder="여행 취향이나 원하는 경험을 자연어로 입력해보세요" 
          class="search-input"
        />
        <button @click="performSearch" class="search-button" :disabled="isLoading">
          <span v-if="isLoading">검색 중...</span>
          <span v-else>검색</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NLPSearchBar',
  data() {
    return {
      searchQuery: '',
      isLoading: false
    };
  },
  methods: {
    async performSearch() {
      if (!this.searchQuery.trim()) {
        return;
      }
      
      this.isLoading = true;
      
      try {
        // 검색 쿼리를 DestinationList 컴포넌트로 리다이렉트
        await this.$router.push({
          path: '/destinations',
          query: { q: this.searchQuery }
        }).catch(err => {
          if (err.name !== 'NavigationDuplicated') {
            console.error('Navigation error:', err);
          }
        });
        
        // 검색 후 검색창 초기화
        this.searchQuery = '';
      } catch (error) {
        console.error('검색 중 오류 발생:', error);
      } finally {
        this.isLoading = false;
      }
    }
  }
};
</script>

<style scoped>
.nlp-search-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.search-header {
  text-align: center;
  margin-bottom: 30px;
}

.search-header h3 {
  font-size: 24px;
  color: #2d3748;
  margin-bottom: 10px;
}

.search-description {
  color: #718096;
  font-size: 16px;
  line-height: 1.5;
}

.search-form {
  margin-bottom: 30px;
}

.search-input-container {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.search-input {
  flex: 1;
  padding: 15px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.search-button {
  background-color: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0 20px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.search-button:hover {
  background-color: #5a67d8;
}

.search-button:disabled {
  background-color: #a0aec0;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .search-input-container {
    flex-direction: column;
  }
  
  .search-button {
    width: 100%;
    padding: 12px;
  }
}
</style> 