import React from 'react';
import { ATTACK_COLORS } from '../utils/constants';

/**
 * NotificationCenter Component
 * Displays real-time attack notifications with animations
 */
const NotificationCenter = ({ notifications, onClear, onClearAll }) => {
  if (notifications.length === 0) return null;

  return (
    <div className="notification-center">
      <div className="notification-header">
        <h3>🔔 Recent Alerts ({notifications.length})</h3>
        {notifications.length > 0 && (
          <button onClick={onClearAll} className="btn-clear-all">
            Clear All
          </button>
        )}
      </div>
      
      <div className="notification-list">
        {notifications.map((notification) => (
          <div
            key={notification.id}
            className="notification-item animate-slide-in"
            style={{
              borderLeftColor: ATTACK_COLORS[notification.attackType] || '#ff006e',
            }}
          >
            <div className="notification-content">
              <div className="notification-title">{notification.title}</div>
              <div className="notification-message">{notification.message}</div>
              <div className="notification-meta">
                <span className="notification-confidence">
                  Confidence: {(notification.confidence * 100).toFixed(1)}%
                </span>
                <span className="notification-time">
                  {notification.timestamp.toLocaleTimeString()}
                </span>
              </div>
            </div>
            <button
              onClick={() => onClear(notification.id)}
              className="notification-close"
              aria-label="Close notification"
            >
              ×
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default NotificationCenter;

