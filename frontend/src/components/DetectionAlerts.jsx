import React from 'react';
import { ATTACK_COLORS } from '../utils/constants';

const DetectionAlerts = ({ detections }) => {
  // Show last 15 detections
  const recentDetections = detections.slice(0, 15);
  const attackDetections = recentDetections.filter(d => d.is_attack);

  return (
    <div className="detection-alerts card">
      <div className="card-header">
        <h2>🎯 Recent Detections</h2>
        <p className="card-subtitle">
          Last 5 minutes • {attackDetections.length} attacks, {recentDetections.length - attackDetections.length} benign
        </p>
      </div>
      
      <div className="alerts-container">
        {recentDetections.length > 0 ? (
          recentDetections.map((detection, index) => (
            <div
              key={detection.flow_id || index}
              className={`alert-item ${detection.is_attack ? 'attack-alert' : 'benign-alert'}`}
              style={{ 
                borderLeftColor: detection.is_attack 
                  ? (ATTACK_COLORS[detection.prediction] || '#dc3545') 
                  : '#198754'
              }}
            >
              <div className="alert-icon">
                {detection.is_attack ? '🚨' : '✅'}
              </div>
              <div className="alert-content">
                <div className="alert-header">
                  <span className={`alert-type ${detection.is_attack ? 'type-attack' : 'type-benign'}`}>
                    {detection.prediction}
                  </span>
                  <span className="alert-confidence">
                    {(detection.confidence * 100).toFixed(1)}% confidence
                  </span>
                </div>
                <div className="alert-details">
                  <span className="detail-endpoint">{detection.src_ip}:{detection.src_port}</span>
                  <span className="detail-arrow">→</span>
                  <span className="detail-endpoint">{detection.dst_ip}:{detection.dst_port}</span>
                </div>
                <div className="alert-meta">
                  <span className="meta-item">
                    <span className="meta-label">Protocol:</span> {detection.protocol}
                  </span>
                  <span className="meta-item">
                    <span className="meta-label">Packets:</span> {detection.packet_count}
                  </span>
                  <span className="meta-item">
                    <span className="meta-label">Time:</span> {new Date(detection.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="empty-state">
            <div className="empty-state-icon">📭</div>
            <div className="empty-state-text">No detections in the last 5 minutes</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DetectionAlerts;

