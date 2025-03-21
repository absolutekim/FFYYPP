<template>
  <v-container class="post-list-container">
    <v-row justify="center">
      <v-col cols="12" md="8">
        <v-card class="post-list-card" elevation="4">
          <v-card-title class="text-center text-h4 font-weight-bold primary--text">
            Community Posts
          </v-card-title>

          <v-card-text>
            <v-btn
              color="primary"
              block
              large
              class="mb-6"
              @click="goToNewPost"
            >
              <v-icon left>mdi-plus</v-icon>
              Create New Post
            </v-btn>

            <v-list>
              <v-list-item
                v-for="post in posts"
                :key="post.id"
                :to="'/community/' + post.id"
                class="post-item"
                ripple
                @click="goToPost(post.id)"
              >
                <v-list-item-content>
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
                </v-list-item-content>
              </v-list-item>
            </v-list>
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
      posts: []
    };
  },
  async created() {
    try {
      const response = await axios.get('http://localhost:8000/api/posts/');
      this.posts = response.data;
    } catch (error) {
      console.error("🚨 게시글을 불러오는 중 오류 발생:", error);
    }
  },
  methods: {
    goToNewPost() {
      this.$router.push('/community/new');
    },
    goToPost(id) {
      this.$router.push('/community/' + id);
    },
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
    }
  }
};
</script>

<style scoped>
.post-list-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f6f9fc 0%, #eef2f7 100%);
  padding: 40px 0;
}

.post-list-card {
  border-radius: 12px;
  overflow: hidden;
}

.post-item {
  transition: transform 0.2s;
  border-bottom: 1px solid #eee;
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
}

.v-list-item-subtitle {
  color: #666;
  font-size: 0.9rem;
}

.v-btn {
  text-transform: none;
  letter-spacing: 0.5px;
}
</style>
