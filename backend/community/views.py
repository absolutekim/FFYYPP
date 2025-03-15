from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer

# ✅ 게시글 목록 조회 + 게시글 작성
class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)  # ✅ 작성자 자동 설정


# ✅ 게시글 상세 조회 + 삭제
class PostDetailDeleteView(generics.RetrieveDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # ✅ 댓글 목록 추가
        comments = Comment.objects.filter(post=instance).order_by('-created_at')
        comment_serializer = CommentSerializer(comments, many=True)

        data = serializer.data
        data['comments'] = comment_serializer.data  # ✅ 게시글 데이터에 댓글 추가

        return Response(data)
        
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # ✅ 작성자가 아니라면 삭제 금지
        if request.user != instance.author:
            return Response({'error': '본인이 작성한 글만 삭제할 수 있습니다.'}, status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ✅ 댓글 생성
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    serializer = CommentSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(post=post, author=request.user)  # ✅ post와 author 자동 설정
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ✅ 댓글 삭제
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.author:
        return Response({'error': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

    comment.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def get_comments(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post).order_by('-created_at')
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)
