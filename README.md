# whispertitles

A Django-based prototype application featuring **Audio Transcription with Speaker Diarization** and **AI-powered Blog Title Suggestions**.

🎯 Features
-----------

### Feature 1: Audio Transcription with Diarization

-   **Multi-format Audio Support**: WAV, MP3, M4A, FLAC, OGG
-   **Automatic Transcription**: Using OpenAI's Whisper model
-   **Speaker Diarization**: Identifies "who spoke when"
-   **Multilingual Support**: Auto-detects language (99+ languages supported)
-   **Structured Output**: JSON format with timestamps and speaker labels

### Feature 2: AI Blog Title Suggestions

-   **Smart Title Generation**: Uses BART/T5 transformer models
-   **Multiple Suggestions**: Generates 3 unique title options
-   **Content Analysis**: Processes blog content to extract key themes
-   **Confidence Scoring**: Each suggestion includes confidence metrics

🛠️ Technology Stack
--------------------

-   **Backend**: Django 4.2 + Django REST Framework
-   **AI/ML**:
    -   Whisper (Audio Transcription)
    -   PyAnnote Audio (Speaker Diarization)
    -   Transformers (Title Generation)
    -   PyTorch
-   **Database**: SQLite (development)
-   **File Processing**: Pydub, Librosa

📋 Requirements
---------------

-   Python 3.8+
-   8GB+ RAM (for AI models)
-   5GB+ storage (for model files)
-   GPU recommended but not required

🚀 Quick Setup
--------------

### 1\. Clone and Setup Environment

```
# Clone the repository
git clone <your-repo-url>
cd django-ai-prototype

# Run setup script
chmod +x setup.sh
./setup.sh

```

### 2\. Manual Setup (Alternative)

```
# Create virtual environment
python3 -m venv django_ai_env
source django_ai_env/bin/activate  # Windows: django_ai_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup Django
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Start server
python manage.py runserver

```

📡 API Endpoints
----------------

### Health Check

```
GET /api/health/

```

**Response:**

```
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "system_info": {
    "cuda_available": true,
    "device_count": 1
  },
  "models_status": {
    "whisper_loaded": true,
    "title_generator_loaded": true
  }
}

```

### Audio Transcription

#### Upload Audio for Transcription

```
POST /api/transcribe/
Content-Type: multipart/form-data

Body:
- audio: [audio file]

```

**Example with cURL:**

```
curl -X POST\
  http://127.0.0.1:8000/api/transcribe/\
  -F "audio=@sample_conversation.wav"

```

**Response:**

```
{
  "transcription_id": "uuid-here",
  "status": "completed",
  "language_detected": "en",
  "speakers_count": 2,
  "transcription_text": "[0:00:00 - 0:00:05] SPEAKER_00: Hello, how are you today?\n[0:00:05 - 0:00:10] SPEAKER_01: I'm doing great, thanks for asking!",
  "segments": [
    {
      "start_time": 0.0,
      "end_time": 5.2,
      "speaker": "SPEAKER_00",
      "text": "Hello, how are you today?",
      "duration": 5.2
    }
  ],
  "processed_at": "2024-01-15T10:35:00Z"
}

```

#### Get Transcription Status

```
GET /api/transcribe/{transcription_id}/

```

### Blog Title Suggestions

#### Generate Title Suggestions

```
POST /api/generate-titles/
Content-Type: application/json

{
  "content": "Your blog post content here...",
  "num_suggestions": 3
}

```

**Example with cURL:**

```
curl -X POST\
  http://127.0.0.1:8000/api/generate-titles/\
  -H "Content-Type: application/json"\
  -d '{
    "content": "Artificial intelligence is revolutionizing the way we work and live. From automating repetitive tasks to providing insights from large datasets, AI is becoming an integral part of modern business operations.",
    "num_suggestions": 3
  }'

```

**Response:**

```
{
  "blog_post_id": "uuid-here",
  "content_length": 234,
  "suggestions": [
    {
      "title": "How AI is Revolutionizing Modern Business Operations",
      "confidence": 0.8,
      "generation_method": "summarization_short"
    },
    {
      "title": "The Future of Work: AI's Impact on Business",
      "confidence": 0.7,
      "generation_method": "summarization_long"
    },
    {
      "title": "Artificial Intelligence Transforming Workplaces",
      "confidence": 0.6,
      "generation_method": "key_phrases"
    }
  ],
  "generated_at": "2024-01-15T10:40:00Z"
}

```

#### Get Blog Post Details

```
GET /api/blog-posts/{blog_post_id}/

```

🧪 Testing the APIs
-------------------

### Test Audio Transcription

1.  **Prepare an audio file** (WAV, MP3, etc.)
2.  **Upload via API**:

    ```
    curl -X POST http://127.0.0.1:8000/api/transcribe/ -F "audio=@your_audio.wav"

    ```

3.  **Check the response** for transcription results

### Test Title Generation

1.  **Send blog content**:

    ```
    curl -X POST http://127.0.0.1:8000/api/generate-titles/ \-H "Content-Type: application/json" \-d '{"content": "Write about your favorite topic here..."}'

    ```

2.  **Review generated titles**

📁 Project Structure
--------------------

```
django_ai_prototype/
├── core/                           # Main Django app
│   ├── models.py                   # Database models
│   ├── views.py                    # API views
│   ├── services.py                 # AI processing logic
│   ├── admin.py                    # Django admin config
│   └── urls.py                     # URL routing
├── media/                          # Uploaded files
│   ├── audio_files/               # Processed audio files
│   └── temp/                      # Temporary processing files
├── django_ai_prototype/           # Django project settings
│   ├── settings.py                # Main configuration
│   └── urls.py                    # Root URL config
├── requirements.txt               # Python dependencies
├── setup.sh                      # Setup script
└── manage.py                     # Django management

```

🔧 Configuration
----------------

### Audio Processing Settings

```
# In settings.py
AI_MODELS = {
    'WHISPER_MODEL': 'base',  # Options: tiny, base, small, medium, large
    'MAX_AUDIO_SIZE_MB': 50,
    'SUPPORTED_AUDIO_FORMATS': ['.wav', '.mp3', '.m4a', '.flac', '.ogg'],
}

```

### Title Generation Settings

```
AI_MODELS = {
    'TITLE_MODEL': 'facebook/bart-large-cnn',  # Or 'sshleifer/distilbart-cnn-12-6'
}

```

🚨 Troubleshooting
------------------

### Common Issues

1.  **"CUDA out of memory"**

    -   Solution: Use CPU instead by setting `CUDA_VISIBLE_DEVICES=""`
    -   Or use smaller models: `WHISPER_MODEL = 'tiny'`
2.  **"Model download failed"**

    -   Solution: Check internet connection
    -   Manually download: `python -c "import whisper; whisper.load_model('base')"`
3.  **"Audio format not supported"**

    -   Solution: Convert to WAV/MP3 first
    -   Install ffmpeg: `sudo apt install ffmpeg` (Linux) or `brew install ffmpeg` (Mac)
4.  **"Title generation too slow"**

    -   Solution: Use smaller model: `sshleifer/distilbart-cnn-12-6`

### Performance Tips

-   **Use GPU** if available for faster processing
-   **Smaller models** for development: `whisper tiny`, `distilbart-cnn-12-6`
-   **Limit file sizes** for reasonable processing times
-   **Batch processing** for multiple files

🔒 Production Considerations
----------------------------

This is a **prototype implementation**. For production:

1.  **Add authentication** and rate limiting
2.  **Use async processing** (Celery + Redis)
3.  **Add proper error handling** and logging
4.  **Use PostgreSQL** instead of SQLite
5.  **Implement file cleanup** strategies
6.  **Add monitoring** and health checks
7.  **Scale with Docker/Kubernetes**

📊 Model Performance
--------------------

### Audio Transcription

-   **Processing Time**: ~1-2 minutes for 5-minute audio
-   **Accuracy**: 85-95% depending on audio quality
-   **Languages**: 99+ languages supported
-   **Speaker Diarization**: Basic implementation (2-speaker detection)

### Title Generation

-   **Processing Time**: 2-5 seconds per request
-   **Quality**: Good for most content types
-   **Length**: Optimized for blog title length (5-15 words)

🤝 Contributing
---------------

1.  Fork the repository
2.  Create a feature branch
3.  Make your changes
4.  Add tests
5.  Submit a pull request

📄 License
----------

MIT License - feel free to use for learning and development purposes.

🆘 Support
----------

For issues and questions:

1.  Check the troubleshooting section
2.  Review the API documentation
3.  Create an issue in the repository

