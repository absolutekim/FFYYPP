from django.urls import path
from .views import MyPageViewSet

urlpatterns = [
    path('profile/', MyPageViewSet.as_view({
        'get': 'retrieve',
        'put': 'update'
    })),
]
