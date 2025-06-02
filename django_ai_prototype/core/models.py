
from django.db import models
import uuid

class AudioTranscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    audio_file = models.FileField(upload_to='audio_files/')
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()  # in bytes
    
    # Processing status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Results
    transcription_text = models.TextField(blank=True, null=True)
    language_detected = models.CharField(max_length=10, blank=True, null=True)
    speakers_count = models.PositiveIntegerField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    
    # Error handling
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Transcription {self.id} - {self.original_filename}"


class TranscriptionSegment(models.Model):
    transcription = models.ForeignKey(
        AudioTranscription, 
        on_delete=models.CASCADE, 
        related_name='segments'
    )
    
    # Segment details
    start_time = models.FloatField()  # in seconds
    end_time = models.FloatField()    # in seconds
    speaker_label = models.CharField(max_length=50)  # e.g., "SPEAKER_00", "SPEAKER_01"
    text = models.TextField()
    confidence = models.FloatField(blank=True, null=True)
    
    class Meta:
        ordering = ['start_time']
    
    def __str__(self):
        return f"{self.speaker_label}: {self.text[:50]}..."
    
    @property
    def duration(self):
        return self.end_time - self.start_time


class BlogPost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    
    # AI Generated titles
    suggested_titles = models.JSONField(blank=True, null=True)  # List of suggested titles
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title or f"Blog Post {self.id}"


class TitleSuggestion(models.Model):
    blog_post = models.ForeignKey(
        BlogPost, 
        on_delete=models.CASCADE, 
        related_name='title_suggestions'
    )
    
    suggested_title = models.CharField(max_length=200)
    confidence_score = models.FloatField(blank=True, null=True)
    model_used = models.CharField(max_length=100, default='facebook/bart-large-cnn')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-confidence_score']
    
    def __str__(self):
        return f"Title suggestion: {self.suggested_title}"