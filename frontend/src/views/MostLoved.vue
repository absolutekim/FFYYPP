<template>
  <div class="most-loved-container">
    <h1 class="page-title">가장 인기 있는 여행지</h1>
    
    <div v-if="isLoading" class="loading-container">
      <div class="spinner"></div>
      <p>인기 여행지를 불러오는 중...</p>
    </div>
    
    <div v-else-if="locations.length === 0" class="empty-state">
      <p>표시할 여행지가 없습니다.</p>
    </div>
    
    <div v-else class="locations-grid">
      <div v-for="(location, index) in locations" :key="location.id" class="location-card">
        <div class="rank-badge">{{ index + 1 }}</div>
        <router-link :to="`/destinations/${location.id}`" class="location-link">
          <div class="location-image-container">
            <img v-if="location.image" :src="location.image" :alt="location.name" class="location-image">
            <div v-else class="placeholder-image">
              <i class="fas fa-image"></i>
            </div>
          </div>
          <div class="location-info">
            <h3 class="location-name">{{ location.name }}</h3>
            <p v-if="location.city || location.country" class="location-address">
              <i class="fas fa-map-marker-alt"></i>
              {{ getLocationString(location) }}
            </p>
            <div class="location-meta">
              <div class="likes-count">
                <i class="fas fa-heart"></i>
                <span>{{ location.likes_count }}</span>
              </div>
              <div v-if="location.average_rating" class="rating">
                <i class="fas fa-star"></i>
                <span>{{ location.average_rating.toFixed(1) }}</span>
              </div>
            </div>
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { useToast } from 'vue-toastification';

export default {
  name: 'MostLoved',
  data() {
    return {
      locations: [],
      isLoading: true
    };
  },
  setup() {
    const toast = useToast();
    return { toast };
  },
  mounted() {
    this.fetchMostLovedLocations();
  },
  methods: {
    async fetchMostLovedLocations() {
      this.isLoading = true;
      try {
        const response = await axios.get('/api/destinations/most-loved/');
        this.locations = response.data;
      } catch (error) {
        console.error('인기 여행지를 불러오는 중 오류가 발생했습니다:', error);
        this.toast.error('인기 여행지를 불러오는 중 오류가 발생했습니다.');
      } finally {
        this.isLoading = false;
      }
    },
    getLocationString(location) {
      const parts = [];
      if (location.city) parts.push(location.city);
      if (location.country) parts.push(location.country);
      return parts.join(', ');
    }
  }
};
</script>

<style scoped>
.most-loved-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.page-title {
  font-size: 2rem;
  margin-bottom: 2rem;
  text-align: center;
  color: #333;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top-color: #3498db;
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 3rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  margin-top: 2rem;
}

.locations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 2rem;
}

.location-card {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  background-color: white;
}

.location-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
}

.rank-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  width: 30px;
  height: 30px;
  background-color: #ff5722;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  z-index: 1;
}

.location-link {
  text-decoration: none;
  color: inherit;
  display: block;
}

.location-image-container {
  height: 180px;
  overflow: hidden;
}

.location-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.location-card:hover .location-image {
  transform: scale(1.05);
}

.placeholder-image {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f0f0f0;
  color: #aaa;
  font-size: 2rem;
}

.location-info {
  padding: 1rem;
}

.location-name {
  margin: 0 0 0.5rem;
  font-size: 1.2rem;
  color: #333;
}

.location-address {
  margin: 0 0 1rem;
  font-size: 0.9rem;
  color: #666;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.location-meta {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
}

.likes-count, .rating {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.likes-count i {
  color: #e74c3c;
}

.rating i {
  color: #f1c40f;
}
</style> 