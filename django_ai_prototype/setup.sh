#!/bin/bash
# setup.sh - Django AI Prototype Setup Script

echo "🚀 Setting up Django AI Prototype..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv django_ai_env
source django_ai_env/bin/activate  # On Windows: django_ai_env\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
echo "⬇️  Installing Python packages..."
pip install -r requirements.txt

# Create Django project structure if it doesn't exist
if [ ! -d "django_ai_prototype" ]; then
    echo "🏗️  Creating Django project..."
    django-admin startproject django_ai_prototype .
    cd django_ai_prototype
    python manage.py startapp core
    cd ..
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p media/audio_files
mkdir -p media/temp
mkdir -p static
mkdir -p logs

# Run Django setup commands
echo "🔧 Setting up Django..."
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
echo "👤 Create superuser? (y/n)"
read -r create_superuser
if [ "$create_superuser" = "y" ]; then
    python manage.py createsuperuser
fi

# Download AI models (this might take a while)
echo "🤖 Pre-downloading AI models..."
python -c "
import whisper
import transformers
print('Downloading Whisper base model...')
whisper.load_model('base')
print('Downloading BART model...')
from transformers import pipeline
pipeline('summarization', model='sshleifer/distilbart-cnn-12-6')
print('Models downloaded successfully!')
"

echo "✅ Setup complete!"
echo ""
echo "🎯 To start the development server:"
echo "   source django_ai_env/bin/activate  # On Windows: django_ai_env\\Scripts\\activate"
echo "   python manage.py runserver"
echo ""
echo "🌐 Access the application at: http://127.0.0.1:8000"
echo "🔧 Admin panel at: http://127.0.0.1:8000/admin"
echo "📚 API endpoints at: http://127.0.0.1:8000/api/health/"