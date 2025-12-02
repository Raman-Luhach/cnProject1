/**
 * Statistics Component - Display flow statistics
 */
import React from 'react';

const Statistics = ({ stats }) => {
  const detectionRate = stats.total_flows > 0 
    ? ((stats.attack_flows / stats.total_flows) * 100).toFixed(1)
    : 0;

  return (
    <div className="stats-grid">
      <div className="stat-card">
        <h3>Total Flows</h3>
        <div className="stat-value">{stats.total_flows}</div>
      </div>
      
      <div className="stat-card">
        <h3>Benign Flows</h3>
        <div className="stat-value benign">{stats.benign_flows}</div>
      </div>
      
      <div className="stat-card">
        <h3>Attacks Detected</h3>
        <div className="stat-value attack">{stats.attack_flows}</div>
      </div>
      
      <div className="stat-card">
        <h3>Detection Rate</h3>
        <div className="stat-value">{detectionRate}%</div>
      </div>
    </div>
  );
};

export default Statistics;

