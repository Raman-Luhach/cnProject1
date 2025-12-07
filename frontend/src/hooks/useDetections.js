import { useState, useEffect } from 'react';
import { CHART_CONFIG } from '../utils/constants';

export const useDetections = (detections) => {
  const [attackCounts, setAttackCounts] = useState({});
  const [timelineData, setTimelineData] = useState([]);
  const [totalAttacks, setTotalAttacks] = useState(0);

  useEffect(() => {
    if (!detections || detections.length === 0) {
      return;
    }

    // Count attacks by type
    const counts = {};
    detections.forEach((detection) => {
      const attackType = detection.prediction;
      counts[attackType] = (counts[attackType] || 0) + 1;
    });
    setAttackCounts(counts);

    // Calculate total attacks
    const total = detections.length;
    setTotalAttacks(total);

    // Generate timeline data (last 100 detections)
    const timeline = detections
      .slice(0, CHART_CONFIG.maxDataPoints)
      .reverse()
      .map((detection, index) => ({
        index,
        timestamp: new Date(detection.timestamp).toLocaleTimeString(),
        attack: detection.prediction,
        confidence: (detection.confidence * 100).toFixed(1),
      }));
    setTimelineData(timeline);
  }, [detections]);

  return {
    attackCounts,
    timelineData,
    totalAttacks,
  };
};

