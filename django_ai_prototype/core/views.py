# core/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.conf import settings
from django.utils import timezone
from django.core.files.storage import default_storage
from django.http import JsonResponse
import os
import logging
import json
from .models import AudioTranscription, TranscriptionSegment, BlogPost, TitleSuggestion
from .services import audio_service, title_service
from django.http import JsonResponse
from django.conf import settings
import datetime

logger = logging.getLogger(__name__)

class AudioTranscriptionView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """Handle audio file upload and transcription"""
        try:
            # Validate audio file
            if 'audio' not in request.FILES:
                return Response(
                    {'error': 'No audio file provided'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            audio_file = request.FILES['audio']
            
            # Validate file size
            max_size = getattr(settings, 'AI_MODELS', {}).get('MAX_AUDIO_SIZE_MB', 50) * 1024 * 1024
            if audio_file.size > max_size:
                return Response(
                    {'error': f'File too large. Maximum size: {max_size / (1024*1024):.1f}MB'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate file extension
            supported_formats = getattr(settings, 'AI_MODELS', {}).get('SUPPORTED_AUDIO_FORMATS', 
                                                                      ['.wav', '.mp3', '.m4a', '.flac'])
            file_extension = os.path.splitext(audio_file.name)[1].lower()
            if file_extension not in supported_formats:
                return Response(
                    {'error': f'Unsupported format. Supported: {", ".join(supported_formats)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create database record
            transcription = AudioTranscription.objects.create(
                audio_file=audio_file,
                original_filename=audio_file.name,
                file_size=audio_file.size,
                status='processing'
            )
            
            try:
                # Save file temporarily for processing
                file_path = default_storage.save(f'temp/{transcription.id}_{audio_file.name}', audio_file)
                full_path = default_storage.path(file_path)
                
                # Process audio
                logger.info(f"Processing audio file: {audio_file.name}")
                result = audio_service.transcribe_audio(full_path)
                
                # Update transcription record
                transcription.transcription_text = audio_service.format_transcription_output(result)
                transcription.language_detected = result.get('language', 'unknown')
                transcription.speakers_count = result.get('speakers_detected', 0)
                transcription.status = 'completed'
                transcription.processed_at = timezone.now()
                transcription.save()
                
                # Save segments
                for segment_data in result.get('segments', []):
                    TranscriptionSegment.objects.create(
                        transcription=transcription,
                        start_time=segment_data['start'],
                        end_time=segment_data['end'],
                        speaker_label=segment_data['speaker'],
                        text=segment_data['text'],
                        confidence=segment_data.get('confidence', 0)
                    )
                
                # Clean up temporary file
                if default_storage.exists(file_path):
                    default_storage.delete(file_path)
                
                # Prepare response
                response_data = {
                    'transcription_id': str(transcription.id),
                    'status': 'completed',
                    'language_detected': result.get('language'),
                    'speakers_count': result.get('speakers_detected', 0),
                    'transcription_text': transcription.transcription_text,
                    'segments': [
                        {
                            'start_time': seg.start_time,
                            'end_time': seg.end_time,
                            'speaker': seg.speaker_label,
                            'text': seg.text,
                            'duration': seg.duration
                        }
                        for seg in transcription.segments.all()
                    ],
                    'processed_at': transcription.processed_at.isoformat() if transcription.processed_at else None
                }
                
                return Response(response_data, status=status.HTTP_200_OK)
                
            except Exception as e:
                # Update transcription with error
                transcription.status = 'failed'
                transcription.error_message = str(e)
                transcription.save()
                
                logger.error(f"Transcription failed: {str(e)}")
                return Response(
                    {'error': 'Transcription failed', 'details': str(e)}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request, transcription_id=None):
        """Get transcription status or list transcriptions"""
        try:
            if transcription_id:
                # Get specific transcription
                try:
                    transcription = AudioTranscription.objects.get(id=transcription_id)
                    response_data = {
                        'transcription_id': str(transcription.id),
                        'status': transcription.status,
                        'original_filename': transcription.original_filename,
                        'language_detected': transcription.language_detected,
                        'speakers_count': transcription.speakers_count,
                        'transcription_text': transcription.transcription_text,
                        'created_at': transcription.created_at.isoformat(),
                        'processed_at': transcription.processed_at.isoformat() if transcription.processed_at else None,
                        'error_message': transcription.error_message
                    }
                    return Response(response_data, status=status.HTTP_200_OK)
                except AudioTranscription.DoesNotExist:
                    return Response(
                        {'error': 'Transcription not found'}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                # List recent transcriptions
                transcriptions = AudioTranscription.objects.all()[:20]
                response_data = {
                    'transcriptions': [
                        {
                            'transcription_id': str(t.id),
                            'status': t.status,
                            'original_filename': t.original_filename,
                            'language_detected': t.language_detected,
                            'speakers_count': t.speakers_count,
                            'created_at': t.created_at.isoformat(),
                        }
                        for t in transcriptions
                    ]
                }
                return Response(response_data, status=status.HTTP_200_OK)
                
        except Exception as e:
            logger.error(f"Error retrieving transcription: {str(e)}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BlogTitleSuggestionView(APIView):
    parser_classes = [JSONParser]
    
    def post(self, request):
        """Generate title suggestions for blog content"""
        try:
            # Validate input
            content = request.data.get('content', '').strip()
            if not content:
                return Response(
                    {'error': 'Blog content is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if len(content) < 50:
                return Response(
                    {'error': 'Content too short. Minimum 50 characters required.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Optional: Get number of suggestions
            num_suggestions = request.data.get('num_suggestions', 3)
            if not isinstance(num_suggestions, int) or num_suggestions < 1 or num_suggestions > 10:
                num_suggestions = 3
            
            # Create blog post record (optional, for tracking)
            blog_post = BlogPost.objects.create(content=content)
            
            try:
                # Generate titles
                logger.info(f"Generating {num_suggestions} titles for content length: {len(content)}")
                suggested_titles = title_service.generate_titles(content, num_suggestions)
                
                # Save suggestions to database
                for title_data in suggested_titles:
                    TitleSuggestion.objects.create(
                        blog_post=blog_post,
                        suggested_title=title_data['title'],
                        confidence_score=title_data['confidence'],
                        model_used=title_data.get('method', 'unknown')
                    )
                
                # Update blog post with suggestions
                blog_post.suggested_titles = [t['title'] for t in suggested_titles]
                blog_post.save()
                
                # Prepare response
                response_data = {
                    'blog_post_id': str(blog_post.id),
                    'content_length': len(content),
                    'suggestions': [
                        {
                            'title': title_data['title'],
                            'confidence': title_data['confidence'],
                            'generation_method': title_data.get('method', 'unknown')
                        }
                        for title_data in suggested_titles
                    ],
                    'generated_at': timezone.now().isoformat()
                }
                
                return Response(response_data, status=status.HTTP_200_OK)
                
            except Exception as e:
                logger.error(f"Title generation failed: {str(e)}")
                return Response(
                    {'error': 'Title generation failed', 'details': str(e)}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Unexpected error in title generation: {str(e)}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request, blog_post_id=None):
        """Get blog post and its title suggestions"""
        try:
            if blog_post_id:
                # Get specific blog post
                try:
                    blog_post = BlogPost.objects.get(id=blog_post_id)
                    suggestions = blog_post.title_suggestions.all()
                    
                    response_data = {
                        'blog_post_id': str(blog_post.id),
                        'content': blog_post.content,
                        'current_title': blog_post.title,
                        'suggestions': [
                            {
                                'title': suggestion.suggested_title,
                                'confidence': suggestion.confidence_score,
                                'generation_method': suggestion.model_used,
                                'created_at': suggestion.created_at.isoformat()
                            }
                            for suggestion in suggestions
                        ],
                        'created_at': blog_post.created_at.isoformat(),
                        'updated_at': blog_post.updated_at.isoformat()
                    }
                    return Response(response_data, status=status.HTTP_200_OK)
                    
                except BlogPost.DoesNotExist:
                    return Response(
                        {'error': 'Blog post not found'}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                # List recent blog posts
                blog_posts = BlogPost.objects.all()[:20]
                response_data = {
                    'blog_posts': [
                        {
                            'blog_post_id': str(post.id),
                            'title': post.title,
                            'content_preview': post.content[:100] + '...' if len(post.content) > 100 else post.content,
                            'suggestions_count': post.title_suggestions.count(),
                            'created_at': post.created_at.isoformat()
                        }
                        for post in blog_posts
                    ]
                }
                return Response(response_data, status=status.HTTP_200_OK)
                
        except Exception as e:
            logger.error(f"Error retrieving blog post: {str(e)}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HealthCheckView(APIView):
    """Simple health check endpoint"""
    
    def get(self, request):
        """Return system status"""
        import torch
        
        status_info = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'system_info': {
                'cuda_available': torch.cuda.is_available(),
                'device_count': torch.cuda.device_count() if torch.cuda.is_available() else 0,
                'python_version': f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}",
            },
            'models_status': {
                'whisper_loaded': audio_service.whisper_model is not None,
                'title_generator_loaded': title_service.generator is not None,
            },
            'endpoints': {
                'transcription': '/api/transcribe/',
                'title_suggestions': '/api/generate-titles/',
                'health': '/api/health/'
            }
        }

        
        return Response(status_info, status=status.HTTP_200_OK)