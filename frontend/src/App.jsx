import React, { useState } from 'react';
import './App.css';
import SupportChat from './components/SupportChat';

const App = () => {
  const [latestPredictions, setLatestPredictions] = useState([]);
  const [latestImage, setLatestImage] = useState(null);

  // This will be called by SupportChat whenever the API responds
  const handleBotResponse = (predictions, imageUrl) => {
    setLatestPredictions(predictions || []);
    if (imageUrl) {
      setLatestImage(imageUrl);
    }
  };

  return (
    <div className="app-main">
      <div className="glass-panel main-panel">
        <header className="header">
          <h1>Visual Product Matcher</h1>
          <p className="subtitle">CLIP-Powered Zero-Shot Image Matching</p>
        </header>

        <div className="interface-grid">
          <div className="chat-column">
            <SupportChat onResponse={handleBotResponse} />
          </div>

          <div className="stats-column">
            <h2>Classification Data</h2>
            {latestImage ? (
              <div className="stats-content">
                <img src={latestImage} alt="Analysis Target" className="preview-image" />
                <div className="predictions-list">
                  {latestPredictions.map((pred, idx) => {
                    const isStrong = (pred.match_type === 'image' && pred.score >= 0.8) || (pred.match_type === 'text' && pred.score >= 0.25);
                    return (
                      <div key={idx} className={`prediction-bar ${isStrong ? 'strong' : 'weak'}`}>
                        <div className="pred-info">
                          <span className="pred-label">{pred.label}</span>
                          <span className="pred-score">{(pred.score * 100).toFixed(1)}%</span>
                        </div>
                        <div className="progress-bg">
                          <div className="progress-fill" style={{ width: `${Math.min(pred.score * 100, 100)}%` }}></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : (
              <div className="empty-stats">
                <p>Upload an image in the chat to see real-time vector similarity scores against your inventory database.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
