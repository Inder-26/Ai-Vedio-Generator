from flask import Flask, render_template, jsonify, send_file, request
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
from video_generator import VideoGenerator

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'generated_videos'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/temp_images', exist_ok=True)

# Initialize video generator
video_gen = VideoGenerator()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/trending-topics', methods=['GET'])
def get_trending_topics():
    """Get trending news topics"""
    try:
        topics = video_gen.get_trending_news()
        return jsonify({
            'success': True,
            'topics': topics
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate-video', methods=['POST'])
def generate_video():
    """Generate video from selected topic"""
    try:
        data = request.json
        topic_index = data.get('topic_index', 0)
        
        # Get trending topics
        topics = video_gen.get_trending_news()
        
        if topic_index >= len(topics):
            return jsonify({
                'success': False,
                'error': 'Invalid topic index'
            }), 400
        
        selected_topic = topics[topic_index]
        
        # Generate video
        video_path, metadata = video_gen.generate_video(selected_topic)
        
        return jsonify({
            'success': True,
            'video_path': video_path,
            'metadata': metadata
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/videos', methods=['GET'])
def list_videos():
    """List all generated videos"""
    try:
        videos = []
        video_dir = app.config['UPLOAD_FOLDER']
        
        for filename in os.listdir(video_dir):
            if filename.endswith('.mp4'):
                filepath = os.path.join(video_dir, filename)
                videos.append({
                    'filename': filename,
                    'created': datetime.fromtimestamp(
                        os.path.getctime(filepath)
                    ).strftime('%Y-%m-%d %H:%M:%S'),
                    'size': f"{os.path.getsize(filepath) / (1024*1024):.2f} MB"
                })
        
        videos.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({
            'success': True,
            'videos': videos
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/videos/<filename>')
def serve_video(filename):
    """Serve generated video"""
    try:
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(video_path):
            return send_file(video_path, mimetype='video/mp4')
        else:
            return jsonify({'error': 'Video not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting AI Video Generator...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)