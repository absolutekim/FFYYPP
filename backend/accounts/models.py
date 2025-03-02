from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)  # 이메일 필수
    nickname = models.CharField(max_length=30, unique=True, blank=True, null=True)  # 닉네임 추가

    def __str__(self):
        return self.username

