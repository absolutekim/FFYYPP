<template>
  <v-container class="community-container">
    <v-row justify="center">
      <v-col cols="12" md="8">
        <v-card class="community-card" elevation="4">
          <v-card-title class="text-center text-h4 font-weight-bold primary--text">
            커뮤니티
          </v-card-title>

          <v-card-text>
            <v-btn
              color="primary"
              block
              large
              class="mb-6"
              @click="$router.push('/community/new')"
            >
              <v-icon left>mdi-plus</v-icon>
              새 글 작성
            </v-btn>

            <v-list class="post-list">
              <v-list-item
                v-for="post in paginatedPosts"
                :key="post.id"
                :to="`/community/${post.id}`"
                class="post-item"
                ripple
                @click="$router.push(`/community/${post.id}`)"
              >
                <template v-slot:default>
                  <v-list-item-title class="text-h6 mb-2">
                    {{ post.title }}
                  </v-list-item-title>
                  <v-list-item-subtitle class="d-flex align-center">
                    <v-icon small class="mr-1">mdi-account</v-icon>
                    {{ post.author }}
                    <v-spacer></v-spacer>
                    <v-icon small class="mr-1">mdi-clock-outline</v-icon>
                    {{ formatDate(post.created_at) }}
                  </v-list-item-subtitle>
                </template>
              </v-list-item>
            </v-list>

            <v-pagination
              v-model="currentPage"
              :length="totalPages"
              :total-visible="7"
              color="primary"
              class="mt-4"
              @update:model-value="handlePageChange"
            ></v-pagination>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return { 
      posts: [],
      loading: false,
      currentPage: 1,
      itemsPerPage: 10
    };
  },
  computed: {
    totalPages() {
      return Math.ceil(this.posts.length / this.itemsPerPage);
    },
    paginatedPosts() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.posts.slice(start, end);
    }
  },
  async created() {
    this.loading = true;
    try {
      const response = await axios.get('/api/community/posts/');
      this.posts = response.data;
    } catch (error) {
      console.error("🚨 게시글을 불러오는 중 오류 발생:", error);
    } finally {
      this.loading = false;
    }
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    handlePageChange(page) {
      this.currentPage = page;
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }
};
</script>

<style scoped>
.community-container {
  background-image: url('@/assets/commback.jpg');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  min-height: 100vh;
  overflow-x: hidden;
  width: 100%;
  margin: 0;
  padding: 0;
}

.v-container {
  margin: 0;
  padding: 0;
  max-width: 100% !important;
}

.community-card {
  border-radius: 12px;
  overflow: hidden;
}

.post-list {
  max-height: 600px;
  overflow-y: auto;
  overflow-x: hidden;
}

.post-item {
  transition: all 0.3s ease;
  border-bottom: 1px solid #eee;
  margin-bottom: 4px;
}

.post-item:last-child {
  border-bottom: none;
}

.post-item:hover {
  transform: translateX(8px);
  background-color: #f5f5f5;
}

.v-list-item-title {
  color: #333;
  font-weight: 500;
  line-height: 1.4;
}

.v-list-item-subtitle {
  color: #666;
  font-size: 0.9rem;
}

.v-btn {
  text-transform: none;
  letter-spacing: 0.5px;
}

.v-card-title {
  padding: 24px 16px;
  border-bottom: 2px solid #eee;
}

.v-card-text {
  padding: 24px 16px;
}

.v-pagination {
  justify-content: center;
}

.v-row {
  margin: 0 !important;
}
</style>
