from rest_framework import serializers
from .models import Planner, PlannerItem
from destinations.serializers import LocationSerializer
from destinations.models import Location

class PlannerItemSerializer(serializers.ModelSerializer):
    """
    플래너 항목 시리얼라이저
    """
    location_details = LocationSerializer(source='location', read_only=True)
    
    class Meta:
        model = PlannerItem
        fields = ['id', 'planner', 'location', 'location_details', 'order', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']

class PlannerSerializer(serializers.ModelSerializer):
    """
    플래너 시리얼라이저
    """
    items = PlannerItemSerializer(many=True, read_only=True)
    user = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = Planner
        fields = ['id', 'user', 'title', 'description', 'items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

class PlannerItemCreateSerializer(serializers.ModelSerializer):
    """
    플래너 항목 생성 시리얼라이저
    """
    class Meta:
        model = PlannerItem
        fields = ['planner', 'location', 'order', 'notes']
    
    def validate(self, data):
        """
        플래너 항목 유효성 검사
        - 플래너에 이미 10개 이상의 항목이 있는지 확인
        """
        planner = data.get('planner')
        if planner.items.count() >= 10:
            raise serializers.ValidationError("플래너에는 최대 10개의 여행지만 추가할 수 있습니다.")
        return data

class PlannerListSerializer(serializers.ModelSerializer):
    """
    플래너 목록 시리얼라이저
    """
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Planner
        fields = ['id', 'title', 'description', 'items_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_items_count(self, obj):
        return obj.items.count()





