# core/management/commands/setup_models.py
from django.core.management.base import BaseCommand
from django.conf import settings
import whisper
from transformers import pipeline
import torch
import os

settings.WHISPER_MODEL_LOADED = False
settings.TITLE_GENERATOR_LOADED = False

class Command(BaseCommand):
    help = 'Download and setup AI models for the application'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--whisper-model',
            type=str,
            default='base',
            help='Whisper model size to download (tiny, base, small, medium, large)'
        )
        parser.add_argument(
            '--title-model', 
            type=str,
            default='t5-small',
            help='Title generation model to download'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-download of models'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🤖 Validating Groq API connection...'))
        
        try:
            from groq import Groq
            client = Groq(api_key=settings.GROQ_API_KEY)
            
            # Test API connectivity
            models = client.models.list()
            self.stdout.write(self.style.SUCCESS('✅ Groq API connection successful'))
            self.stdout.write(f'Available models: {len(models.data)}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Groq API connection failed: {str(e)}'))
            return
        
        self.stdout.write(self.style.SUCCESS('\n🎉 API setup completed successfully!'))