from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/transcribe/', views.transcribe_audio, name='transcribe_audio'),
    path('api/suggest-titles/', views.suggest_titles, name='suggest_titles'),
    path('api/transcriptions/', views.get_transcriptions, name='get_transcriptions'),
    path('api/blog-posts/', views.get_blog_posts, name='get_blog_posts'),
]