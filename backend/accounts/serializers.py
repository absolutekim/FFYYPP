from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from accounts.models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)  # 비밀번호 확인 필드

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'nickname', 'password', 'password2', 'gender', 'selected_tags')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        
        # 태그 선택 검증 (3-7개 사이)
        selected_tags = attrs.get('selected_tags', [])
        if selected_tags and (len(selected_tags) < 3 or len(selected_tags) > 7):
            raise serializers.ValidationError({"selected_tags": "3개에서 7개 사이의 태그를 선택해야 합니다."})
            
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')  # password2는 저장할 필요 없음
        user = CustomUser.objects.create_user(**validated_data)  # 사용자 생성
        return user
