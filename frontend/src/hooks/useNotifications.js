import { useState, useEffect, useCallback } from 'react';

/**
 * Hook for managing attack notifications
 * Tracks new attacks and provides notification system
 */
export const useNotifications = (detections) => {
  const [notifications, setNotifications] = useState([]);
  const [lastDetectionId, setLastDetectionId] = useState(null);

  useEffect(() => {
    if (!detections || detections.length === 0) return;

    const latestDetection = detections[0];
    
    // Only show notification for attacks (not benign traffic)
    if (latestDetection.is_attack && latestDetection.flow_id !== lastDetectionId) {
      const notification = {
        id: latestDetection.flow_id,
        type: 'attack',
        title: `🚨 ${latestDetection.prediction} Detected`,
        message: `From ${latestDetection.src_ip}:${latestDetection.src_port} → ${latestDetection.dst_ip}:${latestDetection.dst_port}`,
        confidence: latestDetection.confidence,
        timestamp: new Date(latestDetection.timestamp),
        attackType: latestDetection.prediction,
      };

      setNotifications(prev => [notification, ...prev].slice(0, 50)); // Keep last 50 notifications
      setLastDetectionId(latestDetection.flow_id);

      // Auto-remove notification after 10 seconds
      setTimeout(() => {
        setNotifications(prev => prev.filter(n => n.id !== notification.id));
      }, 10000);
    }
  }, [detections, lastDetectionId]);

  const clearNotification = useCallback((id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  const clearAll = useCallback(() => {
    setNotifications([]);
  }, []);

  return {
    notifications,
    clearNotification,
    clearAll,
  };
};

