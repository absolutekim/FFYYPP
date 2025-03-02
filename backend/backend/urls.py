"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse  # ✅ JsonResponse import 추가


def root(request):
    return JsonResponse({"message": "Welcome to the Django Backend!"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', root),  # 루트 URL 추가
    path('api/', include('api.urls')),
    path('api/accounts/', include('accounts.urls')),
    path('api/community/', include('community.urls')),  # ✅ community 앱의 API 경로 추가
    path('api/flights/', include('flight.urls')),  # ✅ flights API 추가
]