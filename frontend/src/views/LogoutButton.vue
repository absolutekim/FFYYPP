<template>
  <button @click="logout">로그아웃</button>
</template>

<script>
import axios from 'axios';  // ✅ axios import 추가

export default {
  methods: {
  logout() {
    localStorage.removeItem('access_token');  // ✅ 토큰 삭제
    localStorage.removeItem('refresh_token');

    // ✅ 로그아웃 후 Authorization 헤더 제거
    delete axios.defaults.headers.common['Authorization'];

    alert("로그아웃 되었습니다.");
    this.$router.push('/login');  // ✅ 로그인 페이지로 이동
  }
}
};
</script>
