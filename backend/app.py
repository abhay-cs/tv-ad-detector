from flask import Flask, request, jsonify
from flask_cors import CORS
from analyzer import VideoAnalyzer
import os

app = Flask(__name__)
CORS(app)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# endpoints
@app.route('/api/analyze', methods=['POST'])
def analyze_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # Save video to upload folder
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_file.filename)
        video_file.save(video_path)

        # Analyze video
        analyzer = VideoAnalyzer()
        scene_changes = analyzer.detect_scenes(video_path)

        # Optionally delete the video file after processing
        os.unlink(video_path)

        return jsonify({
            'status': 'success',
            'message': 'Video analysis complete',
            'scene_changes': scene_changes,
            'total_scenes': len(scene_changes)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# api health check
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, port=5500)