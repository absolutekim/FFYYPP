<template>
  <div class="profile-container">
    <div class="profile-header">
      <h1 class="profile-title">내 프로필</h1>
      <div v-if="isAuthenticated" class="user-info">
        <p class="username">{{ username }}</p>
        <p class="email">{{ email }}</p>
      </div>
    </div>

    <div v-if="!isAuthenticated" class="login-required">
      <p>Tou must be logged in to view profile</p>
      <router-link to="/login" class="login-button">Login</router-link>
    </div>

    <div v-else class="profile-content">
      <div class="tabs">
        <button 
          @click="activeTab = 'likes'" 
          :class="['tab-button', { active: activeTab === 'likes' }]"
        >
          <i class="fas fa-heart"></i> Liked Destinations
        </button>
        <button 
          @click="activeTab = 'reviews'" 
          :class="['tab-button', { active: activeTab === 'reviews' }]"
        >
          <i class="fas fa-comment"></i> Your Reviews
        </button>
      </div>

      <div class="tab-content">
        <keep-alive>
          <user-likes v-if="activeTab === 'likes'" />
          <user-reviews v-else-if="activeTab === 'reviews'" />
        </keep-alive>
      </div>
    </div>
  </div>
</template>

<script>
import UserLikes from '@/components/UserLikes.vue';
import UserReviews from '@/components/UserReviews.vue';

export default {
  name: 'ProfileView',
  components: {
    UserLikes,
    UserReviews
  },
  data() {
    return {
      activeTab: 'likes'
    };
  },
  computed: {
    isAuthenticated() {
      return this.$store.getters.isAuthenticated;
    },
    username() {
      return this.$store.getters.username;
    },
    email() {
      return this.$store.getters.email;
    }
  }
};
</script>

<style scoped>
.profile-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
}

.profile-header {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e2e8f0;
}

.profile-title {
  font-size: 28px;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 15px;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.username {
  font-size: 18px;
  font-weight: 600;
  color: #4a5568;
}

.email {
  font-size: 16px;
  color: #718096;
}

.login-required {
  text-align: center;
  padding: 60px 20px;
  background-color: #f8fafc;
  border-radius: 8px;
  color: #718096;
}

.login-button {
  display: inline-block;
  margin-top: 15px;
  padding: 10px 20px;
  background-color: #4299e1;
  color: white;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 500;
  transition: background-color 0.2s;
}

.login-button:hover {
  background-color: #3182ce;
}

.tabs {
  display: flex;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 20px;
}

.tab-button {
  padding: 12px 20px;
  background: none;
  border: none;
  font-size: 16px;
  font-weight: 500;
  color: #718096;
  cursor: pointer;
  transition: all 0.2s;
  border-bottom: 2px solid transparent;
  display: flex;
  align-items: center;
  gap: 8px;
}

.tab-button:hover {
  color: #4299e1;
}

.tab-button.active {
  color: #4299e1;
  border-bottom-color: #4299e1;
}

.tab-button i {
  font-size: 14px;
}

.tab-content {
  min-height: 400px;
}

@media (max-width: 768px) {
  .profile-container {
    padding: 20px 15px;
  }
  
  .profile-title {
    font-size: 24px;
  }
  
  .tabs {
    overflow-x: auto;
  }
  
  .tab-button {
    padding: 10px 15px;
    font-size: 14px;
  }
}
</style> 