from django.urls import path, include, re_path
from . import views

urlpatterns = [
    path('', views.home),
    re_path('news/(?P<article_link>[^/]*)/?', views.post_detail_view)
]
