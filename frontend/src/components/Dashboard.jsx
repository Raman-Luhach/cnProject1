import React, { useState, useEffect } from 'react';
import VMStatus from './VMStatus';
import AttackControls from './AttackControls';
import RealAttackControls from './RealAttackControls';
import DetectionAlerts from './DetectionAlerts';
import Statistics from './Statistics';
import DetectionChart from './DetectionChart';
import FlowTable from './FlowTable';
import { useWebSocket } from '../hooks/useWebSocket';
import { useDetections } from '../hooks/useDetections';
import { monitoringAPI, statsAPI } from '../services/api';
import { DEFAULT_VM_IP } from '../utils/constants';

const Dashboard = () => {
  const {
    isConnected,
    detections,
    vmStatus,
    monitoringStatus,
  } = useWebSocket();

  const { attackCounts, timelineData, totalAttacks } = useDetections(detections);
  const [stats, setStats] = useState(null);
  const [isMonitoring, setIsMonitoring] = useState(false);

  useEffect(() => {
    setIsMonitoring(monitoringStatus);
  }, [monitoringStatus]);

  useEffect(() => {
    // Fetch stats periodically
    const interval = setInterval(async () => {
      try {
        const response = await statsAPI.getSummary();
        setStats(response.data);
      } catch (error) {
        console.error('Error fetching stats:', error);
      }
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const handleStartMonitoring = async () => {
    try {
      // Use default VM IP if vmStatus doesn't have one
      const vmIp = vmStatus?.ipv4 || DEFAULT_VM_IP;
      await monitoringAPI.start(vmIp);
      setIsMonitoring(true);
    } catch (error) {
      console.error('Error starting monitoring:', error);
      alert('Failed to start monitoring: ' + error.message);
    }
  };

  const handleStopMonitoring = async () => {
    try {
      await monitoringAPI.stop();
      setIsMonitoring(false);
    } catch (error) {
      console.error('Error stopping monitoring:', error);
      alert('Failed to stop monitoring: ' + error.message);
    }
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>🛡️ IDS Monitoring System</h1>
        <div className="header-status">
          <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? '● Connected' : '○ Disconnected'}
          </span>
          <span className={`status-indicator ${isMonitoring ? 'monitoring' : 'idle'}`}>
            {isMonitoring ? '📡 Monitoring' : '⏸️ Idle'}
          </span>
          {stats && stats.total_detections !== undefined && stats.total_detections > 0 && (
            <span className="status-indicator alert">
              ⚠️ {stats.total_detections} Threats
            </span>
          )}
        </div>
      </header>

      <div className="dashboard-controls">
        <button
          onClick={isMonitoring ? handleStopMonitoring : handleStartMonitoring}
          className={isMonitoring ? 'btn-stop' : 'btn-start'}
        >
          {isMonitoring ? 'Stop Monitoring' : 'Start Monitoring'}
        </button>
        {stats && stats.packets_captured !== undefined && (
          <div className="stats-quick">
            <span>📦 {stats.packets_captured.toLocaleString()} packets captured</span>
            {detections && detections.length > 0 && (
              <span>🎯 {detections.length} recent detections</span>
            )}
          </div>
        )}
      </div>

      <div className="dashboard-grid">
        <div className="grid-item vm-section">
          <VMStatus vmStatus={vmStatus} />
        </div>

        <div className="grid-item attack-section">
          <RealAttackControls />
        </div>

        <div className="grid-item attack-section-sim">
          <AttackControls vmStatus={vmStatus || { ipv4: DEFAULT_VM_IP }} />
        </div>

        <div className="grid-item stats-section">
          <Statistics 
            stats={stats} 
            attackCounts={attackCounts}
            totalAttacks={totalAttacks}
          />
        </div>

        <div className="grid-item chart-section">
          <DetectionChart timelineData={timelineData} />
        </div>

        <div className="grid-item alerts-section">
          <DetectionAlerts detections={detections} />
        </div>

        <div className="grid-item table-section">
          <FlowTable detections={detections} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
