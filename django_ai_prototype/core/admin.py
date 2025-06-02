# core/admin.py

from django.contrib import admin
from .models import AudioTranscription, TranscriptionSegment, BlogPost, TitleSuggestion

@admin.register(AudioTranscription)
class AudioTranscriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'original_filename', 'status', 'language_detected', 'speakers_count', 'created_at']
    list_filter = ['status', 'language_detected', 'created_at']
    search_fields = ['original_filename', 'transcription_text']
    readonly_fields = ['id', 'created_at', 'processed_at']
    
    fieldsets = (
        ('File Information', {
            'fields': ('id', 'original_filename', 'audio_file', 'file_size')
        }),
        ('Processing Status', {
            'fields': ('status', 'created_at', 'processed_at', 'error_message')
        }),
        ('Results', {
            'fields': ('language_detected', 'speakers_count', 'transcription_text')
        }),
    )

@admin.register(TranscriptionSegment)
class TranscriptionSegmentAdmin(admin.ModelAdmin):
    list_display = ['transcription', 'speaker_label', 'start_time', 'end_time', 'text_preview']
    list_filter = ['speaker_label', 'transcription__language_detected']
    search_fields = ['text', 'speaker_label']
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Text Preview'

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'content_preview', 'created_at', 'suggestions_count']
    search_fields = ['title', 'content']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content Preview'
    
    def suggestions_count(self, obj):
        return obj.title_suggestions.count()
    suggestions_count.short_description = 'Suggestions Count'

@admin.register(TitleSuggestion)
class TitleSuggestionAdmin(admin.ModelAdmin):
    list_display = ['blog_post', 'suggested_title', 'confidence_score', 'model_used', 'created_at']
    list_filter = ['model_used', 'created_at']
    search_fields = ['suggested_title', 'blog_post__title']