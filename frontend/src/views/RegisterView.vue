<template>
  <div class="register-container">
    <div class="register-box">
      <h2>Create Account</h2>
      <form @submit.prevent="register" class="register-form">
        <div class="form-group">
          <label>Username</label>
          <input type="text" v-model="form.username" required placeholder="Enter your username" />
        </div>

        <div class="form-group">
          <label>Email</label>
          <input type="email" v-model="form.email" required placeholder="Enter your email" />
        </div>

        <div class="form-group">
          <label>Nickname</label>
          <input type="text" v-model="form.nickname" required placeholder="Enter your nickname" />
        </div>

        <div class="form-group">
          <label>Password</label>
          <input type="password" v-model="form.password" required placeholder="Enter your password" />
        </div>

        <div class="form-group">
          <label>Confirm Password</label>
          <input type="password" v-model="form.password2" required placeholder="Confirm your password" />
        </div>

        <div class="form-group gender-group">
          <label>Gender</label>
          <div class="radio-group">
            <label class="radio-label">
              <input type="radio" v-model="form.gender" value="M" required />
              <span>Male</span>
            </label>
            <label class="radio-label">
              <input type="radio" v-model="form.gender" value="F" required />
              <span>Female</span>
            </label>
          </div>
        </div>

        <TagChoose v-model="form.selected_tags" />
        
        <!-- 디버깅용 정보 표시 -->
        <div class="debug-info" v-if="showDebug">
          <p>선택된 태그 수: {{ form.selected_tags.length }}</p>
          <p>선택된 태그: {{ form.selected_tags.join(', ') }}</p>
          <p>폼 유효성: {{ isFormValid ? '유효함' : '유효하지 않음' }}</p>
          <p>Username: {{ !!form.username }}</p>
          <p>Email: {{ !!form.email }}</p>
          <p>Nickname: {{ !!form.nickname }}</p>
          <p>Password: {{ !!form.password }}</p>
          <p>Password2: {{ !!form.password2 }}</p>
          <p>Gender: {{ !!form.gender }}</p>
          <p>Tags Valid: {{ form.selected_tags.length >= 3 && form.selected_tags.length <= 7 }}</p>
        </div>

        <button type="submit" class="submit-btn" :disabled="!isFormValid">Create Account</button>
        <button type="button" class="debug-btn" @click="toggleDebug">디버그 정보 {{ showDebug ? '숨기기' : '보기' }}</button>
      </form>
      <p v-if="message" :class="['message', message.includes('failed') ? 'error' : 'success']">{{ message }}</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import TagChoose from '@/components/TagChoose.vue';

export default {
  components: {
    TagChoose
  },
  data() {
    return {
      form: {
        username: '',
        email: '',
        nickname: '',
        password: '',
        password2: '',
        gender: '',
        selected_tags: []
      },
      message: '',
      showDebug: false
    };
  },
  mounted() {
    // 태그 배열이 제대로 초기화되었는지 확인
    if (!Array.isArray(this.form.selected_tags)) {
      this.form.selected_tags = [];
    }
    console.log('RegisterView mounted, selected_tags:', this.form.selected_tags);
  },
  computed: {
    isFormValid() {
      // 각 필드가 유효한지 확인
      const hasUsername = !!this.form.username;
      const hasEmail = !!this.form.email;
      const hasNickname = !!this.form.nickname;
      const hasPassword = !!this.form.password;
      const hasPassword2 = !!this.form.password2;
      const hasGender = !!this.form.gender;
      
      // 태그가 3-7개 사이인지 확인
      const hasValidTags = Array.isArray(this.form.selected_tags) && 
                          this.form.selected_tags.length >= 3 && 
                          this.form.selected_tags.length <= 7;
      
      // 디버깅 로그
      console.log('Form validation:', {
        hasUsername,
        hasEmail,
        hasNickname,
        hasPassword,
        hasPassword2,
        hasGender,
        selectedTagsLength: this.form.selected_tags?.length || 0,
        hasValidTags
      });
      
      // 모든 조건이 충족되는지 확인
      return hasUsername && 
             hasEmail && 
             hasNickname && 
             hasPassword && 
             hasPassword2 && 
             hasGender && 
             hasValidTags;
    }
  },
  methods: {
    toggleDebug() {
      this.showDebug = !this.showDebug;
    },
    async register() {
      try {
        if (this.form.selected_tags.length < 3) {
          this.message = '최소 3개의 태그를 선택해주세요.';
          return;
        }
        
        if (this.form.selected_tags.length > 7) {
          this.message = '최대 7개의 태그만 선택할 수 있습니다.';
          return;
        }
        
        console.log('회원가입 시도:', this.form);
        
        const response = await axios.post('http://localhost:8000/api/accounts/register/', this.form);
        this.message = response.data.message;
        
        if (!this.message.includes('failed')) {
          setTimeout(() => {
            this.$router.push('/login');
          }, 1500);
        }
      } catch (error) {
        console.error('Registration failed:', error.response?.data || error);
        this.message = error.response?.data?.selected_tags || 
                       error.response?.data?.message || 
                       '회원가입에 실패했습니다.';
      }
    }
  }
};
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-box {
  background: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
}

h2 {
  color: #2d3748;
  text-align: center;
  margin-bottom: 30px;
  font-size: 28px;
  font-weight: 600;
}

.register-form {
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
input[type="email"],
input[type="password"] {
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 16px;
  transition: border-color 0.2s;
}

input[type="text"]:focus,
input[type="email"]:focus,
input[type="password"]:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.gender-group {
  margin-top: 10px;
}

.radio-group {
  display: flex;
  gap: 20px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.radio-label input[type="radio"] {
  margin: 0;
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

.submit-btn:disabled {
  background: #a0aec0;
  cursor: not-allowed;
}

.debug-btn {
  background: #e2e8f0;
  color: #4a5568;
  padding: 8px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  margin-top: 10px;
  cursor: pointer;
}

.debug-info {
  background: #f7fafc;
  padding: 15px;
  border-radius: 6px;
  font-size: 14px;
  margin-top: 10px;
  border: 1px solid #e2e8f0;
}

.debug-info p {
  margin: 5px 0;
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

.success {
  background: #c6f6d5;
  color: #2f855a;
}

@media (max-width: 640px) {
  .register-box {
    padding: 20px;
  }
  
  h2 {
    font-size: 24px;
  }
}
</style>
