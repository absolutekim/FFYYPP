<template>
  <v-toolbar color="#2c3e50" dark>
    <v-toolbar-title class="text-h6 font-weight-bold">
      <span 
        @click="$router.push('/')" 
        class="title-text"
      >
        Travel Planner
      </span>
    </v-toolbar-title>

    <v-spacer></v-spacer>

    <v-btn text to="/" class="mx-2 nav-btn">
      <v-icon left>mdi-home</v-icon>
      홈
    </v-btn>

    <!-- 🔹 로그인 상태일 때 -->
    <template v-if="isAuthenticated">
      <v-btn text to="/community" class="mx-2 nav-btn">
        <v-icon left>mdi-account-group</v-icon>
        커뮤니티
      </v-btn>

      <v-btn text to="/destinations" class="mx-2 nav-btn">
        <v-icon left>mdi-map-marker</v-icon>
        여행지
      </v-btn>
      
      <v-btn text to="/most-loved" class="mx-2 nav-btn">
        <v-icon left>mdi-heart</v-icon>
        인기 여행지
      </v-btn>

      <v-btn text to="/recommendations" class="mx-2 nav-btn">
        <v-icon left>mdi-star</v-icon>
        맞춤 추천
      </v-btn>

      <v-btn text to="/flights" class="mx-2 nav-btn">
        <v-icon left>mdi-airplane</v-icon>
        항공편
      </v-btn>

      <v-btn text to="/planner" class="mx-2 nav-btn">
        <v-icon left>mdi-calendar-check</v-icon>
        여행 플래너
      </v-btn>

      <v-btn text to="/mypage" class="mx-2 nav-btn">
        <v-icon left>mdi-account</v-icon>
        마이페이지
      </v-btn>

      <v-btn text @click="logout" class="mx-2 nav-btn">
        <v-icon left>mdi-logout</v-icon>
        로그아웃
      </v-btn>
    </template> <!-- ✅ 여기에서 닫아야 함 -->

    <!-- 🔹 비로그인 상태일 때 -->
    <template v-else>
      <v-btn text to="/register" class="mx-2 nav-btn">
        <v-icon left>mdi-account-plus</v-icon>
        회원가입
      </v-btn>

      <v-btn text to="/login" class="mx-2 nav-btn">
        <v-icon left>mdi-login</v-icon>
        로그인
      </v-btn>
    </template>

  </v-toolbar>
</template>


<script>
import axios from 'axios';

export default {
  name: 'AppNavbar',
  data() {
    return {
      isAuthenticated: !!localStorage.getItem('access_token'),
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
      this.isAuthenticated = false;
      this.$router.push('/login');
    }
  },
  mounted() {
    window.addEventListener('storage', this.checkAuth);
    document.addEventListener('auth-changed', this.checkAuth);
  },
  beforeUnmount() {
    window.removeEventListener('storage', this.checkAuth);
    document.removeEventListener('auth-changed', this.checkAuth);
  }
};
</script>

<style scoped>
.v-toolbar {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.nav-btn {
  text-transform: none;
  letter-spacing: 0.5px;
  font-weight: 400;
  opacity: 0.9;
  transition: opacity 0.2s;
}

.nav-btn:hover {
  opacity: 1;
  background: rgba(255, 255, 255, 0.1) !important;
}

.title-text {
  color: white;
  cursor: pointer;
  transition: color 0.2s;
}

.title-text:active {
  color: #FF5252 !important;  /* 클릭시 빨간색으로 변경 */
}

/* hover 효과도 추가할 수 있습니다 */
.title-text:hover {
  opacity: 0.9;
}

:deep(.router-link-active) {
  color: white !important;
}
</style>