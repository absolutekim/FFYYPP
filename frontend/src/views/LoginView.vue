<template>
  <div class="login-container">
    <div class="login-box">
      <h2>Welcome Back</h2>
      <form @submit.prevent="login" class="login-form">
        <div class="form-group">
          <label>Username</label>
          <input type="text" v-model="username" required placeholder="Enter your username" />
        </div>

        <div class="form-group">
          <label>Password</label>
          <input type="password" v-model="password" required placeholder="Enter your password" />
        </div>

        <button type="submit" class="submit-btn">Sign In</button>
      </form>
      <p v-if="errorMessage" class="message error">{{ errorMessage }}</p>
      <div class="register-link">
        Don't have an account? <router-link to="/register">Register here</router-link>
      </div>
    </div>
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
        const response = await axios.post('/api/accounts/login/', {
          username: this.username,
          password: this.password
        }, {
          headers: { 'Content-Type': 'application/json' }
        });

        localStorage.setItem('access_token', response.data.access);
        localStorage.setItem('refresh_token', response.data.refresh);

        if (response.data.username) {
          localStorage.setItem('username', response.data.username);
        }
        document.dispatchEvent(new Event('auth-changed'));
        this.$router.push('/');
        
      } catch (error) {
        console.error("Login failed:", error);
        this.errorMessage = "Invalid username or password. Please try again.";

        if (error.response) {
          console.error("Server response status:", error.response.status);
          console.error("Server response data:", error.response.data);
        }
      }
    }
  }
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e39047 0%, #65b009 100%);
  padding: 20px;
}

.login-box {
  background: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

h2 {
  color: #2d3748;
  text-align: center;
  margin-bottom: 30px;
  font-size: 28px;
  font-weight: 600;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

label {
  color: #4a5568;
  font-size: 14px;
  font-weight: 500;
}

input[type="text"],
input[type="password"] {
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 16px;
  transition: border-color 0.2s;
}

input[type="text"]:focus,
input[type="password"]:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.submit-btn {
  background: #667eea;
  color: white;
  padding: 12px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-top: 20px;
}

.submit-btn:hover {
  background: #5a67d8;
}

.message {
  margin-top: 20px;
  padding: 12px;
  border-radius: 6px;
  text-align: center;
  font-size: 14px;
}

.error {
  background: #fed7d7;
  color: #c53030;
}

.register-link {
  margin-top: 20px;
  text-align: center;
  color: #4a5568;
  font-size: 14px;
}

.register-link a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.register-link a:hover {
  text-decoration: underline;
}

@media (max-width: 640px) {
  .login-box {
    padding: 20px;
  }
  
  h2 {
    font-size: 24px;
  }
}
</style>
