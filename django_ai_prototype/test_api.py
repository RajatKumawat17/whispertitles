
import requests
import json
import os
import sys

BASE_URL = "http://127.0.0.1:8000/api"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health/")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed!")
            print(f"   - CUDA Available: {data['system_info']['cuda_available']}")
            print(f"   - Whisper Loaded: {data['models_status']['whisper_loaded']}")
            print(f"   - Title Generator Loaded: {data['models_status']['title_generator_loaded']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_title_generation():
    """Test the title generation endpoint"""
    print("\n📝 Testing title generation endpoint...")
    
    sample_content = """
    Artificial intelligence is rapidly transforming the landscape of modern business operations. 
    From automating routine tasks to providing deep insights from complex data analysis, 
    AI technologies are becoming indispensable tools for companies seeking competitive advantages.
    
    Machine learning algorithms can now process vast amounts of information in seconds, 
    identify patterns that humans might miss, and make predictions with remarkable accuracy. 
    This capability is revolutionizing industries ranging from healthcare and finance to 
    retail and manufacturing.
    
    As businesses continue to adopt AI solutions, we're seeing improvements in efficiency, 
    cost reduction, and customer satisfaction. The future of work is being reshaped by 
    these intelligent systems that augment human capabilities rather than replace them.
    """
    
    payload = {
        "content": sample_content.strip(),
        "num_suggestions": 3
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate-titles/",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Title generation successful!")
            print(f"   - Blog Post ID: {data['blog_post_id']}")
            print(f"   - Content Length: {data['content_length']} characters")
            print("   - Generated Titles:")
            
            for i, suggestion in enumerate(data['suggestions'], 1):
                print(f"     {i}. {suggestion['title']}")
                print(f"        Confidence: {suggestion['confidence']:.2f}")
                print(f"        Method: {suggestion['generation_method']}")
            
            return True
        else:
            print(f"❌ Title generation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Title generation failed: {e}")
        return False

def test_audio_transcription():
    """Test the audio transcription endpoint (if audio file provided)"""
    print("\n🎵 Testing audio transcription endpoint...")
    
    # Look for test audio files
    test_files = ['test_audio.wav', 'sample.wav', 'test.mp3', 'audio.wav']
    audio_file_path = None
    
    for filename in test_files:
        if os.path.exists(filename):
            audio_file_path = filename
            break
    
    if not audio_file_path:
        print("⚠️  No test audio file found. Skipping audio transcription test.")
        print("   To test audio transcription, add one of these files to the current directory:")
        for filename in test_files:
            print(f"   - {filename}")
        return None
    
    print(f"   Using audio file: {audio_file_path}")
    
    try:
        with open(audio_file_path, 'rb') as audio_file:
            files = {'audio': audio_file}
            response = requests.post(f"{BASE_URL}/transcribe/", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Audio transcription successful!")
            print(f"   - Transcription ID: {data['transcription_id']}")
            print(f"   - Language Detected: {data['language_detected']}")
            print(f"   - Speakers Count: {data['speakers_count']}")
            print("   - Transcription Preview:")
            
            # Show first few lines of transcription
            lines = data['transcription_text'].split('\n')[:3]
            for line in lines:
                if line.strip():
                    print(f"     {line}")
            
            if len(data['segments']) > 0:
                print(f"   - Total Segments: {len(data['segments'])}")
            
            return True
        else:
            print(f"❌ Audio transcription failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Audio transcription failed: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ Audio file not found: {audio_file_path}")
        return False

def main():
    """Run all tests"""
    print("🚀 Django AI Prototype - API Testing")
    print("=" * 40)
    
    # Test health check first
    if not test_health_check():
        print("\n❌ Server is not running or not healthy.")
        print("   Make sure to run: python manage.py runserver")
        sys.exit(1)
    
    # Test title generation
    title_success = test_title_generation()
    
    # Test audio transcription (optional)
    audio_success = test_audio_transcription()
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Results Summary:")
    print(f"   - Health Check: ✅ Passed")
    print(f"   - Title Generation: {'✅ Passed' if title_success else '❌ Failed'}")
    
    if audio_success is not None:
        print(f"   - Audio Transcription: {'✅ Passed' if audio_success else '❌ Failed'}")
    else:
        print(f"   - Audio Transcription: ⚠️  Skipped (no test file)")
    
    if title_success and (audio_success is None or audio_success):
        print("\n🎉 All available tests passed! Your API is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()