from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from accounts.models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)  # 비밀번호 확인 필드

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'nickname', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')  # password2는 저장할 필요 없음
        user = CustomUser.objects.create_user(**validated_data)  # 사용자 생성
        return user
