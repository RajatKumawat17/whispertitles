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
        self.stdout.write(self.style.SUCCESS('🤖 Setting up AI models...'))
        
        # Check system info
        self.stdout.write(f"🖥️  System Info:")
        self.stdout.write(f"   - CUDA Available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            self.stdout.write(f"   - GPU Device: {torch.cuda.get_device_name(0)}")
        self.stdout.write(f"   - PyTorch Version: {torch.__version__}")
        
        # Setup Whisper model
        whisper_model = options['whisper_model']
        self.stdout.write(f"\n📹 Setting up Whisper model: {whisper_model}")
        try:
            model = whisper.load_model(whisper_model)
            settings.WHISPER_MODEL_LOADED = True
            self.stdout.write(self.style.SUCCESS(f"✅ Whisper {whisper_model} model loaded successfully"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to load Whisper model: {str(e)}"))
            return
        
        # Setup title generation model
        title_model = options['title_model']
        self.stdout.write(f"\n📝 Setting up title generation model: {title_model}")
        
        # Try different model approaches
        models_to_try = [
            (title_model, "text2text-generation"),
            ("t5-small", "text2text-generation"), 
            ("google/pegasus-xsum", "summarization"),
            ("facebook/bart-large-cnn", "summarization")
        ]
        
        success = False
        for model_name, task in models_to_try:
            try:
                self.stdout.write(f"   Trying {model_name} for {task}...")
                device = 0 if torch.cuda.is_available() else -1
                
                if task == "text2text-generation":
                    generator = pipeline(task, model=model_name, device=device)
                    # Test with T5 format
                    test_result = generator("summarize: This is a test article about machine learning and artificial intelligence.")
                else:
                    generator = pipeline(task, model=model_name, device=device)
                    test_result = generator("This is a test article about machine learning and artificial intelligence.")
                
                self.stdout.write(self.style.SUCCESS(f"✅ {model_name} loaded successfully"))
                settings.TITLE_GENERATOR_LOADED = True
                if isinstance(test_result, list) and len(test_result) > 0:
                    output_key = 'generated_text' if task == "text2text-generation" else 'summary_text'
                    self.stdout.write(f"   Test output: {test_result[0].get(output_key, 'No output')}")
                success = True
                break
                
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"   ⚠️  {model_name} failed: {str(e)[:100]}..."))
                continue
        
        if not success:
            self.stdout.write(self.style.ERROR("❌ Failed to load any title generation model"))
            self.stdout.write("💡 Try running with internet connection or check HuggingFace access")
            return
        
        self.stdout.write(self.style.SUCCESS('\n🎉 All models setup completed successfully!'))
        self.stdout.write('\n📋 Next steps:')
        self.stdout.write('   1. Run: python manage.py migrate')
        self.stdout.write('   2. Run: python manage.py runserver')
        self.stdout.write('   3. Test endpoints at http://localhost:8000/api/health/')