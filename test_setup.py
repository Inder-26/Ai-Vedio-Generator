"""
Test script to verify setup and API connections
Run this before starting the main application
"""

import os
from dotenv import load_dotenv
import requests
from groq import Groq

def test_env_variables():
    """Test if environment variables are set"""
    print("Testing Environment Variables...")
    load_dotenv()
    
    groq_key = os.getenv('GROQ_API_KEY')
    news_key = os.getenv('NEWS_API_KEY')
    pexels_key = os.getenv('PEXELS_API_KEY')
    
    results = {
        'GROQ_API_KEY': '[OK] Set' if groq_key else '[MISSING] Missing',
        'NEWS_API_KEY': '[OK] Set' if news_key else '[MISSING] Missing',
        'PEXELS_API_KEY': '[OK] Set' if pexels_key else '[MISSING] Missing'
    }
    
    for key, status in results.items():
        print(f"  {key}: {status}")
    
    return all([groq_key, news_key, pexels_key])

def test_groq_api():
    """Test Groq API connection"""
    print("\nTesting Groq API...")
    try:
        load_dotenv()
        api_key = os.getenv('GROQ_API_KEY')
        # Try standard construction first; if that fails due to underlying HTTP client
        # signature mismatches, try passing an explicit httpx.Client as a fallback.
        try:
            client = Groq(api_key=api_key)
        except TypeError:
            try:
                import httpx
                client = Groq(api_key=api_key, http_client=httpx.Client())
            except Exception:
                # Re-raise to be caught by outer exception handler
                raise
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Say 'API working!'"}],
            max_tokens=10
        )
        
        print("  Groq API is working")
        print("  Response:", response.choices[0].message.content)
        return True
    except Exception as e:
        import traceback
        print("  Groq API failed:")
        traceback.print_exc()
        return False

def test_newsapi():
    """Test NewsAPI connection"""
    print("\nTesting NewsAPI...")
    try:
        load_dotenv()
        api_key = os.getenv('NEWS_API_KEY')
        
        url = 'https://newsapi.org/v2/top-headlines'
        params = {
            'apiKey': api_key,
            'country': 'us',
            'pageSize': 1
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data.get('status') == 'ok':
            print(f"  ✅ NewsAPI is working!")
            print(f"  Found {data.get('totalResults', 0)} articles")
            return True
        else:
            print(f"  ❌ NewsAPI failed: {data.get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"  ❌ NewsAPI failed: {str(e)}")
        return False

def test_pexels_api():
    """Test Pexels API connection"""
    print("\nTesting Pexels API...")
    try:
        load_dotenv()
        api_key = os.getenv('PEXELS_API_KEY')
        
        url = 'https://api.pexels.com/v1/search'
        headers = {'Authorization': api_key}
        params = {'query': 'nature', 'per_page': 1}
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data.get('photos'):
            print(f"  ✅ Pexels API is working!")
            print(f"  Found {len(data['photos'])} images")
            return True
        else:
            print(f"  ❌ Pexels API failed: No photos returned")
            return False
    except Exception as e:
        print(f"  ❌ Pexels API failed: {str(e)}")
        return False

def test_dependencies():
    """Test if all required packages are installed"""
    print("\nTesting Dependencies...")
    
    required_packages = [
        'flask',
        'groq',
        'requests',
        'moviepy',
        'PIL',
        'dotenv'
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            if package == 'PIL':
                __import__('PIL')
            elif package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)
            print(f"  [OK] {package}")
        except ImportError:
            print(f"  [MISSING] {package} not installed")
            all_installed = False
    
    return all_installed

def test_directories():
    """Test if required directories exist"""
    print("\nTesting Directories...")
    
    required_dirs = [
        'generated_videos',
        'static/temp_images',
        'templates'
    ]
    
    all_exist = True
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"  ✅ {directory}")
        else:
            print(f"  ❌ {directory} missing")
            all_exist = False
    
    return all_exist

def main():
    print("=" * 50)
    print("AI Video Generator - Setup Test")
    print("=" * 50)
    
    results = {
        'Environment Variables': test_env_variables(),
        'Dependencies': test_dependencies(),
        'Directories': test_directories(),
        'Groq API': test_groq_api(),
        'NewsAPI': test_newsapi(),
        'Pexels API': test_pexels_api()
    }
    
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    if all(results.values()):
        print("\n🎉 All tests passed! You're ready to run the application.")
        print("Run: python app.py")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
    
    print("=" * 50)

if __name__ == "__main__":
    main()