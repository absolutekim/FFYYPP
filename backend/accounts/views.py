from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from accounts.serializers import RegisterSerializer
from django.contrib.auth import authenticate
from django.db import connection
from accounts.models import CustomUser

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

         # ✅ 로그인한 사용자 인증하기
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)  # ✅ 인증 처리

        if user is None:
            return Response({"error": "Invalid credentials"}, status=401)  # ✅ 인증 실패 시 401 반환

        # ✅ 응답에서 user_id 대신 username을 반환
        response.data['username'] = user.username  

        return response

@api_view(['POST'])
@permission_classes([AllowAny])
def debug_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    print(f"🛠 DEBUG: username={username}, password={password}")  # ✅ 확인 로그 추가

    user = authenticate(username=username, password=password)

    if user is None:
        return Response({"error": "Invalid username or password"}, status=401)

    return Response({"message": "Login successful!"}, status=200)


@api_view(['POST'])
@permission_classes([AllowAny])  # ✅ 인증 없이 접근 가능하도록 설정
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_subcategory_tags(request):
    """
    여행지 태그 목록을 가져오는 API - subcategory0만 추출
    """
    with connection.cursor() as cursor:
        # 정확한 subcategory0 목록만 추출하는 쿼리
        cursor.execute("""
            SELECT DISTINCT json_extract(subcategories, '$[0]') AS first_subcategory
            FROM destinations_location
            WHERE json_extract(subcategories, '$[0]') IS NOT NULL
            ORDER BY first_subcategory;
        """)
        subcategories = [row[0] for row in cursor.fetchall() if row[0]]
        
        print("추출된 subcategory0 목록:", subcategories)
    
    return Response({"tags": subcategories}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    로그인한 사용자의 프로필 정보를 가져오는 API
    """
    user = request.user
    
    return Response({
        "username": user.username,
        "email": user.email,
        "nickname": user.nickname,
        "gender": user.gender,
        "selected_tags": user.selected_tags
    }, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_tags(request):
    """
    사용자의 태그 정보를 업데이트하는 API
    """
    user = request.user
    selected_tags = request.data.get('selected_tags', [])
    
    # 태그 개수 검증
    if len(selected_tags) < 3 or len(selected_tags) > 7:
        return Response({"error": "3개에서 7개 사이의 태그를 선택해야 합니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    user.selected_tags = selected_tags
    user.save()
    
    return Response({
        "message": "태그가 성공적으로 업데이트되었습니다.",
        "selected_tags": user.selected_tags
    }, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user_account(request):
    """
    사용자 계정을 삭제하는 API
    """
    user = request.user
    
    # 비밀번호 확인
    password = request.data.get('password')
    if not password:
        return Response({"error": "비밀번호를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)
    
    # 비밀번호 검증
    if not user.check_password(password):
        return Response({"error": "비밀번호가 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    # 계정 삭제
    try:
        user.delete()
        return Response({"message": "계정이 성공적으로 삭제되었습니다."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

