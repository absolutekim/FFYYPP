<template>
  <div class="destination-recommend">
    <div class="header">
      <h1>맞춤형 여행지 추천</h1>
      <p>회원님의 관심사와 활동에 맞는 여행지를 추천해드립니다.</p>
    </div>

    <div v-if="isLoading" class="loading">
      <div class="spinner"></div>
      <p>추천 여행지를 불러오는 중입니다...</p>
    </div>

    <div v-else-if="error" class="error-container">
      <p>{{ error }}</p>
      <button @click="fetchRecommendations" class="retry-btn">다시 시도</button>
    </div>

    <div v-else>
      <!-- 태그 그룹별 추천 -->
      <div v-if="Object.keys(tagGroupRecommendations).length > 0" class="recommendation-section">
        <div class="section-header">
          <h2>내 관심사 기반 추천</h2>
          <p class="section-description">
            회원님이 선택한 관심 태그를 기반으로 추천한 여행지입니다.
          </p>
        </div>
        
        <!-- 각 태그별 추천 섹션 -->
        <div v-for="(destinations, tag) in tagGroupRecommendations" :key="tag" class="tag-group">
          <h3 class="tag-title">{{ getTagTitle(tag) }}</h3>
          
          <div class="destinations-grid">
            <div 
              v-for="destination in destinations" 
              :key="destination.id" 
              class="destination-card"
            >
              <div 
                class="destination-image" 
                :style="{ backgroundImage: `url(${destination.image || 'https://via.placeholder.com/300x200?text=No+Image'})` }"
              ></div>
              <div class="destination-info">
                <h3>{{ destination.name }}</h3>
                <p class="location">{{ getLocationString(destination) }}</p>
                <p class="category" v-if="destination.category">{{ destination.category }}</p>
                <div class="similarity-score">
                  <span class="score-label">유사도:</span>
                  <div class="score-bar">
                    <div class="score-fill" :style="{ width: `${destination.similarity_score * 100}%` }"></div>
                  </div>
                  <span class="score-value">{{ Math.round(destination.similarity_score * 100) }}%</span>
                </div>
                <router-link :to="`/destinations/${destination.id}`" class="view-details">자세히 보기</router-link>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 활동 기반 추천 -->
      <div v-if="activityBasedRecommendations.length > 0" class="recommendation-section">
        <div class="section-header">
          <h2>내 활동 기반 추천</h2>
          <p class="section-description">
            회원님의 좋아요와 리뷰를 분석하여 맞춤 추천한 여행지입니다.
            <span v-if="activityWeight < 1" class="weight-info">
              (활동 데이터 반영 비율: {{ Math.round(activityWeight * 100) }}%)
            </span>
          </p>
        </div>
        
        <div class="destinations-grid">
          <div 
            v-for="destination in activityBasedRecommendations" 
            :key="destination.id" 
            class="destination-card"
          >
            <div 
              class="destination-image" 
              :style="{ backgroundImage: `url(${destination.image || 'https://via.placeholder.com/300x200?text=No+Image'})` }"
            ></div>
            <div class="destination-info">
              <h3>{{ destination.name }}</h3>
              <p class="location">{{ getLocationString(destination) }}</p>
              <p class="category" v-if="destination.category">{{ destination.category }}</p>
              <div class="similarity-score">
                <span class="score-label">유사도:</span>
                <div class="score-bar">
                  <div class="score-fill" :style="{ width: `${destination.similarity_score * 100}%` }"></div>
                </div>
                <span class="score-value">{{ Math.round(destination.similarity_score * 100) }}%</span>
              </div>
              <router-link :to="`/destinations/${destination.id}`" class="view-details">자세히 보기</router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- 서브카테고리 기반 추천 -->
      <div v-if="subcategoryRecommendations.length > 0" class="recommendation-section">
        <div class="section-header">
          <h2>서브카테고리 기반 추천</h2>
          <p class="section-description">
            회원님이 좋아하는 서브카테고리(Classes & Workshops, Outdoor Activities 등)를 기반으로 추천한 여행지입니다.
          </p>
        </div>
        
        <div class="destinations-grid">
          <div 
            v-for="destination in subcategoryRecommendations" 
            :key="destination.id" 
            class="destination-card"
          >
            <div 
              class="destination-image" 
              :style="{ backgroundImage: `url(${destination.image || 'https://via.placeholder.com/300x200?text=No+Image'})` }"
            ></div>
            <div class="destination-info">
              <h3>{{ destination.name }}</h3>
              <p class="location">{{ getLocationString(destination) }}</p>
              <p class="subcategory" v-if="destination.subcategories && destination.subcategories.length > 0">
                {{ Array.isArray(destination.subcategories) ? destination.subcategories[0] : destination.subcategories }}
              </p>
              <div class="similarity-score">
                <span class="score-label">유사도:</span>
                <div class="score-bar">
                  <div class="score-fill" :style="{ width: `${destination.similarity_score * 100}%` }"></div>
                </div>
                <span class="score-value">{{ Math.round(destination.similarity_score * 100) }}%</span>
              </div>
              <router-link :to="`/destinations/${destination.id}`" class="view-details">자세히 보기</router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- 서브타입 기반 추천 -->
      <div v-if="subtypeRecommendations.length > 0" class="recommendation-section">
        <div class="section-header">
          <h2>서브타입 기반 추천</h2>
          <p class="section-description">
            회원님이 좋아하는 서브타입(Lessons & Workshops, Cooking Classes 등)을 기반으로 추천한 여행지입니다.
          </p>
        </div>
        
        <div class="destinations-grid">
          <div 
            v-for="destination in subtypeRecommendations" 
            :key="destination.id" 
            class="destination-card"
          >
            <div 
              class="destination-image" 
              :style="{ backgroundImage: `url(${destination.image || 'https://via.placeholder.com/300x200?text=No+Image'})` }"
            ></div>
            <div class="destination-info">
              <h3>{{ destination.name }}</h3>
              <p class="location">{{ getLocationString(destination) }}</p>
              <p class="subtype" v-if="destination.subtypes && destination.subtypes.length > 0">
                {{ Array.isArray(destination.subtypes) ? destination.subtypes[0] : destination.subtypes }}
              </p>
              <div class="similarity-score">
                <span class="score-label">유사도:</span>
                <div class="score-bar">
                  <div class="score-fill" :style="{ width: `${destination.similarity_score * 100}%` }"></div>
                </div>
                <span class="score-value">{{ Math.round(destination.similarity_score * 100) }}%</span>
              </div>
              <router-link :to="`/destinations/${destination.id}`" class="view-details">자세히 보기</router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- 국가 기반 추천 -->
      <div v-if="countryRecommendations.length > 0" class="recommendation-section">
        <div class="section-header">
          <h2>국가 기반 추천</h2>
          <p class="section-description">
            회원님이 좋아하는 국가(Japan, South Korea 등)를 기반으로 추천한 여행지입니다.
          </p>
        </div>
        
        <div class="destinations-grid">
          <div 
            v-for="destination in countryRecommendations" 
            :key="destination.id" 
            class="destination-card"
          >
            <div 
              class="destination-image" 
              :style="{ backgroundImage: `url(${destination.image || 'https://via.placeholder.com/300x200?text=No+Image'})` }"
            ></div>
            <div class="destination-info">
              <h3>{{ destination.name }}</h3>
              <p class="location">{{ getLocationString(destination) }}</p>
              <p class="country" v-if="destination.country">{{ destination.country }}</p>
              <div class="similarity-score">
                <span class="score-label">유사도:</span>
                <div class="score-bar">
                  <div class="score-fill" :style="{ width: `${destination.similarity_score * 100}%` }"></div>
                </div>
                <span class="score-value">{{ Math.round(destination.similarity_score * 100) }}%</span>
              </div>
              <router-link :to="`/destinations/${destination.id}`" class="view-details">자세히 보기</router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- 인기 여행지 추천 -->
      <div v-if="popularRecommendations.length > 0" class="recommendation-section">
        <div class="section-header">
          <h2>인기 여행지</h2>
          <p class="section-description">
            많은 사용자들이 좋아하는 인기 여행지입니다.
          </p>
        </div>
        
        <div class="destinations-grid">
          <div 
            v-for="destination in popularRecommendations" 
            :key="destination.id" 
            class="destination-card"
          >
            <div 
              class="destination-image" 
              :style="{ backgroundImage: `url(${destination.image || 'https://via.placeholder.com/300x200?text=No+Image'})` }"
            ></div>
            <div class="destination-info">
              <h3>{{ destination.name }}</h3>
              <p class="location">{{ getLocationString(destination) }}</p>
              <p class="category" v-if="destination.category">{{ destination.category }}</p>
              <router-link :to="`/destinations/${destination.id}`" class="view-details">자세히 보기</router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- 추천 결과가 없는 경우 -->
      <div v-if="recommendations.length === 0" class="no-recommendations">
        <p>아직 추천할 여행지가 없습니다. 여행지에 좋아요를 누르거나 리뷰를 작성해보세요!</p>
        <router-link to="/destinations" class="browse-all-btn">모든 여행지 둘러보기</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'DestinationRecommend',
  data() {
    return {
      recommendations: [],
      subcategoryRecommendations: [],
      subtypeRecommendations: [],
      countryRecommendations: [],
      tagGroupRecommendations: {},
      activityWeight: 0,
      tagWeight: 1,
      isLoading: true,
      error: null
    };
  },
  computed: {
    isAuthenticated() {
      return !!localStorage.getItem('access_token');
    },
    activityBasedRecommendations() {
      return this.recommendations.filter(item => item.recommendation_type === 'activity');
    },
    tagBasedRecommendations() {
      return this.recommendations.filter(item => item.recommendation_type === 'tag');
    },
    popularRecommendations() {
      return this.recommendations.filter(item => item.recommendation_type === 'popular');
    }
  },
  methods: {
    getTagTitle(tag) {
      const tagTitles = {
        'Fun & Games': '놀이와 게임을 찾는 당신에게!',
        'Sights & Landmarks': '멋진 명소와 랜드마크를 찾는 당신에게!',
        'Transportation': '교통편을 찾고 계신가요?',
        'Traveler Resources': '여행자 리소스를 찾는 당신에게!',
        'Zoos & Aquariums': '동물원과 수족관을 좋아하는 당신에게!',
        'Museums': '박물관을 좋아하는 당신에게!',
        'Nature & Parks': '자연과 공원을 좋아하는 당신에게!',
        'Outdoor Activities': '야외 활동을 즐기는 당신에게!',
        'Shopping': '쇼핑을 좋아하는 당신에게!',
        'Spas & Wellness': '스파와 웰니스를 찾는 당신에게!',
        'Nightlife': '밤문화를 즐기는 당신에게!',
        'Food & Drink': '맛있는 음식과 음료를 찾는 당신에게!',
        'Classes & Workshops': '클래스와 워크샵을 찾는 당신에게!',
        'Concerts & Shows': '콘서트와 쇼를 좋아하는 당신에게!',
        'Casinos & Gambling': '카지노와 도박을 즐기는 당신에게!',
        'Water & Amusement Parks': '워터파크와 놀이공원을 좋아하는 당신에게!',
        'Tours': '투어를 찾는 당신에게!',
        'Events': '이벤트를 찾는 당신에게!'
      };
      
      return tagTitles[tag] || `${tag}를 좋아하는 당신에게!`;
    },
    getLocationString(destination) {
      const parts = [];
      if (destination.city) parts.push(destination.city);
      if (destination.state) parts.push(destination.state);
      if (destination.country) parts.push(destination.country);
      
      return parts.join(', ') || '위치 정보 없음';
    },
    async fetchRecommendations() {
      try {
        this.isLoading = true;
        this.error = null;
        this.recommendations = [];
        this.subcategoryRecommendations = [];
        this.subtypeRecommendations = [];
        this.countryRecommendations = [];
        this.tagGroupRecommendations = {};
        
        const token = localStorage.getItem('access_token');
        if (!token) {
          this.error = '로그인이 필요합니다.';
          this.isLoading = false;
          return;
        }
        
        console.log('맞춤 추천 여행지 요청 중...');
        
        const response = await axios.get('http://localhost:8000/api/destinations/recommend/', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        
        console.log('추천 응답:', response.data);
        
        if (response.data.results && response.data.results.length > 0) {
          this.recommendations = response.data.results;
          this.activityWeight = response.data.activity_weight || 0;
          this.tagWeight = response.data.tag_weight || 1;
          
          // 서브카테고리, 서브타입, 국가 기반 추천 결과 설정
          if (response.data.subcategory_recommendations) {
            this.subcategoryRecommendations = response.data.subcategory_recommendations;
          }
          
          if (response.data.subtype_recommendations) {
            this.subtypeRecommendations = response.data.subtype_recommendations;
          }
          
          if (response.data.country_recommendations) {
            this.countryRecommendations = response.data.country_recommendations;
          }
          
          // 태그 그룹별 추천 결과 설정
          if (response.data.tag_group_recommendations) {
            this.tagGroupRecommendations = response.data.tag_group_recommendations;
          }
        } else {
          this.error = '추천할 여행지가 없습니다.';
        }
        
        this.isLoading = false;
      } catch (error) {
        console.error('추천 여행지를 가져오는데 실패했습니다:', error);
        this.error = '추천 여행지를 가져오는데 실패했습니다. 다시 시도해주세요.';
        this.isLoading = false;
      }
    }
  },
  created() {
    if (this.isAuthenticated) {
      this.fetchRecommendations();
    } else {
      this.error = '로그인이 필요합니다.';
      this.isLoading = false;
    }
  }
};
</script>

<style scoped>
.destination-recommend {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: 2rem;
}

.header h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.header p {
  color: #7f8c8d;
  font-size: 1.1rem;
}

.loading {
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
}

.retry-btn {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
  font-size: 1rem;
}

.recommendation-section {
  margin-bottom: 3rem;
}

.section-header {
  margin-bottom: 1.5rem;
}

.section-header h2 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
  border-left: 4px solid #3498db;
  padding-left: 0.8rem;
}

.section-description {
  color: #7f8c8d;
  font-size: 1rem;
}

.weight-info {
  font-size: 0.9rem;
  color: #95a5a6;
}

.destinations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.destination-card {
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
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
  color: #2c3e50;
}

.location {
  color: #7f8c8d;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.category {
  display: inline-block;
  background-color: #e0f7fa;
  color: #00838f;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  margin-bottom: 0.8rem;
}

.similarity-score {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
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

.view-details {
  display: inline-block;
  background-color: #3498db;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  text-decoration: none;
  font-size: 0.9rem;
  transition: background-color 0.3s;
}

.view-details:hover {
  background-color: #2980b9;
}

.no-recommendations {
  text-align: center;
  padding: 3rem;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.browse-all-btn {
  display: inline-block;
  background-color: #3498db;
  color: white;
  padding: 0.8rem 1.5rem;
  border-radius: 4px;
  text-decoration: none;
  margin-top: 1rem;
  font-size: 1rem;
  transition: background-color 0.3s;
}

.browse-all-btn:hover {
  background-color: #2980b9;
}

.tag-group {
  margin-bottom: 2rem;
}

.tag-title {
  font-size: 1.3rem;
  color: #2c3e50;
  margin-bottom: 1rem;
  padding-left: 0.5rem;
  border-left: 3px solid #e74c3c;
}

@media (max-width: 768px) {
  .destination-recommend {
    padding: 1rem;
  }
  
  .destinations-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  }
}
</style> 