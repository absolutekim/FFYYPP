from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'likes', views.LikeViewSet, basename='like')
router.register(r'reviews', views.ReviewViewSet, basename='review')

urlpatterns = [
    # 기본 여행지 API
    path('', views.get_locations, name='get_locations'),
    path('<int:pk>/', views.get_location_detail, name='get_location_detail'),
    path('tag/<str:tag>/', views.get_locations_by_tag, name='get_locations_by_tag'),
    path('search/nlp/', views.search_destinations_nlp, name='search_destinations_nlp'),
    
    # 좋아요 및 리뷰 API
    path('', include(router.urls)),
    path('recommend/', views.recommend_destinations, name='recommend_destinations'),
    path('user/likes/', views.UserLikesView.as_view(), name='user-likes'),
    path('user/reviews/', views.UserReviewsView.as_view(), name='user-reviews'),
    path('<int:location_id>/reviews/', views.location_reviews, name='location_reviews'),
    
    # 인기 여행지 API
    path('most-loved/', views.most_loved_locations, name='most-loved-locations'),
]