import os
import tempfile
import logging
from django.conf import settings
from django.core.files.storage import default_storage
from pydub import AudioSegment
import re
from typing import List, Dict, Tuple
import datetime
import json
from groq import Groq

logger = logging.getLogger(__name__)

class AudioTranscriptionService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        
    def convert_to_wav(self, file_path: str) -> str:
        """Convert audio file to WAV format"""
        try:
            audio = AudioSegment.from_file(file_path)
            wav_path = file_path.rsplit('.', 1)[0] + '.wav'
            # Groq prefers 16kHz mono
            audio = audio.set_frame_rate(16000).set_channels(1)
            audio.export(wav_path, format="wav")
            return wav_path
        except Exception as e:
            logger.error(f"Error converting audio to WAV: {str(e)}")
            raise
    
    def simple_speaker_diarization(self, text: str) -> List[Dict]:
        """
        Simple speaker diarization based on sentence patterns
        Since Groq Whisper doesn't provide timestamps, we'll create segments
        """
        sentences = re.split(r'[.!?]+', text)
        segments = []
        current_time = 0.0
        
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                # Estimate duration based on word count (roughly 150 words per minute)
                word_count = len(sentence.split())
                duration = max(2.0, word_count * 0.4)  # Minimum 2 seconds per segment
                
                # Simple speaker alternation for demo
                speaker = f"SPEAKER_0{i % 2}"
                
                segments.append({
                    'start': current_time,
                    'end': current_time + duration,
                    'speaker': speaker,
                    'text': sentence.strip(),
                    'confidence': 0.8
                })
                
                current_time += duration + 0.5  # Add small pause between segments
        
        return segments
    
    def transcribe_audio(self, file_path: str) -> Dict:
        """Main transcription function using Groq API"""
        try:
            # Convert to WAV if needed
            if not file_path.lower().endswith('.wav'):
                wav_path = self.convert_to_wav(file_path)
            else:
                wav_path = file_path
            
            # Transcribe with Groq Whisper
            logger.info("Starting transcription with Groq...")
            
            with open(wav_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3",
                    response_format="json",
                    language="en",  # You can make this dynamic
                    temperature=0.0
                )
            
            # Get the transcribed text
            transcribed_text = transcription.text
            
            # Apply simple diarization
            segments = self.simple_speaker_diarization(transcribed_text)
            
            # Format result
            formatted_result = {
                'language': 'en',  # Groq doesn't return language detection
                'text': transcribed_text,
                'segments': segments,
                'speakers_detected': len(set(seg.get('speaker', 'SPEAKER_00') for seg in segments))
            }
            
            # Clean up temporary WAV file
            if wav_path != file_path and os.path.exists(wav_path):
                os.remove(wav_path)
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"Error in Groq transcription: {str(e)}")
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
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        
    def clean_content(self, content: str) -> str:
        """Clean and prepare content for title generation"""
        # Remove extra whitespace and newlines
        content = re.sub(r'\s+', ' ', content.strip())
        
        # Limit content length for API efficiency
        max_length = 2000  # Groq can handle more text
        if len(content) > max_length:
            content = content[:max_length] + "..."
        
        return content
    
    def generate_titles(self, content: str, num_titles: int = 3) -> List[Dict]:
        """Generate title suggestions using Groq API"""
        try:
            # Clean content
            cleaned_content = self.clean_content(content)
            
            if len(cleaned_content.strip()) < 50:
                return [{
                    'title': 'Blog Post Title',
                    'confidence': 0.5,
                    'method': 'fallback'
                }]
            
            # Create prompt for title generation
            prompt = f"""Based on the following blog content, generate {num_titles} engaging and SEO-friendly titles. 
            
Content: {cleaned_content}

Please respond with exactly {num_titles} titles in JSON format like this:
{{"titles": ["Title 1", "Title 2", "Title 3"]}}

Make the titles:
- Engaging and clickable
- SEO-friendly
- Between 6-12 words
- Relevant to the content
- Different in style/approach"""

            # Generate titles using Groq
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama3-8b-8192",
                temperature=0.7,
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            response_text = chat_completion.choices[0].message.content
            response_data = json.loads(response_text)
            
            titles = []
            for i, title in enumerate(response_data.get('titles', [])):
                titles.append({
                    'title': title.strip('"'),
                    'confidence': 0.9 - (i * 0.1),
                    'method': 'groq_llama3'
                })
            
            # Ensure we have the requested number of titles
            while len(titles) < num_titles:
                fallback_title = self.extract_key_phrases_title(cleaned_content)
                titles.append({
                    'title': fallback_title,
                    'confidence': 0.4,
                    'method': 'fallback'
                })
            
            return titles[:num_titles]
            
        except Exception as e:
            logger.error(f"Error generating titles with Groq: {str(e)}")
            # Return fallback titles
            return [
                {
                    'title': f'Article: {self.extract_key_phrases_title(content)}',
                    'confidence': 0.3,
                    'method': 'error_fallback'
                }
                for _ in range(num_titles)
            ]
    
    def extract_key_phrases_title(self, content: str) -> str:
        """Extract key phrases and create a title"""
        words = content.split()
        
        # Find words that might be important (longer words, capitalized)
        important_words = []
        for word in words[:50]:
            clean_word = re.sub(r'[^\w]', '', word)
            if len(clean_word) > 4 or clean_word.istitle():
                important_words.append(clean_word)
        
        if important_words:
            title = " ".join(important_words[:5])
            return title.title()
        
        return "New Blog Post"


# Global service instances (for reuse)
audio_service = AudioTranscriptionService()
title_service = TitleGenerationService()