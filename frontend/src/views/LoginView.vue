<template>
  <div>
    <h1>로그인</h1>
    <form @submit.prevent="login">
      <input v-model="username" type="text" placeholder="ID" required>
      <input v-model="password" type="password" placeholder="Password" required>
      <button type="submit">Login</button>
    </form>
    <p v-if="errorMessage" style="color: red;">{{ errorMessage }}</p>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      username: '',
      password: '',
      errorMessage: ''
    };
  },
  methods: {
    async login() {
      try {
        const response = await axios.post('http://localhost:8000/api/accounts/login/', {
          username: this.username,  // ✅ 올바른 필드명 확인
          password: this.password
        }, {
          headers: { 'Content-Type': 'application/json' }  // ✅ JSON 형식으로 전송
        });

        // ✅ 로그인 성공 시 토큰 저장
        localStorage.setItem('access_token', response.data.access);
        localStorage.setItem('refresh_token', response.data.refresh);

        // ✅ 네비게이션 상태 즉시 반영
        document.dispatchEvent(new Event('auth-changed'));

        console.log("✅ 로그인 성공, 토큰 저장됨:", response.data.access);
        this.$router.push('/');
      } catch (error) {
        console.error("🚨 로그인 실패:", error);
        this.errorMessage = "로그인에 실패했습니다. 아이디 또는 비밀번호를 확인하세요.";
      }
    }
  }
};
</script>
