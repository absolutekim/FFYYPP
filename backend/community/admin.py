from django.contrib import admin
from .models import Post, Comment

# ✅ 게시글 관리 설정
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'created_at')  # ✅ 목록에서 보이는 필드
    search_fields = ('title', 'author__username')  # ✅ 제목, 작성자로 검색 가능
    list_filter = ('created_at',)  # ✅ 필터 추가 (생성 날짜)
    ordering = ('-created_at',)  # ✅ 최신 글이 위로 오도록 정렬

# ✅ 댓글 관리 설정
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'author', 'post', 'created_at')  # ✅ 목록에서 보이는 필드
    search_fields = ('content', 'author__username', 'post__title')  # ✅ 댓글 내용, 작성자, 게시글 제목으로 검색 가능
    list_filter = ('created_at',)  # ✅ 필터 추가 (생성 날짜)
    ordering = ('-created_at',)  # ✅ 최신 댓글이 위로 오도록 정렬
