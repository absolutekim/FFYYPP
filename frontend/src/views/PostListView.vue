<template>
  <div>
    <h1>커뮤니티 게시글</h1>
    
    <!-- ✅ 게시글 작성 버튼 추가 -->
    <button @click="goToNewPost">➕ 새 글 작성</button>

    <ul>
      <li v-for="post in posts" :key="post.id">
        <router-link :to="'/community/' + post.id">{{ post.title }}</router-link>
        <p>작성자: {{ post.author }}</p>
      </li>
    </ul>
  </div>
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
    const response = await axios.get('http://localhost:8000/api/posts/');  // ✅ 경로 확인
    this.posts = response.data;
  } catch (error) {
    console.error("🚨 게시글을 불러오는 중 오류 발생:", error);
  }
},
  methods: {
    goToNewPost() {
      this.$router.push('/community/new');  // ✅ 게시글 작성 페이지로 이동
    }
  }
};
</script>

<style scoped>
h1 {
  text-align: center;
}
button {
  display: block;
  margin: 10px auto;
  padding: 10px 15px;
  font-size: 16px;
  cursor: pointer;
}
ul {
  list-style: none;
  padding: 0;
}
li {
  margin: 10px 0;
}
</style>
