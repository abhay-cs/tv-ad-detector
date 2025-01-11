import React, { useState } from 'react';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const VideoUploader = () => {
    const [videoFile, setVideoFile] = useState(null);
    const [analysisResult, setAnalysisResult] = useState(null);
    const [error, setError] = useState(null);
    const [videoPreviewUrl, setVideoPreviewUrl] = useState(null);
    const [loading, setLoading] = useState(false); // Loading state

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file) {
            setVideoFile(file);
            setVideoPreviewUrl(URL.createObjectURL(file)); // Create a preview URL
        }
    };

    const handleUpload = async () => {
        if (!videoFile) {
            alert("Please select a video file first.");
            return;
        }

        const formData = new FormData();
        formData.append('video', videoFile);

        setLoading(true); // Set loading state to true

        try {
            const response = await fetch('http://localhost:5500/api/analyze', {
                method: 'POST',
                body: formData,
            });
            const data = await response.json();

            if (data.status === 'success') {
                setAnalysisResult(data);
            } else {
                setError(data.message || 'An error occurred while analyzing the video.');
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false); // Set loading state to false
        }
    };

    const generateChartData = () => {
        if (!analysisResult || !analysisResult.scene_changes) return null;

        const timestamps = analysisResult.scene_changes.map(scene => scene.timestamp.toFixed(2));
        const intensities = analysisResult.scene_changes.map(scene => scene.change_intensity);

        return {
            labels: timestamps,
            datasets: [
                {
                    label: 'Scene Change Intensity',
                    data: intensities,
                    borderColor: 'rgb(146, 127, 187)',
                    backgroundColor: 'rgba(219, 27, 225, 0.2)',
                    borderWidth: 2,
                    tension: 0.4,
                },
            ],
        };
    };

    const chartOptions = {
        responsive: true,
        plugins: {
            legend: { display: true, position: 'top' },
            tooltip: { enabled: true },
        },
        scales: {
            x: { title: { display: true, text: 'Timestamp (s)' } },
            y: { title: { display: true, text: 'Change Intensity' } },
        },
    };

    return (
        <div>
            <h1>Video Analyzer</h1>
            <input type="file" accept="video/*" onChange={handleFileChange} />
            <button onClick={handleUpload} disabled={loading}>
                {loading ? 'Uploading...' : 'Upload and Analyze'}
            </button>

            {loading && (
                <div style={{ margin: '20px 0', textAlign: 'center' }}>
                    <div className="spinner" style={{ marginBottom: '10px' }}></div>
                    <p>Processing your video... Please wait.</p>
                </div>
            )}

            {videoPreviewUrl && !loading && (
                <div>
                    <h2>Video Preview</h2>
                    <video
                        controls
                        width="600"
                        src={videoPreviewUrl}
                        style={{
                            maxWidth: '50%',
                            width: '800px',
                            margin: '20px 0',
                        }}
                    />
                </div>
            )}

            {error && <p style={{ color: 'red' }}>Error: {error}</p>}

            {analysisResult && (
                <div>
                    <h2>Analysis Result</h2>
                    <p>Total Scenes: {analysisResult.total_scenes}</p>

                    {/* Render the graph */}
                    <div style={{ width: '100%', margin: '0 auto' }}>
                        <Line data={generateChartData()} options={chartOptions} />
                    </div>
                </div>
            )}
        </div>
    );
};

export default VideoUploader;
