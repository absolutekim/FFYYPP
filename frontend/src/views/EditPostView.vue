<template>
  <div>
    <h1>Modify Post</h1>
    <form @submit.prevent="updatePost">
      <label>Title:</label>
      <input type="text" v-model="title" required>
      <label>Content:</label>
      <textarea v-model="content" required></textarea>
      <button type="submit">Upload Post</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      title: '',
      content: ''
    };
  },
  async created() {
    const postId = this.$route.params.id;
    const response = await axios.get(`/api/posts/${postId}/`);
    this.title = response.data.title;
    this.content = response.data.content;
  },
  methods: {
    async updatePost() {
      if (!this.title.trim() || !this.content.trim()) return;
      await axios.put(`/api/posts/${this.$route.params.id}/`, {
        title: this.title,
        content: this.content
      });
      this.$router.push(`/community/${this.$route.params.id}`);
    }
  }
};
</script>
