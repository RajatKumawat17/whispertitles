# core/services.py

import whisper
import torch
import os
import tempfile
import logging
from django.conf import settings
from django.core.files.storage import default_storage
from pydub import AudioSegment
from pyannote.audio import Pipeline
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import re
from typing import List, Dict, Tuple
import datetime

logger = logging.getLogger(__name__)

class AudioTranscriptionService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.whisper_model = None
        self.diarization_pipeline = None
        
    def load_models(self):
        """Load Whisper and diarization models"""
        if self.whisper_model is None:
            model_size = getattr(settings, 'AI_MODELS', {}).get('WHISPER_MODEL', 'base')
            logger.info(f"Loading Whisper model: {model_size}")
            self.whisper_model = whisper.load_model(model_size, device=self.device)
        
        # Note: For prototype, we'll use a simpler approach without pyannote.audio
        # as it requires HuggingFace token. We'll implement basic speaker detection.
        
    def convert_to_wav(self, file_path: str) -> str:
        """Convert audio file to WAV format"""
        try:
            audio = AudioSegment.from_file(file_path)
            wav_path = file_path.rsplit('.', 1)[0] + '.wav'
            audio.export(wav_path, format="wav", parameters=["-ar", "16000"])
            return wav_path
        except Exception as e:
            logger.error(f"Error converting audio to WAV: {str(e)}")
            raise
    
    def simple_speaker_diarization(self, segments: List[Dict]) -> List[Dict]:
        """
        Simple speaker diarization based on pause detection
        This is a basic implementation for prototype purposes
        """
        if not segments:
            return segments
            
        # Assign speakers based on pause patterns
        diarized_segments = []
        current_speaker = "SPEAKER_00"
        speaker_count = 0
        
        for i, segment in enumerate(segments):
            # Simple logic: if there's a significant pause, assume speaker change
            if i > 0:
                prev_end = segments[i-1].get('end', 0)
                current_start = segment.get('start', 0) 
                pause_duration = current_start - prev_end
                
                # If pause > 2 seconds, assume speaker change
                if pause_duration > 2.0:
                    speaker_count = (speaker_count + 1) % 2  # Toggle between 2 speakers
                    current_speaker = f"SPEAKER_0{speaker_count}"
            
            segment['speaker'] = current_speaker
            diarized_segments.append(segment)
        
        return diarized_segments
    
    def transcribe_audio(self, file_path: str) -> Dict:
        """Main transcription function"""
        try:
            self.load_models()
            
            # Convert to WAV if needed
            if not file_path.lower().endswith('.wav'):
                wav_path = self.convert_to_wav(file_path)
            else:
                wav_path = file_path
            
            # Transcribe with Whisper
            logger.info("Starting transcription...")
            result = self.whisper_model.transcribe(wav_path, verbose=True)
            
            # Apply simple diarization
            segments = self.simple_speaker_diarization(result.get('segments', []))
            
            # Format result
            formatted_result = {
                'language': result.get('language', 'unknown'),
                'text': result.get('text', ''),
                'segments': [],
                'speakers_detected': len(set(seg.get('speaker', 'SPEAKER_00') for seg in segments))
            }
            
            # Format segments
            for segment in segments:
                formatted_segment = {
                    'start': segment.get('start', 0),
                    'end': segment.get('end', 0),
                    'speaker': segment.get('speaker', 'SPEAKER_00'),
                    'text': segment.get('text', '').strip(),
                    'confidence': segment.get('avg_logprob', 0)
                }
                formatted_result['segments'].append(formatted_segment)
            
            # Clean up temporary WAV file
            if wav_path != file_path and os.path.exists(wav_path):
                os.remove(wav_path)
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"Error in transcription: {str(e)}")
            raise

    def format_transcription_output(self, result: Dict) -> str:
        """Format transcription result as readable text"""
        output_lines = []
        output_lines.append(f"Language Detected: {result.get('language', 'Unknown')}")
        output_lines.append(f"Speakers Detected: {result.get('speakers_detected', 0)}")
        output_lines.append("-" * 50)
        
        for segment in result.get('segments', []):
            start_time = str(datetime.timedelta(seconds=int(segment['start'])))
            end_time = str(datetime.timedelta(seconds=int(segment['end']))) 
            speaker = segment['speaker']
            text = segment['text']
            
            output_lines.append(f"[{start_time} - {end_time}] {speaker}: {text}")
        
        return "\n".join(output_lines)


class TitleGenerationService:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.generator = None
        
    def load_model(self):
        """Load the title generation model"""
        if self.generator is None:
            model_name = getattr(settings, 'AI_MODELS', {}).get('TITLE_MODEL', 'facebook/bart-large-cnn')
            logger.info(f"Loading title generation model: {model_name}")
            
            try:
                # Use pipeline for simplicity
                self.generator = pipeline(
                    "summarization",
                    model=model_name,
                    tokenizer=model_name,
                    device=0 if torch.cuda.is_available() else -1
                )
            except Exception as e:
                logger.warning(f"Failed to load {model_name}, falling back to distilbart")
                # Fallback to smaller model
                self.generator = pipeline(
                    "summarization", 
                    model="sshleifer/distilbart-cnn-12-6",
                    device=0 if torch.cuda.is_available() else -1
                )
    
    def clean_content(self, content: str) -> str:
        """Clean and prepare content for title generation"""
        # Remove extra whitespace and newlines
        content = re.sub(r'\s+', ' ', content.strip())
        
        # Limit content length (models have token limits)
        max_length = 1000  # characters
        if len(content) > max_length:
            content = content[:max_length] + "..."
        
        return content
    
    def generate_titles(self, content: str, num_titles: int = 3) -> List[Dict]:
        """Generate title suggestions for blog content"""
        try:
            self.load_model()
            
            # Clean content
            cleaned_content = self.clean_content(content)
            
            if len(cleaned_content.strip()) < 50:
                return [{
                    'title': 'Blog Post Title',
                    'confidence': 0.5,
                    'method': 'fallback'
                }]
            
            # Generate multiple titles with different parameters
            titles = []
            
            # Method 1: Direct summarization (short)
            try:
                result1 = self.generator(
                    cleaned_content,
                    max_length=15,
                    min_length=3,
                    do_sample=True,
                    temperature=0.7
                )
                titles.append({
                    'title': result1[0]['summary_text'],
                    'confidence': 0.8,
                    'method': 'summarization_short'
                })
            except:
                pass
            
            # Method 2: Longer summarization
            try:
                result2 = self.generator(
                    cleaned_content,
                    max_length=25,
                    min_length=5,
                    do_sample=True,
                    temperature=0.9
                )
                titles.append({
                    'title': result2[0]['summary_text'],
                    'confidence': 0.7,
                    'method': 'summarization_long'
                })
            except:
                pass
            
            # Method 3: Extract key phrases as title
            key_phrases_title = self.extract_key_phrases_title(cleaned_content)
            if key_phrases_title:
                titles.append({
                    'title': key_phrases_title,
                    'confidence': 0.6,
                    'method': 'key_phrases'
                })
            
            # Ensure we have at least num_titles
            while len(titles) < num_titles:
                titles.append({
                    'title': f"Blog Post About {cleaned_content.split()[0:3]}",
                    'confidence': 0.4,
                    'method': 'fallback'
                })
            
            # Return top num_titles
            return titles[:num_titles]
            
        except Exception as e:
            logger.error(f"Error generating titles: {str(e)}")
            # Return fallback titles
            return [
                {
                    'title': 'New Blog Post',
                    'confidence': 0.3,
                    'method': 'error_fallback'
                }
                for _ in range(num_titles)
            ]
    
    def extract_key_phrases_title(self, content: str) -> str:
        """Extract key phrases and create a title"""
        # Simple approach: take first few important words
        words = content.split()
        
        # Find words that might be important (longer words, capitalized)
        important_words = []
        for word in words[:50]:  # Look at first 50 words
            clean_word = re.sub(r'[^\w]', '', word)
            if len(clean_word) > 4 or clean_word.istitle():
                important_words.append(clean_word)
        
        if important_words:
            title = " ".join(important_words[:5])  # Take first 5 important words
            return title.title()
        
        return None


# Global service instances (for reuse)
audio_service = AudioTranscriptionService()
title_service = TitleGenerationService()