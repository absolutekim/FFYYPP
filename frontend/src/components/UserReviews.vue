<template>
  <div class="user-reviews-container">
    <h2 class="section-title">내가 작성한 리뷰</h2>
    
    <div v-if="isLoading" class="loading-container">
      <div class="spinner"></div>
      <p>리뷰 목록을 불러오는 중...</p>
    </div>
    
    <div v-else-if="reviews.length === 0" class="empty-state">
      <p>아직 작성한 리뷰가 없습니다.</p>
      <router-link to="/destinations" class="browse-link">여행지 둘러보기</router-link>
    </div>
    
    <div v-else class="reviews-list">
      <div v-for="review in reviews" :key="review.id" class="review-card">
        <div class="review-header">
          <div class="destination-info">
            <router-link 
              v-if="review.location_id || (review.location && review.location.id)" 
              :to="`/destinations/${review.location_id || (review.location && review.location.id)}`" 
              class="destination-name"
            >
              {{ review.location_name || (review.location && review.location.name) || '여행지 정보 없음' }}
            </router-link>
            <span v-else class="destination-name">
              {{ review.location_name || (review.location && review.location.name) || '여행지 정보 없음' }}
            </span>
            <p v-if="review.location_city || review.location_country || (review.location && (review.location.city || review.location.country))" class="destination-location">
              <i class="fas fa-map-marker-alt"></i>
              {{ getLocationString(review) }}
            </p>
          </div>
          <div class="review-meta">
            <div class="rating">
              <span v-for="star in 5" :key="star" class="star" :class="{ 'filled': star <= review.rating }">
                <i class="fas fa-star"></i>
              </span>
            </div>
            <span class="review-date">{{ formatDate(review.created_at) }}</span>
          </div>
        </div>
        
        <div class="review-content">
          <p>{{ review.content }}</p>
        </div>
        
        <div v-if="review.sentiment" class="review-sentiment" :class="getSentimentClass(review.sentiment)">
          <span class="sentiment-label">감정 분석:</span>
          <span class="sentiment-value">{{ getSentimentText(review.sentiment) }}</span>
        </div>
        
        <div v-if="review.keywords && review.keywords.length > 0" class="review-keywords">
          <span v-for="(keyword, index) in review.keywords" :key="index" class="keyword-tag">
            {{ keyword }}
          </span>
        </div>
        
        <div class="review-actions">
          <button @click="editReview(review)" class="action-button edit">
            <i class="fas fa-edit"></i> 수정
          </button>
          <button @click="deleteReview(review.id)" class="action-button delete">
            <i class="fas fa-trash"></i> 삭제
          </button>
        </div>
      </div>
    </div>
    
    <div v-if="hasMore" class="load-more">
      <button @click="loadMore" :disabled="isLoadingMore" class="load-more-button">
        {{ isLoadingMore ? '불러오는 중...' : '더 보기' }}
      </button>
    </div>
    
    <!-- 리뷰 수정 모달 -->
    <div v-if="showEditModal" class="edit-modal-overlay" @click="closeEditModal">
      <div class="edit-modal" @click.stop>
        <h3 class="modal-title">리뷰 수정하기</h3>
        
        <div class="rating-container">
          <span class="rating-label">평점:</span>
          <div class="stars">
            <span 
              v-for="star in 5" 
              :key="star" 
              @click="setRating(star)"
              :class="['star', { 'active': star <= editingReview.rating }]"
            >
              <i class="fas fa-star"></i>
            </span>
          </div>
        </div>
        
        <div class="content-container">
          <textarea 
            v-model="editingReview.content" 
            placeholder="여행지에 대한 경험을 공유해주세요..." 
            rows="4"
            :disabled="isSubmitting"
          ></textarea>
        </div>
        
        <div class="modal-actions">
          <button 
            @click="submitEditReview" 
            class="submit-button"
            :disabled="isSubmitting || !isEditValid"
          >
            {{ isSubmitting ? '처리 중...' : '수정하기' }}
          </button>
          
          <button 
            @click="closeEditModal" 
            class="cancel-button"
            :disabled="isSubmitting"
          >
            취소
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { useToast } from 'vue-toastification';

export default {
  name: 'UserReviews',
  data() {
    return {
      reviews: [],
      isLoading: true,
      isLoadingMore: false,
      page: 1,
      hasMore: false,
      showEditModal: false,
      editingReview: {
        id: null,
        rating: 0,
        content: ''
      },
      isSubmitting: false
    };
  },
  setup() {
    const toast = useToast();
    return { toast };
  },
  computed: {
    isEditValid() {
      return this.editingReview.rating > 0 && this.editingReview.content.trim().length > 0;
    }
  },
  mounted() {
    this.fetchReviews();
  },
  methods: {
    isAuthenticated() {
      return !!localStorage.getItem('access_token');
    },
    getToken() {
      return localStorage.getItem('access_token');
    },
    getLocationString(review) {
      const parts = [];
      
      // 백엔드에서 location 객체로 전달하는 경우
      if (review.location) {
        if (review.location.city) parts.push(review.location.city);
        if (review.location.country) parts.push(review.location.country);
      } 
      // 백엔드에서 location_city, location_country로 전달하는 경우
      else {
        if (review.location_city) parts.push(review.location_city);
        if (review.location_country) parts.push(review.location_country);
      }
      
      return parts.join(', ') || '위치 정보 없음';
    },
    async fetchReviews() {
      if (!this.isAuthenticated()) {
        this.toast.warning('로그인이 필요한 기능입니다.');
        this.$router.push('/login');
        return;
      }
      
      this.isLoading = true;
      
      try {
        const response = await axios.get('http://localhost:8000/api/destinations/user/reviews/', {
          headers: {
            Authorization: `Bearer ${this.getToken()}`
          }
        });
        
        // 리뷰 데이터 처리
        this.reviews = response.data.results.map(review => {
          // location 객체가 없고 location_id만 있는 경우 관광지 정보 가져오기
          if (review.location_id && (!review.location || !review.location.name)) {
            this.fetchLocationInfo(review);
          }
          return review;
        });
        
        this.hasMore = this.reviews.length < response.data.count;
      } catch (error) {
        console.error('리뷰 목록을 불러오는 중 오류 발생:', error);
        this.toast.error('리뷰 목록을 불러오는 중 오류가 발생했습니다.');
      } finally {
        this.isLoading = false;
      }
    },
    
    // 관광지 정보 가져오기
    async fetchLocationInfo(review) {
      try {
        const response = await axios.get(`http://localhost:8000/api/destinations/${review.location_id}/`);
        // 리뷰 객체에 관광지 정보 추가
        review.location_name = response.data.name;
        review.location_city = response.data.city;
        review.location_country = response.data.country;
      } catch (error) {
        console.error(`관광지 정보를 가져오는 중 오류 발생 (ID: ${review.location_id}):`, error);
      }
    },
    
    async loadMore() {
      if (this.isLoadingMore) return;
      
      this.isLoadingMore = true;
      this.page += 1;
      
      try {
        const response = await axios.get('http://localhost:8000/api/destinations/user/reviews/', {
          params: { page: this.page },
          headers: {
            Authorization: `Bearer ${this.getToken()}`
          }
        });
        
        this.reviews = [...this.reviews, ...response.data.results];
        this.hasMore = this.reviews.length < response.data.count;
      } catch (error) {
        console.error('추가 리뷰 목록을 불러오는 중 오류 발생:', error);
        this.toast.error('추가 리뷰 목록을 불러오는 중 오류가 발생했습니다.');
      } finally {
        this.isLoadingMore = false;
      }
    },
    
    editReview(review) {
      this.editingReview = {
        id: review.id,
        rating: review.rating,
        content: review.content,
        location_id: review.location_id || (review.location && review.location.id)
      };
      this.showEditModal = true;
    },
    
    closeEditModal() {
      this.showEditModal = false;
      this.editingReview = {
        id: null,
        rating: 0,
        content: ''
      };
    },
    
    setRating(rating) {
      if (!this.isSubmitting) {
        this.editingReview.rating = rating;
      }
    },
    
    async submitEditReview() {
      if (!this.isEditValid) {
        this.toast.warning('평점과 리뷰 내용을 모두 입력해주세요.');
        return;
      }
      
      this.isSubmitting = true;
      
      try {
        // 현재 리뷰 찾기
        const currentReview = this.reviews.find(r => r.id === this.editingReview.id);
        
        console.log('현재 리뷰 전체 객체:', JSON.stringify(currentReview, null, 2));
        console.log('리뷰 객체의 모든 키:', Object.keys(currentReview));
        
        // 리뷰 수정 요청 데이터 준비 - location_id 없이 rating과 content만 전송
        const requestData = {
          rating: this.editingReview.rating,
          content: this.editingReview.content
        };
        
        // PATCH 메서드 사용 - 부분 업데이트
        const response = await axios.patch(
          `http://localhost:8000/api/destinations/reviews/${this.editingReview.id}/`,
          requestData,
          {
            headers: {
              Authorization: `Bearer ${this.getToken()}`
            }
          }
        );
        
        // 리뷰 목록 업데이트
        const index = this.reviews.findIndex(r => r.id === this.editingReview.id);
        if (index !== -1) {
          this.reviews[index] = response.data;
        }
        
        this.toast.success('리뷰가 수정되었습니다.');
        this.closeEditModal();
      } catch (error) {
        console.error('리뷰 수정 중 오류 발생:', error);
        if (error.response) {
          console.error('오류 응답 데이터:', error.response.data);
        }
        this.toast.error('리뷰 수정 중 오류가 발생했습니다.');
      } finally {
        this.isSubmitting = false;
      }
    },
    
    async deleteReview(reviewId) {
      if (!confirm('정말로 이 리뷰를 삭제하시겠습니까?')) {
        return;
      }
      
      try {
        await axios.delete(`http://localhost:8000/api/destinations/reviews/${reviewId}/`, {
          headers: {
            Authorization: `Bearer ${this.getToken()}`
          }
        });
        
        // 리뷰 목록에서 삭제된 리뷰 제거
        this.reviews = this.reviews.filter(review => review.id !== reviewId);
        this.toast.success('리뷰가 삭제되었습니다.');
      } catch (error) {
        console.error('리뷰 삭제 중 오류 발생:', error);
        this.toast.error('리뷰 삭제 중 오류가 발생했습니다.');
      }
    },
    
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    },
    
    getSentimentClass(sentiment) {
      switch (sentiment) {
        case 'POSITIVE':
          return 'positive';
        case 'NEGATIVE':
          return 'negative';
        default:
          return 'neutral';
      }
    },
    
    getSentimentText(sentiment) {
      switch (sentiment) {
        case 'POSITIVE':
          return '긍정적';
        case 'NEGATIVE':
          return '부정적';
        default:
          return '중립적';
      }
    }
  }
};
</script>

<style scoped>
.user-reviews-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 20px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 0;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #4299e1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 40px;
  background-color: #f8fafc;
  border-radius: 8px;
  color: #718096;
}

.browse-link {
  display: inline-block;
  margin-top: 15px;
  padding: 8px 16px;
  background-color: #4299e1;
  color: white;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 500;
  transition: background-color 0.2s;
}

.browse-link:hover {
  background-color: #3182ce;
}

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.review-card {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.review-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

.destination-info {
  display: flex;
  flex-direction: column;
}

.destination-name {
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
  text-decoration: none;
  margin-bottom: 5px;
}

.destination-name:hover {
  color: #4299e1;
}

.destination-location {
  font-size: 14px;
  color: #718096;
}

.destination-location i {
  margin-right: 5px;
}

.review-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.rating {
  display: flex;
  margin-bottom: 5px;
}

.star {
  color: #cbd5e0;
  margin-right: 2px;
}

.star.filled {
  color: #f6ad55;
}

.review-date {
  font-size: 12px;
  color: #718096;
}

.review-content {
  font-size: 16px;
  line-height: 1.6;
  color: #4a5568;
  margin-bottom: 15px;
}

.review-sentiment {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  margin-bottom: 10px;
}

.review-sentiment.positive {
  background-color: #c6f6d5;
  color: #2f855a;
}

.review-sentiment.negative {
  background-color: #fed7d7;
  color: #c53030;
}

.review-sentiment.neutral {
  background-color: #e2e8f0;
  color: #4a5568;
}

.sentiment-label {
  font-weight: 500;
  margin-right: 5px;
}

.review-keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 15px;
}

.keyword-tag {
  background-color: #e2e8f0;
  color: #4a5568;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.review-actions {
  display: flex;
  gap: 10px;
}

.action-button {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 5px;
}

.action-button.edit {
  background-color: #4299e1;
  color: white;
  border: none;
}

.action-button.edit:hover {
  background-color: #3182ce;
}

.action-button.delete {
  background-color: white;
  color: #e53e3e;
  border: 1px solid #e53e3e;
}

.action-button.delete:hover {
  background-color: #fff5f5;
}

.load-more {
  text-align: center;
  margin-top: 30px;
}

.load-more-button {
  padding: 10px 20px;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #4a5568;
  cursor: pointer;
  transition: all 0.2s;
}

.load-more-button:hover:not(:disabled) {
  background-color: #f7fafc;
  border-color: #cbd5e0;
}

.load-more-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* 모달 스타일 */
.edit-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.edit-modal {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
}

.modal-title {
  font-size: 20px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 20px;
}

.rating-container {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.rating-label {
  font-size: 14px;
  font-weight: 500;
  color: #4a5568;
  margin-right: 10px;
}

.stars {
  display: flex;
}

.star {
  font-size: 20px;
  color: #cbd5e0;
  cursor: pointer;
  margin-right: 5px;
  transition: color 0.2s;
}

.star:hover,
.star.active {
  color: #f6ad55;
}

.content-container {
  margin-bottom: 20px;
}

textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  resize: vertical;
  transition: border-color 0.2s;
}

textarea:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
}

textarea:disabled {
  background-color: #f7fafc;
  cursor: not-allowed;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.submit-button,
.cancel-button {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.submit-button {
  background-color: #4299e1;
  color: white;
  border: none;
}

.submit-button:hover:not(:disabled) {
  background-color: #3182ce;
}

.submit-button:disabled {
  background-color: #a0aec0;
  cursor: not-allowed;
}

.cancel-button {
  background-color: white;
  color: #4a5568;
  border: 1px solid #e2e8f0;
}

.cancel-button:hover:not(:disabled) {
  background-color: #f7fafc;
  border-color: #cbd5e0;
}

.cancel-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .review-header {
    flex-direction: column;
    gap: 10px;
  }
  
  .review-meta {
    align-items: flex-start;
  }
}
</style> 