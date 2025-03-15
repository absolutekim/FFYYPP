import { createApp } from 'vue'; // ✅ nextTick 추가!
import App from './App.vue';
import { createVuetify } from 'vuetify';
import 'vuetify/styles'; // ✅ Vuetify 스타일 불러오기
import * as components from 'vuetify/components'; // ✅ Vuetify 컴포넌트 등록
import * as directives from 'vuetify/directives'; // ✅ Vuetify 디렉티브 등록
import router from './router';
import axios from 'axios';
import '@mdi/font/css/materialdesignicons.css'; // ✅ 아이콘 스타일 불러오기
import 'aos/dist/aos.css'; // ✅ AOS 스타일 추가
import AOS from 'aos';



// ✅ Vuetify 설정
const vuetify = createVuetify({
  components, // ✅ 컴포넌트 추가
  directives, // ✅ 디렉티브 추가
  theme: {
    defaultTheme: 'light', // ✅ 기본 테마 설정
    themes: {
      light: {
        dark: false,
        colors: {
          primary: '#1976D2',  // 원하는 색상으로 변경
          // secondary: '#424242',
          // accent: '#82B1FF',
          // error: '#FF5252',
          // info: '#2196F3',
          // success: '#4CAF50',
          // warning: '#FFC107',
        },
      },
    },
  },
  icons: {
    defaultSet: 'mdi', // ✅ 아이콘 기본값 설정
  },
});

const app = createApp(App);
app.use(vuetify); // ✅ Vuetify 플러그인 적용 (항상 router보다 먼저!)
app.use(router);


// ✅ Axios 기본 설정
axios.defaults.baseURL = 'http://localhost:8000';

// ✅ JWT 토큰이 있으면 기본 Authorization 헤더 설정
const token = localStorage.getItem('access_token');
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  console.log("✅ JWT token found:", token);
} else {
  console.warn("⚠️ No JWT token found in localStorage!");
}

// ✅ 로그인 상태 변경을 실시간 감지
document.addEventListener('auth-changed', () => {
  const newToken = localStorage.getItem('access_token');
  if (newToken) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
    console.log("✅ Token updated:", newToken);
  } else {
    delete axios.defaults.headers.common['Authorization'];
    console.warn("⚠️ Token removed!");
  }
});

axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // 이미 재시도한 요청인 경우 무한 루프 방지
    if (originalRequest._retry) {
      return Promise.reject(error);
    }
    
    // 401 오류(인증 실패)인 경우 토큰 갱신 시도
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = localStorage.getItem('refresh_token');
      
      if (!refreshToken) {
        console.warn("⚠️ No refresh token found!");
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        delete axios.defaults.headers.common['Authorization'];
        router.push('/login');
        return Promise.reject(error);
      }

      try {
        console.log("🔄 Attempting to refresh token...");
        const response = await axios.post('/api/token/refresh/', {
          refresh: refreshToken
        });
        
        if (response.data.access) {
          console.log("✅ Token refreshed successfully!");
          localStorage.setItem('access_token', response.data.access);
          
          // 새 토큰으로 헤더 업데이트
          axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`;
          
          // 원래 요청 재시도
          originalRequest.headers['Authorization'] = `Bearer ${response.data.access}`;
          return axios(originalRequest);
        } else {
          console.error("❌ Token refresh failed: No access token in response");
          throw new Error("Token refresh failed");
        }
      } catch (refreshError) {
        console.error("❌ Token refresh error:", refreshError);
        
        // 토큰 갱신 실패 시 로그아웃 처리
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        delete axios.defaults.headers.common['Authorization'];
        
        // 로그인 페이지로 리디렉션
        router.push('/login');
        return Promise.reject(error);
      }
    }
    
    return Promise.reject(error);
  }
);

app.mount('#app');

// ✅ AOS 초기화
AOS.init({ duration: 1200 });
