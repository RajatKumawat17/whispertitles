# Whispertitles - Audio Transcription & Blog Title Generation

A simplified Django application that implements two AI-powered features:
1. **Audio Transcription with Speaker Diarization**
2. **AI-Powered Blog Title Suggestions**

## Features

### Feature 1: Audio Transcription with Diarization
- Transcribes audio files using Groq's Whisper API
- Identifies different speakers in the audio
- Supports multiple audio formats (WAV, MP3, M4A, FLAC)
- Returns structured JSON with speaker segments and timestamps

### Feature 2: Blog Title Suggestions
- Generates 3 engaging title suggestions for blog content
- Uses Groq's LLaMA model for natural language processing
- SEO-friendly and clickable titles
- Analyzes content to create relevant suggestions

## Prerequisites

- Python 3.8+
- Django 4.2+
- Groq API Key (free at [groq.com](https://groq.com))

## Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd django_ai_prototype
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_api_key_here
```

**Get your Groq API key:**
1. Visit [console.groq.com](https://console.groq.com)
2. Sign up/login
3. Create a new API key
4. Copy the key to your `.env` file

### 5. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # Optional: for admin access
```

### 6. Run the Server
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## API Endpoints

### 1. Audio Transcription Endpoint

**POST** `/api/transcribe/`

Upload an audio file and get transcription with speaker diarization.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: audio file (key: 'audio')

**Example using cURL:**
```bash
curl -X POST \
  http://localhost:8000/api/transcribe/ \
  -F "audio=@/path/to/your/audio.wav"
```

**Response:**
```json
{
  "transcription_id": "123e4567-e89b-12d3-a456-426614174000",
  "text": "Hello, my name is John. Hi John, nice to meet you.",
  "language": "en",
  "speakers_count": 2,
  "segments": [
    {
      "start_time": 0.0,
      "end_time": 3.2,
      "speaker": "SPEAKER_0",
      "text": "Hello, my name is John"
    },
    {
      "start_time": 3.7,
      "end_time": 6.5,
      "speaker": "SPEAKER_1", 
      "text": "Hi John, nice to meet you"
    }
  ]
}
```

### 2. Blog Title Generation Endpoint

**POST** `/api/generate-titles/`

Generate title suggestions for blog content.

**Request:**
- Method: POST
- Content-Type: application/json
- Body: JSON with blog content

**Example using cURL:**
```bash
curl -X POST \
  http://localhost:8000/api/generate-titles/ \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Artificial Intelligence is transforming the way we work and live. From automated customer service to predictive analytics, AI is becoming an integral part of modern business operations. Companies that embrace AI early are seeing significant improvements in efficiency and customer satisfaction."
  }'
```

**Response:**
```json
{
  "blog_post_id": "987fcdeb-51a2-43d1-9c4f-123456789abc",
  "content_length": 284,
  "suggested_titles": [
    "How AI is Revolutionizing Modern Business Operations",
    "The Future of Work: AI's Impact on Efficiency and Customer Service", 
    "Why Early AI Adoption Gives Companies a Competitive Edge"
  ]
}
```

## Testing the API

### Using Python Requests
```python
import requests

# Test audio transcription
with open('audio.wav', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/transcribe/',
        files={'audio': f}
    )
print(response.json())

# Test title generation
response = requests.post(
    'http://localhost:8000/api/generate-titles/',
    json={
        'content': 'Your blog content here...'
    }
)
print(response.json())
```

### Using JavaScript (Frontend)
```javascript
// Audio transcription
const formData = new FormData();
formData.append('audio', audioFile);

fetch('/api/transcribe/', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log(data));

// Title generation
fetch('/api/generate-titles/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        content: 'Your blog content here...'
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

## File Structure
```
django_ai_prototype/
├── django_ai_prototype/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/
│   ├── __init__.py
│   ├── admin.py
│   ├── models.py
│   ├── services.py
│   ├── views.py
│   └── urls.py
├── manage.py
├── requirements.txt
├── .env
└── README.md
```

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Missing or invalid input
- **413 Request Entity Too Large**: Audio file exceeds 25MB limit
- **500 Internal Server Error**: Processing failures

**Example error response:**
```json
{
  "error": "File too large. Max size: 25MB"
}
```

## Supported Audio Formats

- WAV (recommended)
- MP3
- M4A
- FLAC
- OGG

**Audio file requirements:**
- Maximum size: 25MB
- Recommended: 16kHz mono WAV files for best results

## Limitations

1. **Speaker Diarization**: Uses simple rule-based diarization for demo purposes
2. **Language Detection**: Currently set to English
3. **File Size**: Limited to 25MB per Groq API constraints
4. **Rate Limits**: Subject to Groq API rate limits

## Development Notes

### Model Information
- **Transcription**: Groq Whisper Large V3
- **Title Generation**: Groq LLaMA 3 8B
- **Database**: SQLite (development)

### Extending the Application

To add more features:
1. Extend models in `core/models.py`
2. Add new services in `core/services.py`  
3. Create new views in `core/views.py`
4. Update URLs in `core/urls.py`

## Troubleshooting

### Common Issues

1. **"No module named 'groq'"**
   ```bash
   pip install groq
   ```

2. **"GROQ_API_KEY not found"**
   - Ensure `.env` file exists with valid API key
   - Check environment variable is loaded

3. **Audio processing errors**
   - Ensure pydub is installed: `pip install pydub`
   - Check audio file format and size

4. **Database errors**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

## License

This project is for demonstration purposes. Please check individual package licenses for production use.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Verify API key configuration
3. Ensure all dependencies are installed
4. Check Django logs for detailed error messages
