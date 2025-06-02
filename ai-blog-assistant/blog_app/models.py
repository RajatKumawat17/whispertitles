from django.db import models
from django.utils import timezone

class AudioTranscription(models.Model):
    audio_file = models.FileField(upload_to='audio_uploads/')
    transcription_text = models.TextField()
    speaker_segments = models.JSONField(default=list)
    created_at = models.DateTimeField(default=timezone.now)
    processing_time = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"Transcription {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    suggested_titles = models.JSONField(default=list)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title