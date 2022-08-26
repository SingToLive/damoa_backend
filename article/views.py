import article
from community.models import UserAndCommunity
from .models import Article, ArticleLikes, Comment, CommentLikes, ArticleAndImage, NoticeboardModel, IpAndArticle
from user.models import CustomUser as CustomUserModel
from noticeboard.models import Noticeboard as NoticboardModel

from .serializers import (
    ArticleSerializer,
    ArticleLikesSerializer,
    CommentSerializer,
    CommentLikesSerializer,
    ArticleAndImageSerializer,
    ArticleToolSerializer,
    ArticleSerializerForMyPage,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.db.models import Prefetch
import run_model.lstm as lstm


# class ArticleList(APIView):
#     def get(self, request):
#         articles = Article.objects.all()
#         serializer = ArticleSerializer(articles, many=True)
#         return Response(serializer.data)

class ArticleAdminList(APIView):
    def get(self, request, pk):
        admin_object = CustomUserModel.objects.filter(id=request.user.id, userandcommunity__is_admin=True, userandcommunity__community=pk)
        # admin_object = CustomUserModel.objects.prefetch_related(
        #     Prefetch("userandcommunity_set",
        #              queryset=UserAndCommunity.objects.all(),
        #              to_attr='userandcommunity')).filter(id=request.user.id, userandcommunity__is_admin=True)
        if not admin_object:
            return Response({"message":"not admin"}, status=400)
        is_valid_articles = Article.objects.filter(is_valid=False)
        serializer = ArticleSerializer(is_valid_articles, many=True)
        return Response(serializer.data, status=200)


class ArticleAdd(APIView):
    def change_data(self, data):
        change_data_dict = {}
        user_info = eval(data["user_id"])
        change_data_dict["user"] = CustomUserModel.objects.get(
            username=user_info["username"]
        ).id
        change_data_dict["title"] = data["title"]
        change_data_dict["noticeboard"] = NoticboardModel.objects.get(
            id=int(data["noticeboard"])
        ).id
        if data["file"] == "undefined":
            change_data_dict["file"] = None
        else:
            change_data_dict["file"] = data["file"]
        change_data_dict["content"] = data["content"]
        if lstm.sentiment_predict(data["content"]) < 50:
            change_data_dict["is_valid"] = True
        else:
            change_data_dict["is_valid"] = False
        return change_data_dict

    def get(self, request):
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True).data
        return Response(serializer, status=status.HTTP_200_OK)

    def post(self, request):
        if (request.data["title"] == "") or (request.data["content"] == ""):
            return Response({"message": "contents_error"}, status=400)
        try:
            data = ArticleAdd.change_data(self, request.data)
        except:
            return Response({'message':'data is wrong'}, status=400)
        # image_data = {}
        # for i in range(5):
        #     try:
        #         image_data[f"image_{i}"] = request.data[f"image_{i}"]
        #     except:
        #         break
        make_article_serializer = ArticleToolSerializer(data=data)
        if make_article_serializer.is_valid():
            make_article_serializer.save()
            return Response({"message": "success"}, status=200)
    
    def put(self, request):
        if (request.data["title"] == "") or (request.data["content"] == ""):
            return Response({"message": "contents_error"}, status=400)
        try:
            data = ArticleAdd.change_data(self, request.data)
        except:
            return Response({"message":"data is not valid"}, status=400)
        article = Article.objects.get(id=request.data['article'])
        make_article_serializer = ArticleToolSerializer(article, data=data)
        if make_article_serializer.is_valid():
            make_article_serializer.save()
            return Response({"message": "success"}, status=200)
        # return Response({"message":make_article_serializer.errors}, status=400)
    
    def delete(self, request):
        article_object = Article.objects.filter(id=request.data['request_id'])
        if not article_object:
            return Response({"message":"article id is not valid"}, status=400)
        article_object.delete()
        return Response(status=200)
        
    
class ArticleDetail(APIView):
    def get_object(self, pk):
        try:
            return Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            raise Http404
    
    def get_client_ip(self, request):
        x_forward_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forward_for:
            ip = x_forward_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 
    
    def get(self, request, pk, format=None):
        article = self.get_object(pk)
        serializer = ArticleSerializer(article)

        ip = self.get_client_ip(request)
        if not IpAndArticle.objects.filter(ip=ip, article=article).exists(): 
            article.count += 1
            article.save()
            IpAndArticle.objects.create(ip=ip, article=article)
        return Response(serializer.data)


class ArticleView(APIView):
    def get(self, request, pk):
        article = Article.objects.filter(noticeboard=pk)
        serializer = ArticleSerializer(article, many=True)
        return Response(serializer.data, status=200)        


# class ArticleMod(APIView):
#     def get_object(self, pk):
#         try:
#             return Article.objects.get(pk=pk)
#         except Article.DoesNotExist:
#             raise Http404

#     def put(self, request, pk):
#         print(request.data)
#         print(pk)
#         article = self.get_object(pk)
#         serializer = ArticleSerializer(article, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArticleDel(APIView):
    def get_object(self, pk):
        try:
            return Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            raise Http404
        
    def delete(self, request, pk):
        article = self.get_object(pk)
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# class ArticleAndImageList(APIView):
#     def get(self, request):
#         images = ArticleAndImage.objects.filter(article=id)
#         serializer = ArticleAndImageSerializer(images, many=True)
#         return Response(serializer.data)


# class Mypage(APIView):
#     def get(self, request):
#         mypage = Article.objects.all()
#         serializer = ArticleSerializerForMyPage(mypage, many=True)
#         return Response(serializer.data)


class CommentAdminList(APIView):
    def get(self, request):
        comments = Comment.objects.all()
        is_valid_comments = comments.filter(is_valid=True)
        serializer = CommentSerializer(is_valid_comments, many=True)
        return Response(serializer.data)


class CommentList(APIView):
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data) 

    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        comment_object = Comment.objects.filter(id=request.data['request_id'])
        if not comment_object:
            return Response({'message':'can not find community object'}, status=404)
        comment_object.delete()
        return Response({'message':'delete success'}, status=200)
    
# class Article_Comment(APIView):
#      def get(self, request, pk):
#         comments = Comment.objects.filter(article_id=pk)
#         serializer = CommentSerializer(comments, many=True)
#         return Response(serializer.data)   


# class CommentDetail(APIView):
#     def get_object(self, pk):
#         try:
#             return Comment.objects.get(pk=pk)
#         except Comment.DoesNotExist:
#             raise Http404

#     def get(self, request, pk, format=None):
#         comment = self.get_object(pk)
#         serializer = CommentSerializer(comment)
#         return Response(serializer.data)


class CommentMod(APIView):
    def get_object(self, pk):
        try:
            return Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        Comment = self.get_object(pk)
        serializer = CommentSerializer(Comment)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        comment = self.get_object(pk)
        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDel(APIView):
    def get_object(self, pk):
        try:
            return Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        Comment = self.get_object(pk)
        serializer = CommentSerializer(Comment)
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        comment = self.get_object(pk)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# class ArticleLikesDetail(APIView):
#     def get_object(self, pk):
#         try:
#             return ArticleLikes.objects.get(pk=pk)
#         except ArticleLikes.DoesNotExist:
#             raise Http404

#     def get(self, request, pk, format=None):
#         articleLikes = self.get_object(pk)
#         serializer = ArticleLikesSerializer(articleLikes)
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = ArticleLikesSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def put(self, request, pk, format=None):
#         articleLikes = self.get_object(pk)
#         serializer = ArticleLikesSerializer(articleLikes, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class CommentLikesDetail(APIView):
#     def get_object(self, pk):
#         try:
#             return CommentLikes.objects.get(pk=pk)
#         except CommentLikes.DoesNotExist:
#             raise Http404

#     def get(self, request, pk, format=None):
#         commentLikes = self.get_object(pk)
#         serializer = CommentLikesSerializer(commentLikes)
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = CommentLikesSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def put(self, request, pk, format=None):
#         commentLikes = self.get_object(pk)
#         serializer = CommentLikesSerializer(commentLikes, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)