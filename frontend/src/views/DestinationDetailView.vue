<template>
  <v-container class="destination-detail-container">
    <v-row justify="center">
      <v-col cols="12" md="8">
        <v-card class="destination-detail-card" elevation="4">
          <!-- Loading state -->
          <v-card v-if="loading" class="text-center pa-6">
            <v-progress-circular indeterminate color="primary"></v-progress-circular>
            <div class="mt-4">🔄 Loading data...</div>
          </v-card>

          <!-- Error state -->
          <v-alert v-else-if="error" type="error" class="text-center">
            🚨 Error: {{ error }}
          </v-alert>

          <!-- Data display -->
          <template v-else>
            <!-- Header image -->
            <v-img
              v-if="destination.image"
              :src="destination.image"
              height="300"
              cover
              class="destination-detail-image"
            ></v-img>

            <!-- Title section -->
            <v-card-title class="text-h4 font-weight-bold d-flex align-center flex-wrap">
              {{ destination.name }}
              <v-chip
                color="info"
                variant="outlined"
                class="ml-2"
              >
                {{ destination.country }}
              </v-chip>
            </v-card-title>

            <!-- 좋아요 버튼 추가 -->
            <div class="like-button-container px-4">
              <like-button 
                :location-id="Number(destination.id)" 
                :initial-liked="destination.user_has_liked"
                @like-changed="onLikeChanged"
              />
            </div>

            <v-card-text>
              <!-- Basic information -->
              <v-row>
                <v-col cols="12">
                  <h3 class="text-h6 mb-3">Basic Information</h3>
                  <v-chip
                    color="primary"
                    variant="outlined"
                    class="mr-2 mb-2"
                  >
                    {{ destination.type }}
                  </v-chip>
                  
                  <div v-if="destination.subcategories" class="my-2">
                    <v-chip
                      v-for="(subcat, index) in destination.subcategories"
                      :key="index"
                      color="secondary"
                      variant="outlined"
                      class="mr-2 mb-2"
                    >
                      {{ subcat }}
                    </v-chip>
                  </div>

                  <div v-if="destination.subtypes" class="my-2">
                    <v-chip
                      v-for="(subtype, index) in destination.subtypes"
                      :key="index"
                      color="success"
                      variant="outlined"
                      class="mr-2 mb-2"
                    >
                      {{ subtype }}
                    </v-chip>
                  </div>

                  <div v-if="destination.description" class="mt-4 text-body-1">
                    {{ destination.description }}
                  </div>
                </v-col>

                <!-- Address information -->
                <v-col cols="12" md="6">
                  <h3 class="text-h6 mb-3">Address Information</h3>
                  <v-list>
                    <v-list-item v-if="destination.address">
                      <template v-slot:prepend>
                        <v-icon color="primary">mdi-map-marker</v-icon>
                      </template>
                      <v-list-item-title>Address</v-list-item-title>
                      <v-list-item-subtitle>{{ destination.address }}</v-list-item-subtitle>
                    </v-list-item>

                    <v-list-item v-if="destination.local_address">
                      <template v-slot:prepend>
                        <v-icon color="primary">mdi-map-marker-outline</v-icon>
                      </template>
                      <v-list-item-title>Local Address</v-list-item-title>
                      <v-list-item-subtitle>{{ destination.local_address }}</v-list-item-subtitle>
                    </v-list-item>

                    <v-list-item v-if="destination.city || destination.state">
                      <template v-slot:prepend>
                        <v-icon color="primary">mdi-city</v-icon>
                      </template>
                      <v-list-item-title>City/State</v-list-item-title>
                      <v-list-item-subtitle>
                        {{ [destination.city, destination.state].filter(Boolean).join(', ') }}
                      </v-list-item-subtitle>
                    </v-list-item>

                    <v-list-item v-if="destination.postal_code">
                      <template v-slot:prepend>
                        <v-icon color="primary">mdi-post</v-icon>
                      </template>
                      <v-list-item-title>Postal Code</v-list-item-title>
                      <v-list-item-subtitle>{{ destination.postal_code }}</v-list-item-subtitle>
                    </v-list-item>

                    <v-list-item v-if="destination.street1 || destination.street2">
                      <template v-slot:prepend>
                        <v-icon color="primary">mdi-road-variant</v-icon>
                      </template>
                      <v-list-item-title>Street Address</v-list-item-title>
                      <v-list-item-subtitle>
                        {{ [destination.street1, destination.street2].filter(Boolean).join(' ') }}
                      </v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </v-col>

                <!-- Contact and location information -->
                <v-col cols="12" md="6">
                  <h3 class="text-h6 mb-3">Additional Information</h3>
                  <v-list>
                    <v-list-item v-if="destination.website">
                      <template v-slot:prepend>
                        <v-icon color="primary">mdi-web</v-icon>
                      </template>
                      <v-list-item-title>Website</v-list-item-title>
                      <v-list-item-subtitle>
                        <a :href="destination.website" target="_blank">{{ destination.website }}</a>
                      </v-list-item-subtitle>
                    </v-list-item>

                    <v-list-item v-if="destination.email">
                      <template v-slot:prepend>
                        <v-icon color="primary">mdi-email</v-icon>
                      </template>
                      <v-list-item-title>Email</v-list-item-title>
                      <v-list-item-subtitle>
                        <a :href="`mailto:${destination.email}`">{{ destination.email }}</a>
                      </v-list-item-subtitle>
                    </v-list-item>

                    <v-list-item v-if="destination.latitude && destination.longitude">
                      <template v-slot:prepend>
                        <v-icon color="primary">mdi-crosshairs-gps</v-icon>
                      </template>
                      <v-list-item-title>Coordinates</v-list-item-title>
                      <v-list-item-subtitle>
                        {{ destination.latitude }}, {{ destination.longitude }}
                      </v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </v-col>
              </v-row>

              <!-- 리뷰 섹션 추가 -->
              <v-row class="mt-4">
                <v-col cols="12">
                  <h3 class="text-h6 mb-3">리뷰</h3>
                  
                  <!-- 리뷰 작성 폼 -->
                  <div v-if="isAuthenticated && !isEditingReview">
                    <review-form 
                      :location-id="Number(destination.id)" 
                      @review-submitted="onReviewSubmitted"
                      ref="reviewForm"
                    />
                  </div>
                  
                  <!-- 리뷰 수정 폼 -->
                  <div v-if="isEditingReview">
                    <review-form 
                      :location-id="Number(destination.id)" 
                      :existing-review="currentEditingReview"
                      @review-submitted="onReviewUpdated"
                      @cancel="cancelEditReview"
                      ref="editReviewForm"
                    />
                  </div>
                  
                  <!-- 리뷰 목록 -->
                  <review-list 
                    :location-id="Number(destination.id)" 
                    @edit-review="startEditReview"
                    ref="reviewList"
                  />
                </v-col>
              </v-row>
            </v-card-text>

            <!-- Back button -->
            <v-card-actions class="pa-4">
              <v-btn
                color="primary"
                variant="outlined"
                block
                @click="$router.push('/destinations')"
              >
                <v-icon left>mdi-arrow-left</v-icon>
                Back to List
              </v-btn>
            </v-card-actions>
          </template>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios';
import LikeButton from '@/components/LikeButton.vue';
import ReviewForm from '@/components/ReviewForm.vue';
import ReviewList from '@/components/ReviewList.vue';

export default {
  components: {
    LikeButton,
    ReviewForm,
    ReviewList
  },
  data() {
    return {
      destination: {},
      loading: true,
      error: null,
      isEditingReview: false,
      currentEditingReview: null
    };
  },
  computed: {
    isAuthenticated() {
      return !!localStorage.getItem('access_token');
    }
  },
  async created() {
    try {
      // 인증 토큰이 있으면 헤더에 추가
      const token = localStorage.getItem('access_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      
      const response = await axios.get(`http://localhost:8000/api/destinations/${this.$route.params.id}/`, {
        headers
      });
      this.destination = response.data;
      console.log('여행지 상세 정보:', this.destination);
    } catch (err) {
      this.error = err.message;
      console.error("🚨 Failed to load data:", err);
    } finally {
      this.loading = false;
    }
  },
  methods: {
    onLikeChanged(isLiked) {
      this.destination.user_has_liked = isLiked;
    },
    onReviewSubmitted(review) {
      console.log('리뷰 제출됨:', review);
      // 리뷰 목록 새로고침
      if (this.$refs.reviewList) {
        this.$refs.reviewList.fetchReviews();
      }
    },
    startEditReview(review) {
      console.log('리뷰 수정 시작:', review);
      this.isEditingReview = true;
      this.currentEditingReview = review;
    },
    cancelEditReview() {
      console.log('리뷰 수정 취소');
      this.isEditingReview = false;
      this.currentEditingReview = null;
    },
    onReviewUpdated(review) {
      console.log('리뷰 업데이트됨:', review);
      // 리뷰 목록 새로고침
      if (this.$refs.reviewList) {
        this.$refs.reviewList.fetchReviews();
      }
      this.isEditingReview = false;
      this.currentEditingReview = null;
    }
  }
};
</script>

<style scoped>
.destination-detail-container {
  padding-top: 2rem;
  padding-bottom: 2rem;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.destination-detail-card {
  border-radius: 12px;
  overflow: hidden;
}

.destination-detail-image {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.v-card-title {
  padding: 1.5rem;
  background-color: white;
}

.v-card-text {
  padding: 1.5rem;
}

.like-button-container {
  margin: 0 0 10px 0;
}

a {
  color: #1976d2;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

@media (max-width: 600px) {
  .destination-detail-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
  }
}
</style> 