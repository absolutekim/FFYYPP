<template>
  <nav>
    <ul>
      <li><router-link to="/">홈</router-link></li>
      <li v-if="isAuthenticated"><router-link to="/community">Community</router-link></li>
      <li v-if="isAuthenticated"><router-link to="/flights">Flight</router-link></li> <!-- ✅ 추가됨 -->
      <li v-if="!isAuthenticated"><router-link to="/register">Register</router-link></li>
      <li v-if="!isAuthenticated"><router-link to="/login">Login</router-link></li>
      <li v-if="isAuthenticated"><button @click="logout">Logout</button></li>
    </ul>
  </nav>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AppNavbar',
  data() {
    return {
      isAuthenticated: !!localStorage.getItem('access_token'), // ✅ 로그인 상태 확인
    };
  },
  methods: {
    checkAuth() {
      this.isAuthenticated = !!localStorage.getItem('access_token');
    },
    logout() {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      delete axios.defaults.headers.common['Authorization'];

      alert("Successfully Logged Out.");
      this.isAuthenticated = false; // ✅ 즉시 UI 반영
      this.$router.push('/login');
    }
  },
  mounted() {
    window.addEventListener('storage', this.checkAuth); // ✅ 로그인/로그아웃 상태 실시간 업데이트
    document.addEventListener('auth-changed', this.checkAuth); // ✅ 커스텀 이벤트 감지
  },
  beforeUnmount() {
    window.removeEventListener('storage', this.checkAuth);
    document.removeEventListener('auth-changed', this.checkAuth);
  }
};
</script>

<style scoped>
nav {
  background: #333;
  color: white;
  padding: 20px;
}

ul {
  display: flex;
  list-style: none;
  gap: 10px;
}

a, button {
  color: white;
  text-decoration: none;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
}

a:hover, button:hover {
  text-decoration: underline;
}
</style>
