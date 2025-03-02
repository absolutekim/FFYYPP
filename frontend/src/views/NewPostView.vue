<template>
  <div>
    <h1>새 게시글 작성</h1>
    <form @submit.prevent="createPost">
      <label>제목:</label>
      <input type="text" v-model="title" required>
      <label>내용:</label>
      <textarea v-model="content" required></textarea>
      <button type="submit">작성</button>
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
  methods: {
    async createPost() {
  try {
    const userId = localStorage.getItem('user_id'); // ✅ 로그인한 유저 ID 가져오기
    const response = await axios.post(`http://localhost:8000/api/community/posts/`, {
      title: this.title,
      content: this.content,
      author_id: userId // ✅ 추가된 부분
    });

    console.log("✅ 게시글 작성 성공:", response.data);
    this.$router.push('/community');  // ✅ 게시글 목록으로 이동
  } catch (error) {
    console.error("🚨 게시글 작성 실패:", error);
  }
}
  }
};
</script>
