from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    email = models.EmailField(unique=True)  # 이메일 필수
    nickname = models.CharField(max_length=30, unique=True, blank=True, null=True)  # 닉네임 추가
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)  # ✅ 성별 필드 추가
    selected_tags = models.JSONField(blank=True, null=True)  # ✅ 사용자가 선택한 태그 저장 (3-7개)

    def __str__(self):
        return self.username

