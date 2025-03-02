import { createApp } from 'vue';
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
  },
  icons: {
    defaultSet: 'mdi', // ✅ 아이콘 기본값 설정
  },
});

const app = createApp(App);
app.use(vuetify); // ✅ Vuetify 플러그인 적용 (항상 router보다 먼저!)
app.use(router);

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

app.mount('#app');

// ✅ AOS 초기화
AOS.init();
