import React from 'react';
import { ATTACK_COLORS } from '../utils/constants';

const Statistics = ({ stats, attackCounts, totalAttacks }) => {
  const formatNumber = (num) => {
    if (!num) return '0';
    return num.toLocaleString();
  };

  const formatBytes = (bytes) => {
    if (!bytes) return '0 B';
    const units = ['B', 'KB', 'MB', 'GB'];
    let size = bytes;
    let unitIndex = 0;
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }
    return `${size.toFixed(2)} ${units[unitIndex]}`;
  };

  return (
    <div className="statistics card">
      <h2>📊 Statistics</h2>
      
      <div className="stats-grid">
        <div className="stat-item primary">
          <div className="stat-value">{formatNumber(stats?.detection?.total_flows || 0)}</div>
          <div className="stat-label">Total Flows</div>
        </div>
        
        <div className={`stat-item ${totalAttacks > 0 ? 'danger' : 'success'}`}>
          <div className="stat-value">{formatNumber(totalAttacks)}</div>
          <div className="stat-label">Attacks Detected</div>
        </div>
        
        <div className="stat-item success">
          <div className="stat-value">{formatNumber(stats?.detection?.benign_count || 0)}</div>
          <div className="stat-label">Benign Flows</div>
        </div>
        
        <div className="stat-item info">
          <div className="stat-value">
            {stats?.detection?.detection_rate 
              ? (stats.detection.detection_rate * 100).toFixed(1) + '%'
              : '0%'}
          </div>
          <div className="stat-label">Detection Rate</div>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-item">
          <div className="stat-value">{formatNumber(stats?.packets_captured || 0)}</div>
          <div className="stat-label">📦 Packets Captured</div>
        </div>
        
        <div className="stat-item">
          <div className="stat-value">{formatBytes(stats?.bytes_captured || 0)}</div>
          <div className="stat-label">💾 Data Processed</div>
        </div>
        
        <div className="stat-item">
          <div className="stat-value">{stats?.capture_duration ? Math.floor(stats.capture_duration) + 's' : '0s'}</div>
          <div className="stat-label">⏱️ Runtime</div>
        </div>
        
        <div className="stat-item">
          <div className="stat-value">
            {stats?.packets_per_second ? stats.packets_per_second.toFixed(0) + '/s' : '0/s'}
          </div>
          <div className="stat-label">📈 Packet Rate</div>
        </div>
      </div>

      {Object.keys(attackCounts).length > 0 && (
        <div className="attack-distribution">
          <h3>Attack Distribution</h3>
          <div className="distribution-list">
            {Object.entries(attackCounts)
              .sort((a, b) => b[1] - a[1])
              .map(([attackType, count]) => (
                <div key={attackType} className="distribution-item">
                  <div
                    className="distribution-bar"
                    style={{
                      width: `${(count / totalAttacks) * 100}%`,
                      backgroundColor: ATTACK_COLORS[attackType] || '#999',
                    }}
                  />
                  <div className="distribution-label">
                    <span>{attackType}</span>
                    <span>{count}</span>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Statistics;
