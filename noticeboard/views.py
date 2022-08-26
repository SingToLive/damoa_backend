from article import serializers
from community.models import Community as CommunityModel
from community.models import IpAndCommunity as IpAndCommunityModel
import noticeboard
from .models import Noticeboard
from article.models import Article
from .serializers import NoticeboardSerializer
from article.serializers import ArticleSerializer

# APIView를 사용하기 위해 import
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404


class NoticeboardList(APIView):
    # def get(self, request):
    #     noticeboards = Noticeboard.objects.all()
    #     serializer = NoticeboardSerializer(noticeboards, many=True)
    #     return Response(serializer.data)

    def post(self, request):
        noticeboard_object = Noticeboard.objects.filter(community=request.data['community'], name=request.data['name'])
        if noticeboard_object:
            return Response({"message":"this noticeboard already exist in this community"}, status=400)
        serializer = NoticeboardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NoticeboardDetail(APIView):
    def get_client_ip(request):
        x_forward_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forward_for:
            ip = x_forward_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get(self, request, pk):
        noticeboard = Noticeboard.objects.filter(community=pk)
        if not noticeboard:
            return Response({"message":"noticeboard doesn't exist"}, status=400)
        serializer = NoticeboardSerializer(noticeboard, many=True)
        
        community = CommunityModel.objects.get(id=pk)
        ip = NoticeboardDetail.get_client_ip(request)
        
        if not IpAndCommunityModel.objects.filter(ip=ip, community=community).exists():
            community.count += 1
            community.save()
            
            IpAndCommunityModel.objects.create(ip=ip, community=community)
            
        return Response(serializer.data, status=200)
    
class NoticeboardObject(APIView):
    def get(self, request, pk):
        noticeboard = Noticeboard.objects.filter(id=pk)
        if not noticeboard:
            return Response({"message":"noticeboard doesn't exist"}, status=400)
        serializer = NoticeboardSerializer(noticeboard, many=True)
        return Response(serializer.data, status=200)

