from rest_framework import serializers
from .models import Post, Comment

class PostSerializer(serializers.ModelSerializer):
    author_id = serializers.ReadOnlyField(source='author.id')  
    author = serializers.ReadOnlyField(source='author.username')  # ✅ username 반환

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'author_id', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    author_id = serializers.ReadOnlyField(source='author.id')  # ✅ author_id 추가
    author = serializers.ReadOnlyField(source='author.username')  # ✅ author 필드도 읽기 전용

    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'author_id', 'post', 'created_at']
        read_only_fields = ['post', 'author']  # ✅ post와 author를 read_only로 설정