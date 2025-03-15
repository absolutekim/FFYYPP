from django.shortcuts import render
from django.urls import path
from .views import register_user, CustomTokenObtainPairView, debug_login, get_subcategory_tags, get_user_profile, update_user_tags, delete_user_account
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', register_user, name='register'),  # 회원가입 API
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # ✅ 커스텀 로그인 적용
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # 토큰 갱신
    path('debug-login/', debug_login, name='debug_login'),  # ✅ 디버깅용 로그인 엔드포인트 추가
    path('tags/', get_subcategory_tags, name='get_subcategory_tags'),
    path('profile/', get_user_profile, name='get_user_profile'),
    path('update-tags/', update_user_tags, name='update_user_tags'),
    path('delete-account/', delete_user_account, name='delete_user_account'),  # 계정 삭제 API
]
