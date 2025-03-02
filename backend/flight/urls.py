from django.urls import path
from .views import search_flights, search_airports, get_flight_details  # ✅ 추가 확인!

urlpatterns = [
    path("search/", search_flights, name="search-flights"),
    path("search-airports/", search_airports, name="search-airports"),  # 🏙️ 공항 자동완성
    path('details/', get_flight_details, name='get_flight_details'),

]
