from django.contrib import admin
from accounts.models import CustomUser

# Django Admin에서 CustomUser 관리 가능하게 등록
admin.site.register(CustomUser)
