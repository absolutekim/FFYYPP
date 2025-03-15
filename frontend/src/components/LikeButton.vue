<template>
  <div class="like-button-container">
    <button 
      @click="toggleLike" 
      :class="['like-button', { 'liked': isLiked }]"
      :disabled="isLoading"
    >
      <i :class="['fas', isLiked ? 'fa-heart' : 'fa-heart-o']"></i>
      <span>{{ isLiked ? '좋아요 취소' : '좋아요' }}</span>
    </button>
  </div>
</template>

<script>
import axios from 'axios';
import { useToast } from 'vue-toastification';

export default {
  name: 'LikeButton',
  props: {
    locationId: {
      type: Number,
      required: true
    },
    initialLiked: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      isLiked: this.initialLiked,
      isLoading: false
    };
  },
  setup() {
    const toast = useToast();
    return { toast };
  },
  watch: {
    // 부모 컴포넌트에서 initialLiked가 변경되면 isLiked 업데이트
    initialLiked: {
      immediate: true,
      handler(newValue) {
        console.log('initialLiked 변경됨:', newValue);
        this.isLiked = newValue;
      }
    }
  },
  methods: {
    isAuthenticated() {
      return !!localStorage.getItem('access_token');
    },
    getToken() {
      return localStorage.getItem('access_token');
    },
    async toggleLike() {
      if (!this.isAuthenticated()) {
        this.toast.warning('로그인이 필요한 기능입니다.');
        this.$router.push('/login');
        return;
      }

      this.isLoading = true;

      try {
        if (this.isLiked) {
          // 좋아요 취소
          await axios.delete(`http://localhost:8000/api/destinations/likes/unlike/`, {
            params: { location_id: this.locationId },
            headers: {
              Authorization: `Bearer ${this.getToken()}`
            }
          });
          this.isLiked = false;
          this.toast.success('좋아요가 취소되었습니다.');
        } else {
          // 좋아요 추가
          try {
            await axios.post(`http://localhost:8000/api/destinations/likes/`, 
              { location_id: this.locationId },
              {
                headers: {
                  Authorization: `Bearer ${this.getToken()}`
                }
              }
            );
            this.isLiked = true;
            this.toast.success('좋아요가 추가되었습니다.');
          } catch (error) {
            // 이미 좋아요한 경우 (409 Conflict)
            if (error.response && error.response.status === 409) {
              this.isLiked = true; // 이미 좋아요 상태로 설정
              this.toast.info('이미 좋아요한 여행지입니다.');
            } else {
              throw error; // 다른 오류는 다시 던짐
            }
          }
        }
        
        // 부모 컴포넌트에 이벤트 발생
        this.$emit('like-changed', this.isLiked);
      } catch (error) {
        console.error('좋아요 처리 중 오류 발생:', error);
        if (error.response && error.response.status === 409) {
          this.isLiked = true; // 이미 좋아요 상태로 설정
          this.toast.info('이미 좋아요한 여행지입니다.');
        } else {
          this.toast.error('좋아요 처리 중 오류가 발생했습니다.');
        }
      } finally {
        this.isLoading = false;
      }
    }
  }
};
</script>

<style scoped>
.like-button-container {
  margin: 10px 0;
}

.like-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 16px;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #4a5568;
  cursor: pointer;
  transition: all 0.2s;
}

.like-button:hover {
  background-color: #f7fafc;
  border-color: #cbd5e0;
}

.like-button.liked {
  background-color: #fed7d7;
  border-color: #fc8181;
  color: #e53e3e;
}

.like-button.liked:hover {
  background-color: #fecaca;
}

.like-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.like-button i {
  font-size: 16px;
}
</style> 