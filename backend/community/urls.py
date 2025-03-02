from django.urls import path
from .views import PostListCreateView, PostDetailDeleteView, create_comment, delete_comment, get_comments

urlpatterns = [
    path('posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetailDeleteView.as_view(), name='post-detail-delete'),
    path('posts/<int:post_id>/comments/', create_comment, name='create-comment'),  # ✅ POST 요청용
    path('posts/<int:post_id>/comments/all/', get_comments, name='get-comments'),  # ✅ GET 요청용
    path('comments/<int:comment_id>/', delete_comment, name='delete-comment'),
]