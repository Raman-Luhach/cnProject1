import React from 'react';
import { ATTACK_COLORS } from '../utils/constants';

const DetectionAlerts = ({ detections }) => {
  const recentDetections = detections.slice(0, 10);

  return (
    <div className="detection-alerts card">
      <h2>Recent Detections</h2>
      <div className="alerts-container">
        {recentDetections.length > 0 ? (
          recentDetections.map((detection, index) => (
            <div
              key={index}
              className="alert-item"
              style={{ borderLeftColor: ATTACK_COLORS[detection.prediction] || '#999' }}
            >
              <div className="alert-header">
                <span className="alert-type">{detection.prediction}</span>
                <span className="alert-confidence">
                  {(detection.confidence * 100).toFixed(1)}%
                </span>
              </div>
              <div className="alert-details">
                <span>{detection.src_ip}:{detection.src_port}</span>
                <span>→</span>
                <span>{detection.dst_ip}:{detection.dst_port}</span>
              </div>
              <div className="alert-meta">
                <span>{detection.protocol}</span>
                <span>{detection.packet_count} packets</span>
                <span>{new Date(detection.timestamp).toLocaleTimeString()}</span>
              </div>
            </div>
          ))
        ) : (
          <div className="no-detections">No detections yet</div>
        )}
      </div>
    </div>
  );
};

export default DetectionAlerts;

