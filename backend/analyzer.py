import cv2
import numpy as np


class VideoAnalyzer:
    def __init__(self, threshold=30.0):
        self.threshold = threshold

    def compare_histograms(self, frame1, frame2):
        hist1 = cv2.calcHist([frame1], [0], None, [256], [0, 256])
        hist2 = cv2.calcHist([frame2], [0], None, [256], [0, 256])
        return cv2.compareHist(hist1, hist2, cv2.HISTCMP_CHISQR)

    def detect_scenes(self, video_path):

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Could not open video file")

        fps = cap.get(cv2.CAP_PROP_FPS)

        prev_frame = None
        frame_count = 0
        scene_changes = []
        frame_skip = 1

        while True:
            for _ in range(frame_skip):
                ret, frame = cap.read()  # Skip frames
                if not ret:
                    break
            # ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # MSE approach not consistent
            if prev_frame is not None:
                hist_diif = self.compare_histograms(prev_frame, gray)
                diff = cv2.absdiff(prev_frame, gray)
                mse = np.mean(diff ** 2)  # how different the frames are.

                if hist_diif > self.threshold:
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
