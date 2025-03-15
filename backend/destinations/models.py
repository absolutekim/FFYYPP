from django.db import models
from django.conf import settings
from django.utils import timezone

class Location(models.Model):
    id = models.AutoField(primary_key=True)  # ✅ 기본 키 설정
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    subcategories = models.JSONField(blank=True, null=True)  # ✅ JSON 형태로 저장
    subtypes = models.JSONField(blank=True, null=True)  # ✅ JSON 형태로 저장
    type = models.CharField(max_length=255, blank=True, null=True)

    address = models.CharField(max_length=500, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    street1 = models.CharField(max_length=255, blank=True, null=True)
    street2 = models.CharField(max_length=255, blank=True, null=True)

    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    local_address = models.CharField(max_length=500, blank=True, null=True)
    local_name = models.CharField(max_length=255, blank=True, null=True)
    location_string = models.CharField(max_length=500, blank=True, null=True)

    image = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    # 좋아요 수를 저장하는 필드 추가
    likes_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

# 좋아요 모델
class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'location')  # 한 사용자가 같은 여행지에 중복 좋아요 방지
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} likes {self.location.name}"
    
    def save(self, *args, **kwargs):
        # 새로운 좋아요가 추가될 때 location의 likes_count 증가
        is_new = self.pk is None
        
        # 이미 존재하는지 확인 (중복 방지)
        if is_new and Like.objects.filter(user=self.user, location=self.location).exists():
            # 이미 존재하면 저장하지 않고 기존 객체 반환
            return Like.objects.get(user=self.user, location=self.location)
        
        super().save(*args, **kwargs)
        
        if is_new:
            # 트랜잭션 안전성을 위해 데이터베이스에서 최신 값을 가져와 업데이트
            location = Location.objects.get(pk=self.location.pk)
            location.likes_count += 1
            location.save(update_fields=['likes_count'])
    
    def delete(self, *args, **kwargs):
        # 좋아요가 삭제될 때 location의 likes_count 감소
        location_id = self.location.id
        super().delete(*args, **kwargs)
        
        # 트랜잭션 안전성을 위해 데이터베이스에서 최신 값을 가져와 업데이트
        try:
            location = Location.objects.get(pk=location_id)
            location.likes_count = max(0, location.likes_count - 1)  # 음수가 되지 않도록 보장
            location.save(update_fields=['likes_count'])
        except Location.DoesNotExist:
            # 여행지가 삭제된 경우 무시
            pass

# 리뷰 모델
class Review(models.Model):
    RATING_CHOICES = (
        (1, '1 - 매우 불만족'),
        (2, '2 - 불만족'),
        (3, '3 - 보통'),
        (4, '4 - 만족'),
        (5, '5 - 매우 만족'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='reviews')
    content = models.TextField()
    rating = models.IntegerField(choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # 감정 분석 결과 저장 필드
    sentiment = models.CharField(max_length=20, null=True, blank=True)  # POSITIVE, NEGATIVE, NEUTRAL
    sentiment_score = models.FloatField(null=True, blank=True)  # 감정 점수 (0~1)
    
    # 리뷰에서 추출된 키워드 저장
    keywords = models.JSONField(null=True, blank=True)  # JSON 형식으로 저장된 키워드 목록
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s review on {self.location.name}"
    
    def save(self, *args, **kwargs):
        # 리뷰 저장 시 감정 분석 수행
        if self.content:
            from .review_utils import analyze_review
            analysis_result = analyze_review(self.content)
            
            self.sentiment = analysis_result['sentiment']
            self.sentiment_score = analysis_result['sentiment_score']
            self.keywords = analysis_result['keywords']
        
        super().save(*args, **kwargs)
