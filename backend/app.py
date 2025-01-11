from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import os

app = Flask(__name__)
CORS(app)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)  # Create folder if it doesn't exist
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# analyze video
class VideoAnalyzer:
    def __init__(self, threshold=30.0):
        self.threshold = threshold

    def detect_scenes(self, video_path):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Could not open video file")

        fps = cap.get(cv2.CAP_PROP_FPS)
        prev_frame = None
        frame_count = 0
        scene_changes = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if prev_frame is not None:
                # Calculate mean squared error between frames
                diff = cv2.absdiff(prev_frame, gray)
                mse = np.mean(diff ** 2)

                if mse > self.threshold:
                    timestamp = frame_count / fps
                    scene_changes.append({
                        'timestamp': timestamp,
                        'frame_number': frame_count,
                        'time_string': f"{int(timestamp // 60)}:{int(timestamp % 60):02d}",
                        'change_intensity': float(mse)
                    })

            prev_frame = gray
            frame_count += 1

        cap.release()
        return scene_changes


@app.route('/api/analyze', methods=['POST'])
def analyze_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # Save video to upload folder
        video_path = os.path.join(
            app.config['UPLOAD_FOLDER'], video_file.filename)
        video_file.save(video_path)

        # Analyze video
        analyzer = VideoAnalyzer()
        scene_changes = analyzer.detect_scenes(video_path)

        # Optionally delete the video file after processing
        # os.unlink(video_path)

        return jsonify({
            'status': 'success',
            'message': 'Video analysis complete',
            'scene_changes': scene_changes,
            'total_scenes': len(scene_changes)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    app.run(debug=True, port=5500)
