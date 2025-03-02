import { createRouter, createWebHistory } from 'vue-router';
import WelcomeView from '@/views/WelcomeView.vue';
import RegisterView from '@/views/RegisterView.vue';
import LoginView from '@/views/LoginView.vue';
import PostDetailView from '@/views/PostDetailView.vue';
import NewPostView from '@/views/NewPostView.vue';
import EditPostView from '@/views/EditPostView.vue';
import CommunityView from '@/views/CommunityView.vue';
import FlightSearchView from '@/views/FlightSearchView.vue';

const routes = [
  { path: '/', component: WelcomeView },
  { path: '/register', component: RegisterView },
  { path: '/login', component: LoginView },
  { path: '/community', component: CommunityView, meta: { requiresAuth: true } },
  { path: '/community/:id', component: PostDetailView, props: true, meta: { requiresAuth: true } },
  { path: '/community/new', component: NewPostView, meta: { requiresAuth: true } },
  { path: '/community/:id/edit', component: EditPostView, props: true, meta: { requiresAuth: true } },
  { path: '/flights', component: FlightSearchView },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// ✅ 로그인하지 않은 사용자는 커뮤니티 접근 차단
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('access_token');
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    alert("로그인이 필요합니다.");
    next('/login'); // ✅ 로그인 페이지로 리디렉트
  } else {
    next();
  }
});

export default router;
