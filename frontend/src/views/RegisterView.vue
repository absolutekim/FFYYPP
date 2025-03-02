<template>
  <div>
    <h2>회원가입</h2>
    <form @submit.prevent="register">
      <label>아이디:</label>
      <input type="text" v-model="form.username" required />

      <label>이메일:</label>
      <input type="email" v-model="form.email" required />

      <label>닉네임:</label>
      <input type="text" v-model="form.nickname" required />

      <label>비밀번호:</label>
      <input type="password" v-model="form.password" required />

      <label>비밀번호 확인:</label>
      <input type="password" v-model="form.password2" required />

      <button type="submit">회원가입</button>
    </form>
    <p v-if="message">{{ message }}</p>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      form: {
        username: '',
        email: '',
        nickname: '',
        password: '',
        password2: ''
      },
      message: ''
    };
  },
  methods: {
    async register() {
      try {
        const response = await axios.post('http://localhost:8000/api/accounts/register/', this.form);
        this.message = response.data.message;
      } catch (error) {
        console.error('회원가입 실패:', error.response.data);
        this.message = '회원가입에 실패했습니다.';
      }
    }
  }
};
</script>
