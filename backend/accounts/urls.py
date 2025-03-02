from django.shortcuts import render
from django.urls import path
from .views import register_user
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', register_user, name='register'),  # 회원가입 API
     path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # 로그인
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # 토큰 갱신
]
