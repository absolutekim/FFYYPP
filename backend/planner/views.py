from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Planner, PlannerItem
from .serializers import (
    PlannerSerializer, 
    PlannerItemSerializer, 
    PlannerItemCreateSerializer,
    PlannerListSerializer
)
from destinations.models import Location

class IsOwner(permissions.BasePermission):
    """
    사용자가 플래너의 소유자인지 확인하는 권한 클래스
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class PlannerViewSet(viewsets.ModelViewSet):
    """
    플래너 CRUD API
    """
    serializer_class = PlannerSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    
    def get_queryset(self):
        """
        현재 로그인한 사용자의 플래너만 반환
        """
        return Planner.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """
        요청 메서드에 따라 적절한 시리얼라이저 반환
        """
        if self.action == 'list':
            return PlannerListSerializer
        return PlannerSerializer
    
    def perform_create(self, serializer):
        """
        플래너 생성 시 현재 로그인한 사용자를 소유자로 설정
        """
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """
        특정 플래너의 모든 항목 조회
        """
        planner = self.get_object()
        items = planner.items.all()
        serializer = PlannerItemSerializer(items, many=True)
        return Response(serializer.data)

class PlannerItemViewSet(viewsets.ModelViewSet):
    """
    플래너 항목 CRUD API
    """
    serializer_class = PlannerItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        현재 로그인한 사용자의 플래너 항목만 반환
        """
        return PlannerItem.objects.filter(planner__user=self.request.user)
    
    def get_serializer_class(self):
        """
        요청 메서드에 따라 적절한 시리얼라이저 반환
        """
        if self.action in ['create', 'update', 'partial_update']:
            return PlannerItemCreateSerializer
        return PlannerItemSerializer
    
    def perform_create(self, serializer):
        """
        플래너 항목 생성 시 유효성 검사
        """
        planner = serializer.validated_data.get('planner')
        
        # 플래너 소유자 확인
        if planner.user != self.request.user:
            return Response(
                {"detail": "이 플래너의 소유자가 아닙니다."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer.save()
    
    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """
        플래너 항목 순서 변경
        """
        items_data = request.data.get('items', [])
        if not items_data:
            return Response(
                {"detail": "항목 데이터가 없습니다."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 모든 항목이 현재 사용자의 것인지 확인
        item_ids = [item.get('id') for item in items_data]
        items = PlannerItem.objects.filter(id__in=item_ids)
        
        if items.count() != len(item_ids):
            return Response(
                {"detail": "일부 항목을 찾을 수 없습니다."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        for item in items:
            if item.planner.user != request.user:
                return Response(
                    {"detail": "일부 항목의 소유자가 아닙니다."}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # 순서 업데이트
        for item_data in items_data:
            item_id = item_data.get('id')
            new_order = item_data.get('order')
            
            if item_id and new_order is not None:
                PlannerItem.objects.filter(id=item_id).update(order=new_order)
        
        return Response({"detail": "항목 순서가 업데이트되었습니다."}, status=status.HTTP_200_OK)
