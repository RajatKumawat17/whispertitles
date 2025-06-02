from django.contrib import admin
from .models import AudioTranscription, BlogPost

@admin.register(AudioTranscription)
class AudioTranscriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'processing_time', 'get_speaker_count']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'processing_time']
    
    def get_speaker_count(self, obj):
        return len(set(seg['speaker'] for seg in obj.speaker_segments))
    get_speaker_count.short_description = 'Speakers'

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']