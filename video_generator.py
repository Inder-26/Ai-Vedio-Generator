import os
from urllib import response
import requests
import json
import textwrap
from datetime import datetime
from groq import Groq
from moviepy.editor import ImageClip, CompositeVideoClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont

# --- CRITICAL FIX: Tell the system there is NO proxy ---
os.environ['NO_PROXY'] = '*' 
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)

class VideoGenerator:
    def __init__(self):
        # 1. Load Keys
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.newsapi_key = os.getenv('NEWS_API_KEY')
        self.pexels_api_key = os.getenv('PEXELS_API_KEY')
        
        if not all([self.groq_api_key, self.newsapi_key, self.pexels_api_key]):
            raise ValueError("API Keys missing in .env file!")

        # 2. Initialize Groq with specific settings to bypass the bug
        # We pass base_url explicitly to help the client stay on track
        self.groq_client = Groq()
        
        # 3. Directories
        self.output_dir = 'generated_videos'
        self.temp_image_dir = 'static/temp_images'
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_image_dir, exist_ok=True)

    def get_trending_news(self, limit=10):
        url = 'https://newsapi.org/v2/everything'
        params = {
            'apiKey': self.newsapi_key,
            'q': 'India OR Indian OR Modi OR ISRO OR Cricket OR Bollywood',
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': limit
        }
        response = requests.get(url, params=params)
        response.raise_for_status()

        articles = response.json().get('articles', [])

        return [{
        'title': a['title'],
        'description': a['description'],
        'source': a.get('source', {}).get('name', 'News'),
        'publishedAt': a.get('publishedAt', '')
        } for a in articles if a.get('title') and a.get('description')]

    def generate_script(self, topic):
        prompt = f"Create a 4-scene video script JSON for: {topic['title']}. Format: {{\"title\": \"\", \"scenes\": [{{\"keywords\": \"\", \"narration\": \"\"}}]}}"
        response = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)

    def search_pexels_image(self, query):
        url = 'https://api.pexels.com/v1/search'
        headers = {'Authorization': self.pexels_api_key}
        params = {'query': query, 'per_page': 1}
        res = requests.get(url, headers=headers, params=params)
        photos = res.json().get('photos', [])
        return photos[0]['src']['large'] if photos else None

    def create_text_image(self, text):
        width, height = 1920, 1080
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, height-250, width, height], fill=(0, 0, 0, 160))
        try:
            font = ImageFont.truetype("arial.ttf", 50)
        except:
            font = ImageFont.load_default()
        lines = textwrap.wrap(text, width=50)
        y_text = height - 180
        for line in lines:
            draw.text((width//2, y_text), line, font=font, fill="white", anchor="mm")
            y_text += 60
        path = os.path.join(self.temp_image_dir, f"txt_{datetime.now().timestamp()}.png")
        img.save(path)
        return path

    def generate_video(self, topic):
        script = self.generate_script(topic)
        clips = []
        for idx, scene in enumerate(script['scenes']):
            img_url = self.search_pexels_image(scene['keywords'])
            if img_url:
                img_data = requests.get(img_url).content
                img_path = os.path.join(self.temp_image_dir, f"img_{idx}.jpg")
                with open(img_path, 'wb') as f: f.write(img_data)
                txt_path = self.create_text_image(scene['narration'])
                img_clip = ImageClip(img_path).set_duration(7).resize(width=1920)

                txt_clip = ImageClip(txt_path).set_duration(7)

                clips.append(CompositeVideoClip([img_clip, txt_clip]))

        
        final_video = concatenate_videoclips(clips, method="compose")
        filename = f"vid_{datetime.now().strftime('%H%M%S')}.mp4"
        dest = os.path.join(self.output_dir, filename)
        final_video.write_videofile(dest, fps=24, codec="libx264", audio=False, preset="ultrafast")
        return filename, {"title": script['title'], "scenes": len(clips)}