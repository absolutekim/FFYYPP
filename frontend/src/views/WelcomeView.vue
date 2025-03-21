<template>
  <div class="welcome-container">
    <v-container>
      <v-row justify="center" align="center" class="fill-height">
        <v-col cols="12" md="8" class="text-center">
          <div data-aos="fade-up" class="welcome-content">
            <h1 class="text-h2 font-weight-bold white--text mb-6">
              Welcome to Travel Planner
            </h1>
            <p class="text-h5 white--text mb-8">
              The Best Choice for Your Perfect Journey
            </p>
            <!-- 로그인하지 않은 사용자에게 표시할 버튼 -->
            <div v-if="!isAuthenticated">
              <v-btn
                to="/login"
                x-large
                color="primary"
                elevation="4"
                class="mr-4"
                data-aos="fade-up"
                data-aos-delay="200"
              >
                <v-icon left>mdi-login</v-icon>
                Login
              </v-btn>
              <v-btn
                to="/register"
                x-large
                color="secondary"
                elevation="4"
                data-aos="fade-up"
                data-aos-delay="400"
              >
                <v-icon left>mdi-account-plus</v-icon>
                Register
              </v-btn>
            </div>
            
            <!-- 로그인한 사용자에게 표시할 버튼 -->
            <div v-else>
              <v-btn
                to="/flights"
                x-large
                color="primary"
                elevation="4"
                class="mr-4"
                data-aos="fade-up"
                data-aos-delay="200"
              >
                <v-icon left>mdi-airplane</v-icon>
                Flight Search
              </v-btn>
              <v-btn
                to="/planner"
                x-large
                color="secondary"
                elevation="4"
                class="mr-4"
                data-aos="fade-up"
                data-aos-delay="400"
              >
                <v-icon left>mdi-map-marker-path</v-icon>
                Travel Planner
              </v-btn>
              <v-btn
                to="/recommendations"
                x-large
                color="success"
                elevation="4"
                data-aos="fade-up"
                data-aos-delay="600"
              >
                <v-icon left>mdi-star</v-icon>
                Recommendations for you
              </v-btn>
            </div>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import AOS from 'aos';
import 'aos/dist/aos.css';

export default {
  name: 'WelcomeView',
  mounted() {
    AOS.init({
      duration: 1000,
      once: true
    });
  },
  computed: {
    isAuthenticated() {
      return !!localStorage.getItem('access_token');
    }
  }
};
</script>

<style scoped>
.welcome-container {
  min-height: 100vh;
  background-image: url('@/assets/back.jpg');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  display: flex;
  align-items: center;
  position: relative;
}

.welcome-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
}

.welcome-content {
  position: relative;
  z-index: 1;
}

.fill-height {
  min-height: 100vh;
}
</style>
