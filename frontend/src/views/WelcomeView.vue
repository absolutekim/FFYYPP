<template>
  <p></p>
  <div class="displayBox" data-aos="fade-up">  <p class="large-text">Welcome to Travel Kim.</p></div>
</template>

<style scoped>
.large-text {
  font-size: 50px; /* 원하는 크기로 조절 */
  font-weight: bold; /* 글자를 두껍게 */
  color: #333; /* 글자색 설정 */
  margin-top: 50px; /* 50px만큼 아래로 이동 */
}
</style>

<script>
import axios from 'axios';

export default {
  data() {
    return { message: 'Loading...' };
  },
  watch: {
    '$route'() { // ✅ 페이지 이동 시마다 토큰 재확인
      this.checkAuth();
    },
    isAuthenticated(newVal) {  // ✅ `oldVal` 제거
      if (newVal) {
        this.fetchData();
      }
    }
  },
  computed: {
    isAuthenticated() {
      return !!localStorage.getItem('access_token'); // ✅ 토큰 여부 확인
    }
  },
  async created() {
    await this.checkAuth();
    await this.fetchData();
  },
  methods: {
    async checkAuth() {
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.warn("🚨 No JWT token found! Redirecting to login...");
        this.$router.push('/login');
        return false;
      }
      console.log("✅ JWT token found:", token);
      return true;
    },
    async fetchData() {
      try {
        const isAuthenticated = await this.checkAuth();
        if (!isAuthenticated) return; // ✅ 인증되지 않으면 fetchData 실행 중단

        const response = await axios.get('http://localhost:8000/api/welcome/', {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });

        console.log("✅ API 요청 성공:", response.data);
        this.message = response.data.message;
      } catch (error) {
        console.error('🚨 API 요청 실패:', error);
        if (error.response && error.response.status === 401) {
          console.warn("⚠️ JWT 토큰이 만료되었거나 유효하지 않음. 로그인 페이지로 이동합니다.");
          localStorage.removeItem("access_token");
          this.$router.push('/login');
        }
      }
    }
  }
};
</script>
