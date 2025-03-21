<template>
  <div class="destination-recommend">
    <div class="header">
      <h1>Recommendations For You</h1>
      <p>List of Recommended Destionations as your Preferences</p>
    </div>

    <div v-if="isLoading" class="loading">
      <div class="spinner"></div>
      <p>Fetching Recommended List...</p>
    </div>

    <div v-else-if="error" class="error-container">
      <p>{{ error }}</p>
      <button @click="fetchRecommendations" class="retry-btn">다시 시도</button>
    </div>

    <div v-else>
      <!-- 태그 그룹별 추천 -->
      <div v-if="Object.keys(tagGroupRecommendations).length > 0" class="recommendation-section">
        <div class="section-header">
          <h2>Based on your Preference</h2>
          <p class="section-description">
            These are the recommended destinations based on the tag of interest you chose.
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
                  <span class="score-label">Similarity:</span>
                  <div class="score-bar">
                    <div class="score-fill" :style="{ width: `${destination.similarity_score * 100}%` }"></div>
                  </div>
                  <span class="score-value">{{ Math.round(destination.similarity_score * 100) }}%</span>
                </div>
                <router-link :to="`/destinations/${destination.id}`" class="view-details">View Details</router-link>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 활동 기반 추천 -->
      <div v-if="activityBasedRecommendations.length > 0" class="recommendation-section">
        <div class="section-header">
          <h2>Based on your Activities</h2>
          <p class="section-description">
            These are customized recommended destinations by analyzing your likes and reviews.
            <span v-if="activityWeight < 1" class="weight-info">
              (Activity Data Reflection Rate: {{ Math.round(activityWeight * 100) }}%)
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
                <span class="score-label">Similarity:</span>
                <div class="score-bar">
                  <div class="score-fill" :style="{ width: `${destination.similarity_score * 100}%` }"></div>
                </div>
                <span class="score-value">{{ Math.round(destination.similarity_score * 100) }}%</span>
              </div>
              <router-link :to="`/destinations/${destination.id}`" class="view-details">View Details</router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- 서브카테고리 기반 추천 -->
      <div v-if="subcategoryRecommendations.length > 0" class="recommendation-section">
        <div class="section-header">
          <h2>Based on Sub-Categories</h2>
          <p class="section-description">
            These are recommended destinations based on your favorite subcategories (classes & workshops, outdoor activities, etc.).
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
                <span class="score-label">Similarity:</span>
                <div class="score-bar">
                  <div class="score-fill" :style="{ width: `${destination.similarity_score * 100}%` }"></div>
                </div>
                <span class="score-value">{{ Math.round(destination.similarity_score * 100) }}%</span>
              </div>
              <router-link :to="`/destinations/${destination.id}`" class="view-details">View Details</router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- 서브타입 기반 추천 -->
      <div v-if="subtypeRecommendations.length > 0" class="recommendation-section">
        <div class="section-header">
          <h2>Based on Sub-Types</h2>
          <p class="section-description">
            These are recommended destinations based on your favorite subtype (Lessons & Worksops, Cooking Classes, etc.).
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
                <span class="score-label">Similarity:</span>
                <div class="score-bar">
                  <div class="score-fill" :style="{ width: `${destination.similarity_score * 100}%` }"></div>
                </div>
                <span class="score-value">{{ Math.round(destination.similarity_score * 100) }}%</span>
              </div>
              <router-link :to="`/destinations/${destination.id}`" class="view-details">View Details</router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- 국가 기반 추천 -->
      <div v-if="countryRecommendations.length > 0" class="recommendation-section">
        <div class="section-header">
          <h2>Based on Countries</h2>
          <p class="section-description">
            These are recommended destinations based on your favorite countries (Japan, South Korea, etc.).
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
                <span class="score-label">Similarity:</span>
                <div class="score-bar">
                  <div class="score-fill" :style="{ width: `${destination.similarity_score * 100}%` }"></div>
                </div>
                <span class="score-value">{{ Math.round(destination.similarity_score * 100) }}%</span>
              </div>
              <router-link :to="`/destinations/${destination.id}`" class="view-details">View Details</router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- 키워드 기반 추천 -->
      <div v-if="keywordRecommendations.length > 0" class="recommendation-section">
        <div class="section-header">
          <h2>Based on your Reviews</h2>
          <p class="section-description">
            These are the recommended destinations based on the keywords extracted from your review.
          </p>
        </div>
        
        <div class="destinations-grid">
          <div 
            v-for="destination in keywordRecommendations" 
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
                <span class="score-label">Similarity:</span>
                <div class="score-bar">
                  <div class="score-fill" :style="{ width: `${destination.similarity_score * 100}%` }"></div>
                </div>
                <span class="score-value">{{ Math.round(destination.similarity_score * 100) }}%</span>
              </div>
              <router-link :to="`/destinations/${destination.id}`" class="view-details">View Details</router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- 최근 본 여행지 기반 추천 -->
      <div v-if="recentlyViewedRecommendations.length > 0" class="recommendation-section">
        <div class="section-header">
          <h2>Based on Recently-Viewed Destinations</h2>
          <p class="section-description">
            These are similar destinations to the ones you recently looked at.
          </p>
        </div>
        
        <div class="destinations-grid">
          <div 
            v-for="destination in recentlyViewedRecommendations" 
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
                <span class="score-label">Similarity:</span>
                <div class="score-bar">
                  <div class="score-fill" :style="{ width: `${destination.similarity_score * 100}%` }"></div>
                </div>
                <span class="score-value">{{ Math.round(destination.similarity_score * 100) }}%</span>
              </div>
              <router-link :to="`/destinations/${destination.id}`" class="view-details">View Details</router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- 인기 여행지 추천 -->
      <div v-if="popularRecommendations.length > 0" class="recommendation-section">
        <div class="section-header">
          <h2>Popular Destinations</h2>
          <p class="section-description">
            These are popular destinations that many users love.
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
              <router-link :to="`/destinations/${destination.id}`" class="view-details">View Details</router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- 추천 결과가 없는 경우 -->
      <div v-if="recommendations.length === 0" class="no-recommendations">
        <p>There are no travel destinations to recommend yet. Click Like or write a review for the destination!</p>
        <router-link to="/destinations" class="browse-all-btn">Seek for Destinations</router-link>
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
      keywordRecommendations: [],
      recentlyViewedRecommendations: [],
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
        'Fun & Games': 'For those looking for fun and games!',
        'Sights & Landmarks': 'For those looking for great sights and landmarks!',
        'Transportation': 'Looking for transportation options?',
        'Traveler Resources': 'For those looking for traveler resources!',
        'Zoos & Aquariums': 'For those who love zoos and aquariums!',
        'Museums': 'For those who love museums!',
        'Nature & Parks': 'For those who love nature and parks!',
        'Outdoor Activities': 'For those who enjoy outdoor activities!',
        'Shopping': 'For those who love shopping!',
        'Spas & Wellness': 'For those looking for spas and wellness!',
        'Nightlife': 'For those who enjoy nightlife!',
        'Food & Drink': 'For those looking for delicious food and drinks!',
        'Classes & Workshops': 'For those looking for classes and workshops!',
        'Concerts & Shows': 'For those who love concerts and shows!',
        'Casinos & Gambling': 'For those who enjoy casinos and gambling!',
        'Water & Amusement Parks': 'For those who love water and amusement parks!',
        'Tours': 'For those looking for tours!',
        'Events': 'For those looking for events!'
      };
      
      return tagTitles[tag] || `For those who love ${tag}!`;
    },
    getLocationString(destination) {
      const parts = [];
      if (destination.city) parts.push(destination.city);
      if (destination.state) parts.push(destination.state);
      if (destination.country) parts.push(destination.country);
      
      return parts.join(', ') || 'No Location Information';
    },
    async fetchRecommendations() {
      try {
        this.isLoading = true;
        this.error = null;
        this.recommendations = [];
        this.subcategoryRecommendations = [];
        this.subtypeRecommendations = [];
        this.countryRecommendations = [];
        this.keywordRecommendations = [];
        this.recentlyViewedRecommendations = [];
        this.tagGroupRecommendations = {};
        
        const token = localStorage.getItem('access_token');
        if (!token) {
          this.error = 'You must be logged in';
          this.isLoading = false;
          return;
        }
        
        console.log('Loading Recommendation List...');
        
        // 최근 본 여행지 정보 가져오기
        const recentlyViewed = JSON.parse(localStorage.getItem('recentlyViewed') || '[]');
        console.log('Recently Viewed Destinations', recentlyViewed);
        
        const response = await axios.post('http://localhost:8000/api/destinations/recommend/', 
          { recently_viewed: recentlyViewed },
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );
        
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
          
          // 키워드 기반 추천 결과 설정
          if (response.data.keyword_recommendations) {
            this.keywordRecommendations = response.data.keyword_recommendations;
          }
          
          // 최근 본 여행지 기반 추천 결과 설정
          if (response.data.recently_viewed_recommendations) {
            this.recentlyViewedRecommendations = response.data.recently_viewed_recommendations;
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