/**
 * Dashboard Component - Main dashboard integrating all components
 */
import React, { useState, useEffect } from 'react';
import Statistics from './Statistics';
import AttackAlerts from './AttackAlerts';
import AttackChart from './AttackChart';
import TimelineChart from './TimelineChart';
import FlowTable from './FlowTable';
import Controls from './Controls';
import { monitoringAPI, attacksAPI, statsAPI } from '../services/api';
import websocketService from '../services/websocket';
import { WS_URL } from '../utils/constants';

const Dashboard = () => {
  const [stats, setStats] = useState({
    total_flows: 0,
    benign_flows: 0,
    attack_flows: 0,
    attacks_by_type: {},
    detection_rate: 0,
  });
  
  const [recentAttacks, setRecentAttacks] = useState([]);
  const [allFlows, setAllFlows] = useState([]);
  const [timelineData, setTimelineData] = useState([]);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Connect to WebSocket
    websocketService.connect(WS_URL);

    // Set up event listeners
    websocketService.on('connect', () => {
      console.log('Connected to WebSocket');
      setIsConnected(true);
    });

    websocketService.on('disconnect', () => {
      console.log('Disconnected from WebSocket');
      setIsConnected(false);
    });

    websocketService.on('attack', handleAttackDetection);
    websocketService.on('benign', handleBenignFlow);

    // Fetch initial stats
    fetchStats();

    // Poll stats every 5 seconds
    const statsInterval = setInterval(fetchStats, 5000);

    return () => {
      clearInterval(statsInterval);
      websocketService.disconnect();
    };
  }, []);

  const handleAttackDetection = (attack) => {
    console.log('Attack detected:', attack);
    
    // Update recent attacks
    setRecentAttacks(prev => [attack, ...prev]);
    
    // Update all flows
    setAllFlows(prev => [attack, ...prev]);
    
    // Update stats
    setStats(prev => {
      const newAttackFlows = prev.attack_flows + 1;
      const newTotalFlows = prev.total_flows + 1;
      return {
        ...prev,
        total_flows: newTotalFlows,
        attack_flows: newAttackFlows,
        attacks_by_type: {
          ...prev.attacks_by_type,
          [attack.type]: (prev.attacks_by_type[attack.type] || 0) + 1,
        },
        detection_rate: (newAttackFlows / newTotalFlows) * 100,
      };
    });
    
    // Update timeline
    updateTimeline(attack.type, true);
  };

  const handleBenignFlow = (flow) => {
    // Update all flows
    setAllFlows(prev => [flow, ...prev]);
    
    // Update stats
    setStats(prev => {
      const newBenignFlows = prev.benign_flows + 1;
      const newTotalFlows = prev.total_flows + 1;
      const newDetectionRate = prev.attack_flows > 0 
        ? (prev.attack_flows / newTotalFlows) * 100 
        : 0;
      return {
        ...prev,
        total_flows: newTotalFlows,
        benign_flows: newBenignFlows,
        detection_rate: newDetectionRate,
      };
    });
    
    // Update timeline
    updateTimeline('Benign', false);
  };

  const updateTimeline = (type, isAttack) => {
    const now = new Date();
    const timeStr = now.toLocaleTimeString();
    
    setTimelineData(prev => {
      const newData = [...prev];
      const lastEntry = newData[newData.length - 1];
      
      // If last entry is recent (within 1 second), update it
      if (lastEntry && lastEntry.time === timeStr) {
        // Create a new object instead of mutating
        newData[newData.length - 1] = {
          ...lastEntry,
          attacks: lastEntry.attacks + (isAttack ? 1 : 0),
          benign: lastEntry.benign + (isAttack ? 0 : 1),
        };
      } else {
        // Create new entry
        newData.push({
          time: timeStr,
          attacks: isAttack ? 1 : 0,
          benign: isAttack ? 0 : 1,
        });
      }
      
      // Keep only last 20 entries
      if (newData.length > 20) {
        newData.shift();
      }
      
      return newData;
    });
  };

  const fetchStats = async () => {
    try {
      const response = await statsAPI.getSummary();
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleStartMonitoring = async (interface_, targetIp) => {
    try {
      await monitoringAPI.start(interface_, targetIp);
      setIsMonitoring(true);
      console.log('Monitoring started');
    } catch (error) {
      console.error('Error starting monitoring:', error);
      alert('Failed to start monitoring: ' + error.message);
    }
  };

  const handleStopMonitoring = async () => {
    try {
      console.log('🛑 Stopping monitoring...');
      await monitoringAPI.stop();
      setIsMonitoring(false);
      console.log('✅ Monitoring stopped successfully');
      // Refresh stats after stopping
      await fetchStats();
    } catch (error) {
      console.error('❌ Error stopping monitoring:', error);
      alert('Failed to stop monitoring: ' + (error.response?.data?.detail || error.message));
      // Still set monitoring to false if it was stopped
      setIsMonitoring(false);
    }
  };

  const handleLaunchAttack = async (attackType, duration, targetIp) => {
    try {
      await attacksAPI.launch(attackType, duration, targetIp);
      console.log(`Launched attack: ${attackType}`);
      alert(`Attack "${attackType}" launched successfully!`);
    } catch (error) {
      console.error('Error launching attack:', error);
      alert('Failed to launch attack: ' + error.message);
    }
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>IDS Real-Time Monitoring Dashboard</h1>
        <div className="status-indicator">
          <span className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`}></span>
          <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
          {isMonitoring && <span className="monitoring-badge">Monitoring Active</span>}
        </div>
      </header>

      <Controls
        onStartMonitoring={handleStartMonitoring}
        onStopMonitoring={handleStopMonitoring}
        onLaunchAttack={handleLaunchAttack}
        isMonitoring={isMonitoring}
      />

      <Statistics stats={stats} />

      <div className="charts-grid">
        <AttackChart attacksByType={stats.attacks_by_type} />
        <TimelineChart timelineData={timelineData} />
      </div>

      <AttackAlerts recentAttacks={recentAttacks} />

      <FlowTable flows={allFlows} />
    </div>
  );
};

export default Dashboard;

