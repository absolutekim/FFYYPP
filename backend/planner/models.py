from django.db import models
from django.conf import settings
from destinations.models import Location

class Planner(models.Model):
    """
    사용자가 생성한 여행 플래너
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='planners')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}의 플래너: {self.title}"
    
    class Meta:
        ordering = ['-created_at']

class PlannerItem(models.Model):
    """
    플래너에 추가된 여행지 항목
    """
    id = models.AutoField(primary_key=True)
    planner = models.ForeignKey(Planner, on_delete=models.CASCADE, related_name='items')
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)  # 여행지 순서
    notes = models.TextField(blank=True, null=True)  # 여행지에 대한 메모
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.planner.title} - {self.location.name} ({self.order}번째)"
    
    class Meta:
        ordering = ['order']
        unique_together = ['planner', 'location']  # 같은 플래너에 같은 여행지 중복 방지
