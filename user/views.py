from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from community import serializers
from user.serializers import CustomUserSerializer, CustomUserTokenObtainPairSerializer, MyPageSerializer
from rest_framework import status, permissions
from django.contrib.auth import login, authenticate
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from user.models import CustomUser as CustomUserModel
from rest_framework.permissions import IsAuthenticated
# Create your views here.
class UserView(APIView):
    def post(self, request):
        user_serializer = CustomUserSerializer(data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response({"message": "가입 완료"}, status=status.HTTP_200_OK)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        permission_classes = (IsAuthenticated,)
        user = CustomUserModel.objects.get(user_id = request.user.user_id)
        if not user.check_password(request.data['password_current']):
            return Response({"message":"password doesn't match"}, status=400)
        data = {"user_id":request.user.user_id, "username":request.user.username, "password":request.data["password_change"]}
        user_serializer = CustomUserSerializer(user, data=data)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response({"message":"password changed"}, status=200)
        return Response({"message":"password for change is not valid"}, status=400)
    
class JwtTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomUserTokenObtainPairSerializer


class OnlyAuthenticatedUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user
        if not user:
            return Response(
                {"error": "접근 권한이 없습니다."}, status=status.HTTP_401_UNAUTHORIZED
            )
        return Response({"message": "인증 성공!"})


class MyPage(APIView):
    def get(self, request):
        user = CustomUserModel.objects.get(user_id = request.user.user_id)
        serializer = MyPageSerializer(user).data
        return Response(serializer)