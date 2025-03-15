<template>
  <header class="app-header">
    <div class="header-container">
      <div class="logo-container">
        <router-link to="/" class="logo">
          <img src="@/assets/logo.png" alt="Travel Logo" v-if="false">
          <span class="logo-text">여행 추천</span>
        </router-link>
      </div>
      
      <div class="search-container">
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="여행지 검색..." 
          class="search-input"
          @keyup.enter="handleSearch"
        />
        <button @click="handleSearch" class="search-button">
          <i class="fas fa-search"></i>
        </button>
      </div>
      
      <nav class="main-nav">
        <ul class="nav-links">
          <li><router-link to="/destinations">여행지</router-link></li>
          <li><router-link to="/recommend">맞춤 추천</router-link></li>
          <li v-if="isAuthenticated"><router-link to="/profile">마이페이지</router-link></li>
          <li v-if="isAuthenticated"><a href="#" @click.prevent="logout">로그아웃</a></li>
          <li v-else><router-link to="/login">로그인</router-link></li>
        </ul>
      </nav>
      
      <button class="mobile-menu-button" @click="toggleMobileMenu">
        <i class="fas fa-bars"></i>
      </button>
    </div>
    
    <div class="mobile-menu" :class="{ active: mobileMenuOpen }">
      <ul class="mobile-nav-links">
        <li><router-link to="/destinations" @click="closeMobileMenu">여행지</router-link></li>
        <li><router-link to="/recommend" @click="closeMobileMenu">맞춤 추천</router-link></li>
        <li v-if="isAuthenticated"><router-link to="/profile" @click="closeMobileMenu">마이페이지</router-link></li>
        <li v-if="isAuthenticated"><a href="#" @click.prevent="logout">로그아웃</a></li>
        <li v-else><router-link to="/login" @click="closeMobileMenu">로그인</router-link></li>
      </ul>
    </div>
  </header>
</template>

<script>
export default {
  name: 'AppHeader',
  data() {
    return {
      searchQuery: '',
      mobileMenuOpen: false
    };
  },
  computed: {
    isAuthenticated() {
      return !!localStorage.getItem('access_token');
    }
  },
  methods: {
    handleSearch() {
      if (this.searchQuery.trim()) {
        this.$router.push({
          path: '/destinations',
          query: { q: this.searchQuery }
        }).catch(err => {
          if (err.name !== 'NavigationDuplicated') {
            throw err;
          }
        });
        
        this.searchQuery = '';
      }
    },
    toggleMobileMenu() {
      this.mobileMenuOpen = !this.mobileMenuOpen;
    },
    closeMobileMenu() {
      this.mobileMenuOpen = false;
    },
    logout() {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      this.closeMobileMenu();
      
      const authRequiredRoutes = ['/profile', '/recommend'];
      if (authRequiredRoutes.includes(this.$route.path)) {
        this.$router.push('/');
      } else {
        this.$router.go();
      }
    }
  },
  watch: {
    '$route'() {
      this.mobileMenuOpen = false;
    }
  }
};
</script>

<style scoped>
.app-header {
  background-color: #ffffff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo-container {
  flex: 0 0 auto;
}

.logo {
  display: flex;
  align-items: center;
  text-decoration: none;
}

.logo img {
  height: 40px;
  margin-right: 0.5rem;
}

.logo-text {
  font-size: 1.5rem;
  font-weight: 700;
  color: #3498db;
}

.search-container {
  flex: 0 1 400px;
  display: flex;
  margin: 0 1rem;
}

.search-input {
  flex-grow: 1;
  padding: 0.5rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 4px 0 0 4px;
  font-size: 0.9rem;
}

.search-button {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0 1rem;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
}

.main-nav {
  flex: 0 0 auto;
}

.nav-links {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-links li {
  margin-left: 1.5rem;
}

.nav-links a {
  text-decoration: none;
  color: #4a5568;
  font-weight: 500;
  transition: color 0.3s;
}

.nav-links a:hover,
.nav-links a.router-link-active {
  color: #3498db;
}

.mobile-menu-button {
  display: none;
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #4a5568;
  cursor: pointer;
}

.mobile-menu {
  display: none;
  background-color: #ffffff;
  padding: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.mobile-nav-links {
  list-style: none;
  margin: 0;
  padding: 0;
}

.mobile-nav-links li {
  margin-bottom: 1rem;
}

.mobile-nav-links a {
  display: block;
  text-decoration: none;
  color: #4a5568;
  font-weight: 500;
  padding: 0.5rem 0;
  transition: color 0.3s;
}

.mobile-nav-links a:hover,
.mobile-nav-links a.router-link-active {
  color: #3498db;
}

@media (max-width: 768px) {
  .search-container {
    flex: 1;
    margin: 0 1rem;
  }
  
  .main-nav {
    display: none;
  }
  
  .mobile-menu-button {
    display: block;
  }
  
  .mobile-menu.active {
    display: block;
  }
}

@media (max-width: 576px) {
  .header-container {
    padding: 0.8rem;
  }
  
  .logo-text {
    font-size: 1.2rem;
  }
  
  .search-container {
    max-width: 200px;
  }
}
</style> 