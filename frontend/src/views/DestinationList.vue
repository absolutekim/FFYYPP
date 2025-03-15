<template>
  <div class="destination-list-container">
    <div class="search-section">
      <div class="search-container">
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="여행지 검색..." 
          class="search-input"
          @keyup.enter="handleSearch"
        />
        <button @click="handleSearch" class="search-button">
          <i class="fas fa-search"></i> 검색
        </button>
      </div>
      
      <div class="search-options">
        <div class="sort-container">
          <label for="sort-select">정렬:</label>
          <select id="sort-select" v-model="sortOption" @change="handleSort" class="sort-select">
            <option value="name">이름순</option>
            <option value="rating">평점순</option>
            <option value="popularity">인기순</option>
            <option value="recent">최신순</option>
          </select>
        </div>
        
        <div class="filter-container">
          <label for="category-select">카테고리:</label>
          <select id="category-select" v-model="selectedCategory" @change="handleFilter" class="filter-select">
            <option value="">전체</option>
            <option v-for="category in categories" :key="category" :value="category">{{ category }}</option>
          </select>
        </div>
        
        <div class="filter-container">
          <label for="country-select">국가:</label>
          <select id="country-select" v-model="selectedCountry" @change="handleFilter" class="filter-select">
            <option value="">전체</option>
            <option v-for="country in countries" :key="country" :value="country">{{ country }}</option>
          </select>
        </div>
        
        <div class="limit-container">
          <label for="result-limit">검색 결과 개수:</label>
          <select id="result-limit" v-model="resultLimit" class="limit-select" @change="handleLimitChange">
            <option value="20">20개</option>
            <option value="50">50개</option>
            <option value="100">100개</option>
            <option value="200">200개</option>
          </select>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="loading-container">
      <div class="spinner"></div>
      <p>여행지 정보를 불러오는 중입니다...</p>
    </div>

    <div v-else-if="error" class="error-container">
      <p>{{ error }}</p>
      <button @click="fetchDestinations" class="retry-button">다시 시도</button>
    </div>

    <div v-else>
      <div v-if="isSearchMode" class="search-results-header">
        <h2>
          <i class="fas fa-search"></i> 
          "{{ searchQuery }}" 검색 결과 ({{ filteredDestinations.length }}개)
          <span class="search-type">감정 분석 기반 검색</span>
        </h2>
        <button @click="clearSearch" class="clear-search-button">
          <i class="fas fa-times"></i> 검색 초기화
        </button>
      </div>

      <div v-if="filteredDestinations.length === 0" class="no-results">
        <p v-if="isSearchMode">검색 결과가 없습니다. 다른 키워드로 검색해보세요.</p>
        <p v-else>표시할 여행지가 없습니다.</p>
      </div>

      <div v-else class="destinations-grid">
        <div 
          v-for="destination in paginatedDestinations" 
          :key="destination.id" 
          class="destination-card"
          @click="viewDestinationDetails(destination.id)"
        >
          <div 
            class="destination-image" 
            :style="{ backgroundImage: `url(${destination.image || 'https://via.placeholder.com/300x200?text=No+Image'})` }"
          ></div>
          <div class="destination-info">
            <h3>{{ destination.name }}</h3>
            <p class="location">{{ getLocationString(destination) }}</p>
            
            <div class="destination-meta">
              <span v-if="destination.category" class="category-tag">{{ destination.category }}</span>
              <span v-if="destination.average_rating" class="rating">
                <i class="fas fa-star"></i> {{ destination.average_rating.toFixed(1) }}
              </span>
            </div>
            
            <!-- 유사도 정보 추가 -->
            <div v-if="isSearchMode && destination.similarity_score" class="similarity-score">
              <span class="score-label">유사도:</span>
              <div class="score-bar">
                <div class="score-fill" :style="{ width: `${destination.similarity_score * 100}%` }"></div>
              </div>
              <span class="score-value">{{ Math.round(destination.similarity_score * 100) }}%</span>
            </div>
            
            <p v-if="destination.description" class="description">
              {{ truncateText(destination.description, 100) }}
            </p>
            
            <div class="card-actions">
              <button class="view-details-button">
                자세히 보기 <i class="fas fa-arrow-right"></i>
              </button>
              
              <button 
                v-if="isAuthenticated" 
                @click.stop="addToPlanner(destination)" 
                class="add-to-planner-button"
              >
                <i class="fas fa-plus"></i> 플래너에 추가
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 페이지네이션 -->
      <div v-if="totalPages > 1" class="pagination">
        <button 
          @click="changePage(currentPage - 1)" 
          :disabled="currentPage === 1"
          class="pagination-button"
        >
          <i class="fas fa-chevron-left"></i>
        </button>
        
        <button 
          v-for="page in displayedPages" 
          :key="page" 
          @click="changePage(page)"
          :class="['pagination-button', { active: currentPage === page }]"
        >
          {{ page }}
        </button>
        
        <button 
          @click="changePage(currentPage + 1)" 
          :disabled="currentPage === totalPages"
          class="pagination-button"
        >
          <i class="fas fa-chevron-right"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'DestinationList',
  data() {
    return {
      destinations: [],
      isLoading: true,
      error: null,
      currentPage: 1,
      itemsPerPage: 12,
      searchQuery: '',
      isSearchMode: false,
      searchResults: [],
      sortOption: 'name',
      selectedCategory: '',
      categories: [],
      resultLimit: 50,
      selectedCountry: '',
      countries: []
    };
  },
  computed: {
    filteredDestinations() {
      let result = this.isSearchMode ? this.searchResults : this.destinations;
      
      // 카테고리 필터링
      if (this.selectedCategory) {
        result = result.filter(dest => dest.category === this.selectedCategory);
      }
      
      // 국가 필터링
      if (this.selectedCountry) {
        result = result.filter(dest => dest.country === this.selectedCountry);
      }
      
      // 정렬
      result = [...result].sort((a, b) => {
        switch (this.sortOption) {
          case 'name': {
            return a.name.localeCompare(b.name);
          }
          case 'rating': {
            const ratingA = a.average_rating || 0;
            const ratingB = b.average_rating || 0;
            return ratingB - ratingA;
          }
          case 'popularity': {
            const likesA = a.likes_count || 0;
            const likesB = b.likes_count || 0;
            return likesB - likesA;
          }
          case 'recent': {
            // 가정: created_at 필드가 있다고 가정
            const dateA = new Date(a.created_at || 0);
            const dateB = new Date(b.created_at || 0);
            return dateB - dateA;
          }
          default:
            return 0;
        }
      });
      
      return result;
    },
    paginatedDestinations() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.filteredDestinations.slice(start, end);
    },
    totalPages() {
      return Math.ceil(this.filteredDestinations.length / this.itemsPerPage);
    },
    displayedPages() {
      const pages = [];
      const maxPagesToShow = 5;
      
      let startPage = Math.max(1, this.currentPage - Math.floor(maxPagesToShow / 2));
      let endPage = startPage + maxPagesToShow - 1;
      
      if (endPage > this.totalPages) {
        endPage = this.totalPages;
        startPage = Math.max(1, endPage - maxPagesToShow + 1);
      }
      
      for (let i = startPage; i <= endPage; i++) {
        pages.push(i);
      }
      
      return pages;
    },
    isAuthenticated() {
      return !!localStorage.getItem('access_token');
    }
  },
  methods: {
    async fetchDestinations() {
      try {
        this.isLoading = true;
        this.error = null;
        
        const response = await axios.get('http://localhost:8000/api/destinations/');
        this.destinations = response.data;
        
        // 카테고리 목록 추출
        this.extractCategories();
        
        // 국가 목록 추출
        this.extractCountries();
        
        this.isLoading = false;
      } catch (error) {
        console.error('여행지 정보를 가져오는데 실패했습니다:', error);
        this.error = '여행지 정보를 가져오는데 실패했습니다. 다시 시도해주세요.';
        this.isLoading = false;
      }
    },
    
    extractCategories() {
      const categorySet = new Set();
      this.destinations.forEach(dest => {
        if (dest.category) {
          categorySet.add(dest.category);
        }
      });
      this.categories = Array.from(categorySet).sort();
    },
    
    extractCountries() {
      const countrySet = new Set();
      const destinations = this.isSearchMode ? this.searchResults : this.destinations;
      
      destinations.forEach(dest => {
        if (dest.country) {
          countrySet.add(dest.country);
        }
      });
      
      this.countries = Array.from(countrySet).sort();
    },
    
    async handleSearch() {
      if (!this.searchQuery.trim()) {
        this.clearSearch();
        return;
      }
      
      try {
        this.isLoading = true;
        this.error = null;
        
        const response = await axios.get(`http://localhost:8000/api/destinations/search/nlp/?query=${encodeURIComponent(this.searchQuery)}&limit=${this.resultLimit}`);
        
        if (response.data && response.data.results) {
          this.searchResults = response.data.results;
          this.isSearchMode = true;
          this.currentPage = 1; // 검색 시 첫 페이지로 이동
          
          // 국가 목록 추출
          this.extractCountries();
          
          // URL 쿼리 파라미터 업데이트 (검색 상태 유지)
          this.$router.replace({
            path: this.$route.path,
            query: { ...this.$route.query, q: this.searchQuery, limit: this.resultLimit }
          });
        } else {
          this.searchResults = [];
        }
        
        this.isLoading = false;
      } catch (error) {
        console.error('검색 중 오류가 발생했습니다:', error);
        this.error = '검색 중 오류가 발생했습니다. 다시 시도해주세요.';
        this.isLoading = false;
      }
    },
    
    handleLimitChange() {
      // 검색 결과 개수가 변경되면 검색을 다시 수행
      if (this.isSearchMode && this.searchQuery) {
        this.handleSearch();
      }
    },
    
    clearSearch() {
      this.searchQuery = '';
      this.isSearchMode = false;
      this.searchResults = [];
      this.currentPage = 1;
      this.selectedCountry = ''; // 국가 필터 초기화
      
      // URL 쿼리 파라미터에서 검색어와 검색 결과 개수 제거
      this.$router.replace({
        path: this.$route.path,
        query: { ...this.$route.query, q: undefined, limit: undefined }
      });
      
      // 국가 목록 다시 추출
      this.extractCountries();
    },
    
    handleSort() {
      // 정렬 옵션이 변경되면 첫 페이지로 이동
      this.currentPage = 1;
    },
    
    handleFilter() {
      // 필터 옵션이 변경되면 첫 페이지로 이동
      this.currentPage = 1;
    },
    
    changePage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page;
        // 페이지 변경 시 상단으로 스크롤
        window.scrollTo(0, 0);
      }
    },
    
    viewDestinationDetails(id) {
      this.$router.push(`/destinations/${id}`);
    },
    
    getLocationString(destination) {
      const parts = [];
      if (destination.city) parts.push(destination.city);
      if (destination.state) parts.push(destination.state);
      if (destination.country) parts.push(destination.country);
      
      return parts.join(', ') || '위치 정보 없음';
    },
    
    truncateText(text, maxLength) {
      if (!text) return '';
      if (text.length <= maxLength) return text;
      return text.slice(0, maxLength) + '...';
    },
    
    addToPlanner(destination) {
      // 사용자가 로그인하지 않은 경우
      if (!this.isAuthenticated) {
        this.$router.push('/login');
        return;
      }
      
      // 플래너 페이지로 이동하면서 여행지 정보 전달
      this.$router.push({
        path: '/planner',
        query: { destination: destination.id }
      });
    }
  },
  created() {
    this.fetchDestinations();
    
    // URL 쿼리 파라미터에서 검색어와 검색 결과 개수 가져오기
    const query = this.$route.query.q;
    const limit = this.$route.query.limit;
    
    if (limit) {
      this.resultLimit = parseInt(limit);
    }
    
    if (query) {
      this.searchQuery = query;
      this.handleSearch();
    }
  },
  watch: {
    // URL 변경 감지
    '$route.query.q': function(newQuery) {
      if (newQuery !== this.searchQuery) {
        this.searchQuery = newQuery || '';
        if (newQuery) {
          this.handleSearch();
        } else {
          this.clearSearch();
        }
      }
    }
  }
};
</script>

<style scoped>
.destination-list-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.search-section {
  margin-bottom: 2rem;
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.search-container {
  display: flex;
  margin-bottom: 1rem;
}

.search-input {
  flex-grow: 1;
  padding: 0.8rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 4px 0 0 4px;
  font-size: 1rem;
}

.search-button {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0 1.5rem;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s;
}

.search-button:hover {
  background-color: #2980b9;
}

.search-options {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.sort-container, .filter-container, .limit-container {
  display: flex;
  align-items: center;
}

.sort-container label, .filter-container label, .limit-container label {
  margin-right: 0.5rem;
  font-weight: 500;
  color: #4a5568;
}

.sort-select, .filter-select, .limit-select {
  padding: 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  background-color: white;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
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

.error-container {
  text-align: center;
  padding: 2rem;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  color: #e53e3e;
}

.retry-button {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
}

.search-results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.search-results-header h2 {
  font-size: 1.5rem;
  color: #2d3748;
  margin: 0;
}

.search-type {
  font-size: 0.9rem;
  color: #3498db;
  background-color: #e6f7ff;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  margin-left: 0.5rem;
  font-weight: normal;
}

.clear-search-button {
  background-color: #e2e8f0;
  color: #4a5568;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s;
}

.clear-search-button:hover {
  background-color: #cbd5e0;
}

.no-results {
  text-align: center;
  padding: 3rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  color: #4a5568;
}

.destinations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.destination-card {
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
}

.destination-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.destination-image {
  height: 180px;
  background-size: cover;
  background-position: center;
}

.destination-info {
  padding: 1.2rem;
}

.destination-info h3 {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
  color: #2d3748;
}

.location {
  color: #718096;
  font-size: 0.9rem;
  margin-bottom: 0.8rem;
}

.destination-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.8rem;
}

.category-tag {
  background-color: #e6f7ff;
  color: #0070f3;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
}

.rating {
  color: #f6ad55;
  font-weight: 600;
  font-size: 0.9rem;
}

.similarity-score {
  display: flex;
  align-items: center;
  margin: 0.8rem 0;
  font-size: 0.9rem;
}

.score-label {
  margin-right: 0.5rem;
  color: #7f8c8d;
}

.score-bar {
  flex-grow: 1;
  height: 6px;
  background-color: #ecf0f1;
  border-radius: 3px;
  overflow: hidden;
  margin: 0 0.5rem;
}

.score-fill {
  height: 100%;
  background-color: #3498db;
  border-radius: 3px;
}

.score-value {
  color: #3498db;
  font-weight: bold;
}

.description {
  color: #718096;
  font-size: 0.9rem;
  margin-bottom: 1rem;
  line-height: 1.4;
}

.card-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
}

.view-details-button {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s;
  flex: 1;
  margin-right: 0.5rem;
}

.add-to-planner-button {
  background-color: #27ae60;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s;
  flex: 1;
}

.add-to-planner-button:hover {
  background-color: #219653;
}

.pagination {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 2rem;
}

.pagination-button {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.pagination-button.active {
  background-color: #3498db;
  color: white;
  border-color: #3498db;
}

.pagination-button:hover:not(:disabled) {
  background-color: #f7fafc;
  border-color: #cbd5e0;
}

.pagination-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .destination-list-container {
    padding: 1rem;
  }
  
  .search-container {
    flex-direction: column;
  }
  
  .search-input {
    border-radius: 4px;
    margin-bottom: 0.5rem;
  }
  
  .search-button {
    border-radius: 4px;
    width: 100%;
    padding: 0.8rem;
  }
  
  .search-options {
    flex-direction: column;
  }
  
  .destinations-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  }
}
</style> 