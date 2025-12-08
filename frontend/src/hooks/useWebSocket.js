import { useEffect, useState } from 'react';
import wsService from '../services/websocket';
import { WS_EVENTS } from '../utils/constants';

export const useWebSocket = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [detections, setDetections] = useState([]);
  const [vmStatus, setVmStatus] = useState(null);
  const [attackStatus, setAttackStatus] = useState(null);
  const [stats, setStats] = useState(null);
  const [monitoringStatus, setMonitoringStatus] = useState(false);

  useEffect(() => {
    // Connect to WebSocket
    wsService.connect();

    // Connection status handler
    const handleConnection = (data) => {
      setIsConnected(data.status === 'connected');
    };

    // Detection event handler - increased buffer to 1000 for better tracking
    const handleDetection = (data) => {
      setDetections((prev) => {
        const newDetections = [data.data, ...prev].slice(0, 1000);
        return newDetections;
      });
    };

    // VM status handler
    const handleVMStatus = (data) => {
      setVmStatus(data.data);
    };

    // Attack status handler
    const handleAttackStatus = (data) => {
      setAttackStatus(data.data);
    };

    // Stats handler
    const handleStats = (data) => {
      setStats(data.data);
    };

    // Monitoring status handler
    const handleMonitoringStatus = (data) => {
      setMonitoringStatus(data.data.is_running);
    };

    // Register listeners
    wsService.on('connection', handleConnection);
    wsService.on(WS_EVENTS.DETECTION, handleDetection);
    wsService.on(WS_EVENTS.VM_STATUS, handleVMStatus);
    wsService.on(WS_EVENTS.ATTACK_STATUS, handleAttackStatus);
    wsService.on(WS_EVENTS.STATS, handleStats);
    wsService.on(WS_EVENTS.MONITORING_STATUS, handleMonitoringStatus);

    // Cleanup
    return () => {
      wsService.off('connection', handleConnection);
      wsService.off(WS_EVENTS.DETECTION, handleDetection);
      wsService.off(WS_EVENTS.VM_STATUS, handleVMStatus);
      wsService.off(WS_EVENTS.ATTACK_STATUS, handleAttackStatus);
      wsService.off(WS_EVENTS.STATS, handleStats);
      wsService.off(WS_EVENTS.MONITORING_STATUS, handleMonitoringStatus);
    };
  }, []);

  return {
    isConnected,
    detections,
    vmStatus,
    attackStatus,
    stats,
    monitoringStatus,
  };
};

