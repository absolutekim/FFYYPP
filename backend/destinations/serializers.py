from rest_framework import serializers
from destinations.models import Location, Like, Review
from django.contrib.auth import get_user_model

User = get_user_model()

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'  # 🔹 모든 필드 포함 (likes_count 포함)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id', 'username', 'email']

class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        write_only=True,
        source='location'
    )
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'location', 'location_id', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
    
    def create(self, validated_data):
        # 현재 요청한 사용자를 like.user로 설정
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class ReviewSerializer(serializers.ModelSerializer):
    location_id = serializers.IntegerField(write_only=True)
    location_name = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'location', 'location_id', 'location_name', 'username', 'rating', 'content', 'sentiment', 'created_at', 'updated_at']
        read_only_fields = ['user', 'location', 'sentiment', 'created_at', 'updated_at']
    
    def get_location_name(self, obj):
        return obj.location.name if obj.location else None
    
    def get_username(self, obj):
        return obj.user.username if obj.user else None
    
    def create(self, validated_data):
        print("ReviewSerializer.create 호출됨:", validated_data)
        location_id = validated_data.pop('location_id')
        user = self.context['request'].user
        
        try:
            location = Location.objects.get(id=location_id)
        except Location.DoesNotExist:
            raise serializers.ValidationError({"location_id": "존재하지 않는 여행지입니다."})
        
        # 이미 리뷰가 있는지 확인
        existing_review = Review.objects.filter(user=user, location=location).first()
        if existing_review:
            raise serializers.ValidationError({"error": "이미 이 여행지에 대한 리뷰를 작성했습니다."})
        
        review = Review.objects.create(
            user=user,
            location=location,
            **validated_data
        )
        return review
    
    def update(self, instance, validated_data):
        print("ReviewSerializer.update 호출됨:", validated_data)
        if 'location_id' in validated_data:
            location_id = validated_data.pop('location_id')
            try:
                location = Location.objects.get(id=location_id)
                instance.location = location
            except Location.DoesNotExist:
                raise serializers.ValidationError({"location_id": "존재하지 않는 여행지입니다."})
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class LocationDetailSerializer(LocationSerializer):
    """여행지 상세 정보와 함께 좋아요 및 리뷰 정보를 포함하는 시리얼라이저"""
    reviews_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()
    user_review = serializers.SerializerMethodField()
    recent_reviews = serializers.SerializerMethodField()
    
    class Meta:
        model = Location
        fields = '__all__'
    
    def get_reviews_count(self, obj):
        return obj.reviews.count()
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if not reviews:
            return None
        return sum(review.rating for review in reviews) / reviews.count()
    
    def get_user_has_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
    def get_user_review(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                review = obj.reviews.get(user=request.user)
                return ReviewSerializer(review).data
            except Review.DoesNotExist:
                return None
        return None
    
    def get_recent_reviews(self, obj):
        # 최근 리뷰 5개만 반환
        reviews = obj.reviews.all()[:5]
        return ReviewSerializer(reviews, many=True).data
