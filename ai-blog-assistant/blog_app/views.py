import os
import json
import time
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from groq import Groq
import librosa
import soundfile as sf
import numpy as np
from .models import AudioTranscription, BlogPost

# Initialize Groq client
client = Groq(api_key=settings.GROQ_API_KEY)

def index(request):
    """Main page with frontend interface"""
    return render(request, 'index.html')

@csrf_exempt
@require_http_methods(["POST"])
def transcribe_audio(request):
    """Audio transcription with speaker diarization using Groq API"""
    try:
        if 'audio_file' not in request.FILES:
            return JsonResponse({'error': 'No audio file provided'}, status=400)
        
        audio_file = request.FILES['audio_file']
        
        # Validate file type
        allowed_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg']
        file_ext = os.path.splitext(audio_file.name)[1].lower()
        if file_ext not in allowed_extensions:
            return JsonResponse({'error': 'Unsupported file format'}, status=400)
        
        # Save uploaded file temporarily
        file_path = default_storage.save(f'temp/{audio_file.name}', ContentFile(audio_file.read()))
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        
        start_time = time.time()
        
        try:
            # Transcribe using Groq Whisper
            with open(full_path, "rb") as file:
                transcription = client.audio.transcriptions.create(
                    file=file,
                    model="whisper-large-v3",
                    response_format="verbose_json",
                    timestamp_granularities=["word"]
                )
            
            # Process audio for speaker diarization simulation
            audio_data, sr = librosa.load(full_path, sr=16000)
            duration = len(audio_data) / sr
            
            # Simple speaker diarization simulation based on audio characteristics
            speaker_segments = perform_simple_diarization(audio_data, sr, transcription.text)
            
            processing_time = time.time() - start_time
            
            # Save to database
            transcription_obj = AudioTranscription.objects.create(
                audio_file=file_path,
                transcription_text=transcription.text,
                speaker_segments=speaker_segments,
                processing_time=processing_time
            )
            
            response_data = {
                'id': transcription_obj.id,
                'transcription': transcription.text,
                'speaker_segments': speaker_segments,
                'processing_time': round(processing_time, 2),
                'duration': round(duration, 2),
                'language': getattr(transcription, 'language', 'unknown')
            }
            
            return JsonResponse(response_data)
            
        finally:
            # Clean up temporary file
            if os.path.exists(full_path):
                os.remove(full_path)
                
    except Exception as e:
        return JsonResponse({'error': f'Transcription failed: {str(e)}'}, status=500)

def perform_simple_diarization(audio_data, sr, transcription_text):
    """Simple speaker diarization based on audio energy and pauses"""
    # Split audio into segments based on silence
    frame_length = int(0.5 * sr)  # 0.5 second frames
    energy = []
    
    for i in range(0, len(audio_data), frame_length):
        frame = audio_data[i:i+frame_length]
        energy.append(np.mean(frame**2))
    
    # Identify speech segments vs silence
    energy = np.array(energy)
    threshold = np.mean(energy) * 0.1
    
    segments = []
    words = transcription_text.split()
    current_speaker = 1
    word_index = 0
    
    # Simple speaker assignment based on energy changes
    for i, eng in enumerate(energy):
        start_time = i * 0.5
        end_time = (i + 1) * 0.5
        
        if eng > threshold and word_index < len(words):
            # Assign speaker based on energy patterns
            if i > 0 and abs(eng - energy[i-1]) > np.std(energy):
                current_speaker = 2 if current_speaker == 1 else 1
            
            # Get words for this segment
            segment_words = []
            while word_index < len(words) and len(segment_words) < 5:
                segment_words.append(words[word_index])
                word_index += 1
            
            if segment_words:
                segments.append({
                    'speaker': f'Speaker {current_speaker}',
                    'start_time': round(start_time, 2),
                    'end_time': round(end_time, 2),
                    'text': ' '.join(segment_words)
                })
    
    return segments

@csrf_exempt
@require_http_methods(["POST"])
def suggest_titles(request):
    """Generate blog post title suggestions using Groq API"""
    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        
        if not content:
            return JsonResponse({'error': 'No content provided'}, status=400)
        
        if len(content) < 50:
            return JsonResponse({'error': 'Content too short. Please provide at least 50 characters.'}, status=400)
        
        # Generate title suggestions using Groq
        prompt = f"""
        Based on the following blog post content, suggest 3 engaging and SEO-friendly titles. 
        The titles should be catchy, informative, and between 40-60 characters.
        
        Content: {content[:1000]}...
        
        Please respond with exactly 3 titles, one per line, without numbering or bullet points.
        """
        
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert content marketer and SEO specialist. Generate compelling blog post titles that are engaging, SEO-friendly, and click-worthy."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        suggestions_text = completion.choices[0].message.content.strip()
        suggestions = [title.strip() for title in suggestions_text.split('\n') if title.strip()]
        
        # Ensure we have exactly 3 suggestions
        while len(suggestions) < 3:
            suggestions.append(f"Title Suggestion {len(suggestions) + 1}")
        suggestions = suggestions[:3]
        
        # Save to database
        blog_post = BlogPost.objects.create(
            title=suggestions[0],
            content=content,
            suggested_titles=suggestions
        )
        
        response_data = {
            'id': blog_post.id,
            'suggestions': suggestions,
            'content_length': len(content),
            'content_preview': content[:200] + '...' if len(content) > 200 else content
        }
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Title generation failed: {str(e)}'}, status=500)

@require_http_methods(["GET"])
def get_transcriptions(request):
    """Get all transcriptions"""
    transcriptions = AudioTranscription.objects.all().order_by('-created_at')[:10]
    data = []
    
    for t in transcriptions:
        data.append({
            'id': t.id,
            'created_at': t.created_at.isoformat(),
            'transcription': t.transcription_text[:200] + '...' if len(t.transcription_text) > 200 else t.transcription_text,
            'speaker_count': len(set(seg['speaker'] for seg in t.speaker_segments)),
            'processing_time': t.processing_time
        })
    
    return JsonResponse({'transcriptions': data})

@require_http_methods(["GET"])
def get_blog_posts(request):
    """Get all blog posts"""
    posts = BlogPost.objects.all().order_by('-created_at')[:10]
    data = []
    
    for post in posts:
        data.append({
            'id': post.id,
            'title': post.title,
            'content_preview': post.content[:200] + '...' if len(post.content) > 200 else post.content,
            'suggested_titles': post.suggested_titles,
            'created_at': post.created_at.isoformat()
        })
    
    return JsonResponse({'blog_posts': data})