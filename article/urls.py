from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    # path("", views.ArticleList.as_view()),
    # path("mypage/", views.Mypage.as_view()),
    # path("images/", views.ArticleAndImageList.as_view()),
    # path("<int:pk>/write/put/", views.ArticleMod.as_view()),
    path("write/", views.ArticleAdd.as_view()),
    path("<int:pk>/write/", views.ArticleDetail.as_view()),
    path("<int:pk>/write/delete/", views.ArticleDel.as_view()),
    path("comment/write/", views.CommentList.as_view()),
    # path("comment/write/<int:pk>", views.Article_Comment.as_view()),
    # path("comment/<int:pk>/write/", views.CommentDetail.as_view()),
    # path("<int:pk>/suggestion/", views.ArticleLikesDetail.as_view()),
    # path("comment/<int:pk>/suggestion/", views.CommentLikesDetail.as_view()),
    path("comment/admin/", views.CommentAdminList.as_view()),
    path("admin/<int:pk>", views.ArticleAdminList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
