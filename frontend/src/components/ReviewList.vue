<template>
  <div class="review-list-container">
    <h3 class="section-title">리뷰 ({{ reviews.length }})</h3>
    
    <div v-if="isLoading" class="loading-container">
      <div class="spinner"></div>
      <p>리뷰를 불러오는 중...</p>
    </div>
    
    <div v-else-if="reviews.length === 0" class="empty-state">
      <p>아직 리뷰가 없습니다. 첫 번째 리뷰를 작성해보세요!</p>
    </div>
    
    <div v-else class="reviews">
      <div v-for="review in reviews" :key="review.id" class="review-card">
        <div class="review-header">
          <div class="user-info">
            <span class="username">{{ review.user.username }}</span>
            <div class="rating">
              <span v-for="star in 5" :key="star" class="star" :class="{ 'filled': star <= review.rating }">
                <i class="fas fa-star"></i>
              </span>
            </div>
          </div>
          <div class="review-meta">
            <span class="date">{{ formatDate(review.created_at) }}</span>
            <div v-if="isCurrentUserReview(review)" class="review-actions">
              <button @click="editReview(review)" class="action-button edit">
                <i class="fas fa-edit"></i>
              </button>
              <button @click="deleteReview(review)" class="action-button delete">
                <i class="fas fa-trash"></i>
              </button>
            </div>
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
      </div>
    </div>
    
    <div v-if="hasMoreReviews" class="load-more">
      <button @click="loadMoreReviews" :disabled="isLoadingMore" class="load-more-button">
        {{ isLoadingMore ? '불러오는 중...' : '더 보기' }}
      </button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { useToast } from 'vue-toastification';

export default {
  name: 'ReviewList',
  props: {
    locationId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      reviews: [],
      isLoading: true,
      isLoadingMore: false,
      page: 1,
      hasMoreReviews: false
    };
  },
  setup() {
    const toast = useToast();
    return { toast };
  },
  computed: {
    currentUserId() {
      // 로컬 스토리지에서 사용자 ID를 가져오는 로직으로 변경
      // 현재는 간단히 null을 반환하고, 실제 구현은 백엔드 API를 통해 사용자 정보를 가져오는 방식으로 해야 함
      return null;
    }
  },
  mounted() {
    this.fetchReviews();
  },
  methods: {
    async fetchReviews() {
      this.isLoading = true;
      
      try {
        const response = await axios.get(`http://localhost:8000/api/destinations/${this.locationId}/reviews/`);
        this.reviews = response.data.results;
        this.hasMoreReviews = this.reviews.length < response.data.count;
      } catch (error) {
        console.error('리뷰 목록을 불러오는 중 오류 발생:', error);
        this.toast.error('리뷰 목록을 불러오는 중 오류가 발생했습니다.');
      } finally {
        this.isLoading = false;
      }
    },
    
    async loadMoreReviews() {
      if (this.isLoadingMore) return;
      
      this.isLoadingMore = true;
      this.page += 1;
      
      try {
        const response = await axios.get(`http://localhost:8000/api/destinations/${this.locationId}/reviews/`, {
          params: { page: this.page }
        });
        
        this.reviews = [...this.reviews, ...response.data.results];
        this.hasMoreReviews = this.reviews.length < response.data.count;
      } catch (error) {
        console.error('추가 리뷰를 불러오는 중 오류 발생:', error);
        this.toast.error('추가 리뷰를 불러오는 중 오류가 발생했습니다.');
      } finally {
        this.isLoadingMore = false;
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
    
    isCurrentUserReview(review) {
      return this.currentUserId && review.user.id === this.currentUserId;
    },
    
    editReview(review) {
      this.$emit('edit-review', review);
    },
    
    async deleteReview(review) {
      if (!confirm('정말로 이 리뷰를 삭제하시겠습니까?')) {
        return;
      }
      
      try {
        const token = localStorage.getItem('access_token');
        await axios.delete(`http://localhost:8000/api/destinations/reviews/${review.id}/`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        
        // 리뷰 목록에서 삭제된 리뷰 제거
        this.reviews = this.reviews.filter(r => r.id !== review.id);
        this.toast.success('리뷰가 삭제되었습니다.');
      } catch (error) {
        console.error('리뷰 삭제 중 오류 발생:', error);
        this.toast.error('리뷰 삭제 중 오류가 발생했습니다.');
      }
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
.review-list-container {
  margin-top: 30px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 20px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px 0;
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
  padding: 30px;
  background-color: #f8fafc;
  border-radius: 8px;
  color: #718096;
}

.reviews {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.review-card {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.review-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.username {
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 5px;
}

.rating {
  display: flex;
}

.star {
  color: #cbd5e0;
  margin-right: 2px;
}

.star.filled {
  color: #f6ad55;
}

.review-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.date {
  font-size: 12px;
  color: #718096;
  margin-bottom: 5px;
}

.review-actions {
  display: flex;
  gap: 5px;
}

.action-button {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  padding: 2px 5px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.action-button.edit {
  color: #4299e1;
}

.action-button.edit:hover {
  background-color: #ebf8ff;
}

.action-button.delete {
  color: #e53e3e;
}

.action-button.delete:hover {
  background-color: #fff5f5;
}

.review-content {
  font-size: 14px;
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
  margin-top: 10px;
}

.keyword-tag {
  background-color: #e2e8f0;
  color: #4a5568;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.load-more {
  text-align: center;
  margin-top: 20px;
}

.load-more-button {
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 14px;
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
</style> 