from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])  # ✅ 누구나 접근 가능하도록 설정
def welcome(request):
    return Response({"message": "Welcome to Django & Vue.js!"})
