# WhisperTitles - AI Blog Assistant

A Django web application that provides:
1. **Audio Transcription with Speaker Diarization** using Groq's Whisper API
2. **AI-powered Blog Title Suggestions** using Groq's LLaMA models

## 🚀 Quick Start (Windows)

### Prerequisites
- Python 3.8+ installed
- Git (optional)
- Groq API key ([Get it here](https://console.groq.com))

### Step 1: Download/Clone Project
```bash
# Option 1: Clone with Git
git clone [repo-url]
cd ai-blog-assistant

# Option 2: Download and extract ZIP file
# Then navigate to the extracted folder
```

### Step 2: Get Groq API Key
1. Visit [Groq Console](https://console.groq.com)
2. Sign up/Login
3. Create a new API key
4. Copy the key for later use

### Step 3: Automatic Setup (Recommended)
```bash
# Run the setup script
setup.bat
```

### Step 4: Manual Setup (Alternative)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create Django project
django-admin startproject blog_project .
python manage.py startapp blog_app

# Create directories
mkdir templates static media media\uploads media\temp

# Run migrations
python manage.py makemigrations blog_app
python manage.py migrate
```

### Step 5: Configure Environment
1. Open `.env` file in the project root
2. Replace `your_groq_api_key_here` with your actual Groq API key:
```
GROQ_API_KEY=gsk_your_actual_api_key_here
```

### Step 6: Run the Application
```bash
# Make sure virtual environment is activated
venv\Scripts\activate

# Start the server
python manage.py runserver
```

### Step 7: Test the Application
1. Open your browser and go to: `http://127.0.0.1:8000`
2. You should see the AI Blog Assistant interface

## 📡 API Endpoints

### 1. Audio Transcription with Diarization
- **URL**: `POST /api/transcribe/`
- **Input**: Audio file (mp3, wav, m4a, flac, ogg)
- **Output**: JSON with transcription and speaker segments

**Example using curl:**
```bash
curl -X POST -F "audio_file=@sample.mp3" http://127.0.0.1:8000/api/transcribe/
```

**Response:**
```json
{
  "id": 1,
  "transcription": "Hello, this is a test recording...",
  "speaker_segments": [
    {
      "speaker": "Speaker 1",
      "start_time": 0.0,
      "end_time": 2.5,
      "text": "Hello, this is a test"
    }
  ],
  "processing_time": 3.45,
  "duration": 10.2,
  "language": "en"
}
```

### 2. Blog Title Suggestions
- **URL**: `POST /api/suggest-titles/`
- **Input**: JSON with blog content
- **Output**: JSON with 3 title suggestions

**Example using curl:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"content":"This is my blog post about artificial intelligence..."}' \
  http://127.0.0.1:8000/api/suggest-titles/
```

**Response:**
```json
{
  "id": 1,
  "suggestions": [
    "The Future of AI: What You Need to Know",
    "Artificial Intelligence Explained Simply",
    "AI Revolution: Impact on Daily Life"
  ],
  "content_length": 156,
  "content_preview": "This is my blog post about artificial intelligence..."
}
```

## 🖥️ Using the Web Interface

### Audio Transcription
1. Click on the audio upload area
2. Select an audio file (MP3, WAV, M4A, FLAC, OGG)
3. Click "Transcribe Audio"
4. View the transcription and speaker segments

### Blog Title Generation
1. Enter your blog post content (minimum 50 characters)
2. Click "Generate Title Suggestions"
3. View 3 AI-generated title suggestions
4. Click "Copy" to copy any title to clipboard

## 🔧 Project Structure
```
ai-blog-assistant/
├── venv/                      # Virtual environment
├── blog_project/              # Django project settings
│   ├── __init__.py
│   ├── settings.py           # Main configuration
│   ├── urls.py              # URL routing
│   └── wsgi.py
├── blog_app/                 # Main application
│   ├── models.py            # Database models
│   ├── views.py             # API endpoints
│   ├── urls.py              # App URLs
│   ├── admin.py             # Admin interface
│   └── apps.py
├── templates/
│   └── index.html           # Frontend interface
├── static/                  # Static files
├── media/                   # Uploaded files
│   ├── uploads/             # Permanent uploads
│   └── temp/                # Temporary files
├── requirements.txt         # Dependencies
├── .env                     # Environment variables
├── setup.bat               # Windows setup script
└── README.md
```

## 🧪 Testing Examples

### Test Audio Transcription
1. Record a short audio clip or download a sample
2. Upload via web interface or use curl:
```bash
curl -X POST -F "audio_file=@test.mp3" http://127.0.0.1:8000/api/transcribe/
```

### Test Title Generation
1. Use the web interface or curl:
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"content":"Technology is rapidly changing how we work and live. From artificial intelligence to automation, these innovations are reshaping industries and creating new opportunities for businesses and individuals alike."}' \
  http://127.0.0.1:8000/api/suggest-titles/
```

## 🛠️ Troubleshooting

### Common Issues

**1. ModuleNotFoundError**
```bash
# Make sure virtual environment is activated
venv\Scripts\activate
pip install -r requirements.txt
```

**2. Groq API Error**
- Check your API key in `.env` file
- Ensure you have credits in your Groq account
- Verify the API key format: `gsk_...`

**3. Audio Upload Error**
- Check file format (MP3, WAV, M4A, FLAC, OGG only)
- Ensure file size is under 50MB
- Try a different audio file

**4. Port Already in Use**
```bash
# Use a different port
python manage.py runserver 8001
```

### Environment Setup Issues
```bash
# If Python is not recognized
# Add Python to your system PATH or use full path:
C:\Python39\python.exe -m venv venv

# If pip is not working
python -m ensurepip --upgrade
```

## 📊 Features

### Audio Transcription
- ✅ Multiple audio formats supported
- ✅ Speaker diarization (identifies who spoke when)
- ✅ Accurate transcription using Groq's Whisper
- ✅ Processing time and duration metrics
- ✅ Language detection
- ✅ Multilingual support

### Blog Title Generation
- ✅ AI-powered suggestions using LLaMA models
- ✅ SEO-friendly titles
- ✅ Context-aware generation
- ✅ Multiple suggestions per request
- ✅ Copy-to-clipboard functionality

### Web Interface
- ✅ Modern, responsive design
- ✅ Real-time processing feedback
- ✅ Recent results history
- ✅ Drag-and-drop file upload
- ✅ Character counter for content

## 🔐 Security Notes
- Audio files are temporarily stored and automatically deleted
- API keys are stored in environment variables
- CSRF protection enabled for web forms
- File upload size limits enforced

## 🚀 Deployment Notes
For production deployment:
1. Set `DEBUG=False` in `.env`
2. Configure proper database (PostgreSQL recommended)
3. Set up static file serving
4. Use HTTPS
5. Configure proper allowed hosts

## 📝 License
This project is for educational and evaluation purposes.

## 🤝 Support
If you encounter any issues:
1. Check the troubleshooting section
2. Ensure all dependencies are installed
3. Verify your Groq API key is correct
4. Check the console for error messages
