import { useState, useEffect } from 'react';
import { CHART_CONFIG } from '../utils/constants';

export const useDetections = (detections, stats) => {
  const [attackCounts, setAttackCounts] = useState({});
  const [timelineData, setTimelineData] = useState([]);
  const [totalAttacks, setTotalAttacks] = useState(0);
  const [recentDetections, setRecentDetections] = useState([]);

  useEffect(() => {
    if (!detections || detections.length === 0) {
      return;
    }

    // Filter to last 5 minutes for recent activity
    const fiveMinutesAgo = Date.now() - (5 * 60 * 1000);
    const recent = detections.filter(d => {
      const detectionTime = new Date(d.timestamp).getTime();
      return detectionTime >= fiveMinutesAgo;
    });
    setRecentDetections(recent);

    // Count attacks by type from recent detections only (for local display)
    const counts = {};
    recent.forEach((detection) => {
      if (detection.is_attack) {
        const attackType = detection.prediction;
        counts[attackType] = (counts[attackType] || 0) + 1;
      }
    });
    setAttackCounts(counts);

    // Calculate total attacks from recent
    const total = recent.filter(d => d.is_attack).length;
    setTotalAttacks(total);

    // Generate timeline data (last 100 recent detections for chart)
    const timeline = recent
      .slice(0, CHART_CONFIG.maxDataPoints)
      .reverse()
      .map((detection, index) => ({
        index,
        timestamp: new Date(detection.timestamp).toLocaleTimeString(),
        attack: detection.prediction,
        confidence: (detection.confidence * 100).toFixed(1),
        isAttack: detection.is_attack,
      }));
    setTimelineData(timeline);
  }, [detections]);

  return {
    attackCounts,
    timelineData,
    totalAttacks,
    recentDetections,
  };
};

