<template>
  <div class="review-form-container">
    <h3 class="form-title">{{ existingReview ? '리뷰 수정하기' : '리뷰 작성하기' }}</h3>
    
    <div class="rating-section">
      <div class="rating-label">평점 선택:</div>
      
      <!-- 별점 선택 라디오 버튼 -->
      <div class="rating-options">
        <div 
          v-for="rating in 5" 
          :key="rating" 
          class="rating-option"
          @click="setRating(rating)"
        >
          <input 
            type="radio" 
            :id="`rating-${rating}`" 
            name="rating" 
            :value="rating" 
            :checked="review.rating === rating"
          />
          <label :for="`rating-${rating}`" class="rating-label-option">
            {{ rating }}점
            <span class="star-icon" :class="{ 'active': rating <= review.rating }">
              <i class="fas fa-star"></i>
            </span>
          </label>
        </div>
      </div>
      
      <div class="selected-rating" v-if="review.rating > 0">
        선택한 평점: <strong>{{ review.rating }}점</strong>
      </div>
      
      <div v-else class="rating-hint">
        ⚠️ 평점을 선택해주세요 (1-5)
      </div>
    </div>
    
    <div class="content-container">
      <label for="review-content" class="content-label">리뷰 내용:</label>
      <textarea 
        id="review-content"
        v-model="review.content" 
        placeholder="여행지에 대한 경험을 공유해주세요..." 
        rows="4"
        :disabled="isLoading"
      ></textarea>
    </div>
    
    <div class="form-actions">
      <button 
        @click="submitReview" 
        class="submit-button"
        :disabled="isLoading || !isValid"
      >
        {{ isLoading ? '처리 중...' : (existingReview ? '수정하기' : '작성하기') }}
      </button>
      
      <button 
        v-if="existingReview" 
        @click="$emit('cancel')" 
        class="cancel-button"
        :disabled="isLoading"
      >
        취소
      </button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { useToast } from 'vue-toastification';

export default {
  name: 'ReviewForm',
  props: {
    locationId: {
      type: Number,
      required: true
    },
    existingReview: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      review: {
        rating: this.existingReview ? this.existingReview.rating : 0,
        content: this.existingReview ? this.existingReview.content : ''
      },
      isLoading: false
    };
  },
  mounted() {
    console.log('ReviewForm mounted - locationId:', this.locationId);
    console.log('ReviewForm mounted - existingReview:', this.existingReview);
    console.log('ReviewForm mounted - initial rating:', this.review.rating);
    console.log('ReviewForm mounted - initial content:', this.review.content);
  },
  setup() {
    const toast = useToast();
    return { toast };
  },
  computed: {
    isValid() {
      const valid = this.review.rating > 0 && this.review.content.trim().length > 0;
      console.log('Rating:', this.review.rating, 'Content length:', this.review.content.trim().length, 'isValid:', valid);
      return valid;
    }
  },
  methods: {
    setRating(rating) {
      console.log('Setting rating to:', rating);
      if (!this.isLoading) {
        this.review.rating = rating;
        console.log('Rating after setting:', this.review.rating);
      }
    },
    
    async submitReview() {
      console.log('submitReview 호출됨');
      console.log('현재 리뷰 상태:', this.review);
      
      if (!localStorage.getItem('access_token')) {
        this.toast.warning('로그인이 필요한 기능입니다.');
        this.$router.push('/login');
        return;
      }
      
      if (!this.isValid) {
        console.log('유효성 검사 실패');
        console.log('Rating:', this.review.rating, 'Content length:', this.review.content.trim().length);
        this.toast.warning('평점과 리뷰 내용을 모두 입력해주세요.');
        return;
      }
      
      this.isLoading = true;
      console.log('리뷰 데이터 전송 시작');
      
      try {
        const reviewData = {
          location_id: this.locationId,
          rating: this.review.rating,
          content: this.review.content
        };
        
        console.log('전송할 리뷰 데이터:', reviewData);
        
        let response;
        const token = localStorage.getItem('access_token');
        
        if (this.existingReview) {
          // 리뷰 수정
          console.log('기존 리뷰 수정 중...');
          response = await axios.put(
            `http://localhost:8000/api/destinations/reviews/${this.existingReview.id}/`,
            reviewData,
            {
              headers: {
                Authorization: `Bearer ${token}`
              }
            }
          );
          this.toast.success('리뷰가 수정되었습니다.');
        } else {
          // 새 리뷰 작성
          console.log('새 리뷰 작성 중...');
          response = await axios.post(
            'http://localhost:8000/api/destinations/reviews/',
            reviewData,
            {
              headers: {
                Authorization: `Bearer ${token}`
              }
            }
          );
          console.log('리뷰 작성 응답:', response.data);
          this.toast.success('리뷰가 작성되었습니다.');
        }
        
        // 부모 컴포넌트에 이벤트 발생
        this.$emit('review-submitted', response.data);
        
        // 폼 초기화 (새 리뷰 작성 시)
        if (!this.existingReview) {
          this.review.rating = 0;
          this.review.content = '';
        }
      } catch (error) {
        console.error('리뷰 제출 중 오류 발생:', error);
        if (error.response) {
          console.error('오류 응답:', error.response.data);
        }
        this.toast.error('리뷰 제출 중 오류가 발생했습니다.');
      } finally {
        this.isLoading = false;
      }
    }
  }
};
</script>

<style scoped>
.review-form-container {
  background-color: #f8fafc;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.form-title {
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 15px;
}

.rating-section {
  margin-bottom: 20px;
}

.rating-label {
  font-size: 14px;
  font-weight: 500;
  color: #4a5568;
  margin-bottom: 10px;
}

.rating-options {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 10px;
}

.rating-option {
  display: flex;
  align-items: center;
}

.rating-option input[type="radio"] {
  margin-right: 5px;
}

.rating-label-option {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 14px;
  color: #4a5568;
}

.star-icon {
  margin-left: 5px;
  color: #cbd5e0;
  transition: color 0.2s;
}

.star-icon.active {
  color: #f6ad55;
}

.selected-rating {
  margin-top: 10px;
  font-size: 14px;
  color: #4a5568;
}

.rating-hint {
  font-size: 13px;
  color: #e53e3e;
  margin-top: 5px;
}

.content-container {
  margin-bottom: 15px;
}

.content-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #4a5568;
  margin-bottom: 5px;
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

.form-actions {
  display: flex;
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
</style> 