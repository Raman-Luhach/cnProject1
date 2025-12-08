import React, { useState, useEffect } from 'react';
import VMStatus from './VMStatus';
import AttackControls from './AttackControls';
import RealAttackControls from './RealAttackControls';
import DetectionAlerts from './DetectionAlerts';
import Statistics from './Statistics';
import DetectionChart from './DetectionChart';
import FlowTable from './FlowTable';
import NotificationCenter from './NotificationCenter';
import { useWebSocket } from '../hooks/useWebSocket';
import { useDetections } from '../hooks/useDetections';
import { useNotifications } from '../hooks/useNotifications';
import { monitoringAPI, statsAPI } from '../services/api';
import { DEFAULT_VM_IP } from '../utils/constants';

const Dashboard = () => {
  const {
    isConnected,
    detections,
    vmStatus,
    monitoringStatus,
  } = useWebSocket();

  const [stats, setStats] = useState(null);
  const { attackCounts, timelineData, totalAttacks, recentDetections } = useDetections(detections, stats);
  const { notifications, clearNotification, clearAll } = useNotifications(detections);
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
        <div className="header-left">
          <h1>🛡️ Intrusion Detection System</h1>
          <p className="header-subtitle">Real-time Network Security Monitoring</p>
        </div>
        <div className="header-status">
          <div className={`status-badge ${isConnected ? 'connected' : 'disconnected'}`}>
            <span className="status-dot"></span>
            <span className="status-text">{isConnected ? 'Connected' : 'Disconnected'}</span>
          </div>
          <div className={`status-badge ${isMonitoring ? 'monitoring' : 'idle'}`}>
            <span className="status-dot"></span>
            <span className="status-text">{isMonitoring ? 'Monitoring Active' : 'Monitoring Idle'}</span>
          </div>
          {stats && stats.detection && stats.detection.attack_count > 0 && (
            <div className="status-badge alert">
              <span className="status-dot"></span>
              <span className="status-text">{stats.detection.attack_count} Threats</span>
            </div>
          )}
        </div>
      </header>

      <div className="dashboard-controls">
        <div className="controls-left">
          <button
            onClick={isMonitoring ? handleStopMonitoring : handleStartMonitoring}
            className={`btn-primary ${isMonitoring ? 'btn-danger' : 'btn-success'}`}
          >
            {isMonitoring ? '⏹️ Stop Monitoring' : '▶️ Start Monitoring'}
          </button>
          {stats && stats.packets_captured !== undefined && isMonitoring && (
            <div className="quick-stats">
              <div className="quick-stat-item">
                <span className="quick-stat-icon">📦</span>
                <span className="quick-stat-value">{stats.packets_captured.toLocaleString()}</span>
                <span className="quick-stat-label">Packets</span>
              </div>
              <div className="quick-stat-item">
                <span className="quick-stat-icon">🔍</span>
                <span className="quick-stat-value">{recentDetections.length}</span>
                <span className="quick-stat-label">Recent (5min)</span>
              </div>
              {stats.detection && stats.detection.attack_count > 0 && (
                <div className="quick-stat-item danger">
                  <span className="quick-stat-icon">🚨</span>
                  <span className="quick-stat-value">{stats.detection.attack_count}</span>
                  <span className="quick-stat-label">Attacks</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {notifications.length > 0 && (
        <NotificationCenter
          notifications={notifications}
          onClear={clearNotification}
          onClearAll={clearAll}
        />
      )}

      <div className="dashboard-grid">
        <div className="grid-row">
          <div className="grid-item vm-section">
            <VMStatus vmStatus={vmStatus} />
          </div>

          <div className="grid-item attack-section">
            <RealAttackControls />
          </div>
        </div>

        <div className="grid-row">
          <div className="grid-item attack-section-sim">
            <AttackControls vmStatus={vmStatus || { ipv4: DEFAULT_VM_IP }} />
          </div>
        </div>

        <div className="grid-row">
          <div className="grid-item stats-section full-width">
            <Statistics 
              stats={stats} 
              attackCounts={attackCounts}
              totalAttacks={totalAttacks}
            />
          </div>
        </div>

        <div className="grid-row">
          <div className="grid-item chart-section">
            <DetectionChart timelineData={timelineData} />
          </div>
        </div>

        <div className="grid-row">
          <div className="grid-item alerts-section">
            <DetectionAlerts detections={recentDetections} />
          </div>
        </div>

        <div className="grid-row">
          <div className="grid-item table-section full-width">
            <FlowTable detections={recentDetections} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
