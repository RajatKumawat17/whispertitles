from django.urls import path
from .views import (
    AudioTranscriptionView, 
    BlogTitleSuggestionView, 
    HealthCheckView
)

app_name = 'core'

urlpatterns = [
    # Health check
    path('health/', HealthCheckView.as_view(), name='health_check'),
    
    # Audio transcription endpoints
    path('transcribe/', AudioTranscriptionView.as_view(), name='transcribe_audio'),
    path('transcribe/<uuid:transcription_id>/', AudioTranscriptionView.as_view(), name='get_transcription'),
    
    # Blog title suggestion endpoints
    path('generate-titles/', BlogTitleSuggestionView.as_view(), name='generate_titles'),
    path('blog-posts/<uuid:blog_post_id>/', BlogTitleSuggestionView.as_view(), name='get_blog_post'),
    path('blog-posts/', BlogTitleSuggestionView.as_view(), name='list_blog_posts'),
]