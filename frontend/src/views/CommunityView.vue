<template>
  <div>
    <h1>Community</h1>
    <router-link to="/community/new">Create New</router-link>
    <ul>
      <li v-for="post in posts" :key="post.id">
        <router-link :to="`/community/${post.id}`">
          {{ post.title }}
        </router-link>
        <span> - Writer: {{ post.author }}</span>
      </li>
    </ul>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return { posts: [] };
  },
  async created() {
    try {
      const response = await axios.get('/api/community/posts/'); // ✅ Django의 API 경로 맞추기
      this.posts = response.data;
    } catch (error) {
      console.error("🚨 게시글을 불러오는 중 오류 발생:", error);
    }
  }
};
</script>
