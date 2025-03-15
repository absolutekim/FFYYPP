from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlannerViewSet, PlannerItemViewSet

router = DefaultRouter()
router.register(r'planners', PlannerViewSet, basename='planner')
router.register(r'planner-items', PlannerItemViewSet, basename='planner-item')

urlpatterns = [
    path('', include(router.urls)),
]

