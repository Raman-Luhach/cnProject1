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

  // Use backend's real attack distribution if available
  const realAttackDistribution = stats?.attacks?.distribution || {};
  const realTotalAttacks = stats?.detection?.attack_count || 0;
  
  // Use real totals from backend, fallback to local counts for recent view
  const displayDistribution = Object.keys(realAttackDistribution).length > 0 
    ? realAttackDistribution 
    : attackCounts;
  const displayTotal = realTotalAttacks > 0 ? realTotalAttacks : totalAttacks;

  return (
    <div className="statistics card">
      <div className="card-header">
        <h2>📊 System Statistics</h2>
        <p className="card-subtitle">Real-time monitoring metrics and attack analysis</p>
      </div>
      
      <div className="section-divider">
        <span>Detection Metrics</span>
      </div>
      
      <div className="stats-grid">
        <div className="stat-item primary">
          <div className="stat-icon">🔄</div>
          <div className="stat-content">
            <div className="stat-value">{formatNumber(stats?.detection?.total_flows || 0)}</div>
            <div className="stat-label">Total Flows Analyzed</div>
          </div>
        </div>
        
        <div className={`stat-item ${displayTotal > 0 ? 'danger' : 'success'}`}>
          <div className="stat-icon">{displayTotal > 0 ? '🚨' : '✅'}</div>
          <div className="stat-content">
            <div className="stat-value">{formatNumber(displayTotal)}</div>
            <div className="stat-label">Attacks Detected (All Time)</div>
          </div>
        </div>
        
        <div className="stat-item success">
          <div className="stat-icon">✨</div>
          <div className="stat-content">
            <div className="stat-value">{formatNumber(stats?.detection?.benign_count || 0)}</div>
            <div className="stat-label">Benign Flows</div>
          </div>
        </div>
        
        <div className="stat-item info">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <div className="stat-value">
              {stats?.detection?.detection_rate 
                ? (stats.detection.detection_rate * 100).toFixed(1) + '%'
                : '0%'}
            </div>
            <div className="stat-label">Attack Rate</div>
          </div>
        </div>
      </div>

      <div className="section-divider">
        <span>Network Activity</span>
      </div>

      <div className="stats-grid">
        <div className="stat-item">
          <div className="stat-icon">📦</div>
          <div className="stat-content">
            <div className="stat-value">{formatNumber(stats?.packets_captured || 0)}</div>
            <div className="stat-label">Packets Captured</div>
          </div>
        </div>
        
        <div className="stat-item">
          <div className="stat-icon">💾</div>
          <div className="stat-content">
            <div className="stat-value">{formatBytes(stats?.bytes_captured || 0)}</div>
            <div className="stat-label">Data Processed</div>
          </div>
        </div>
        
        <div className="stat-item">
          <div className="stat-icon">⏱️</div>
          <div className="stat-content">
            <div className="stat-value">{stats?.capture_duration ? Math.floor(stats.capture_duration) + 's' : '0s'}</div>
            <div className="stat-label">Monitoring Duration</div>
          </div>
        </div>
        
        <div className="stat-item">
          <div className="stat-icon">📈</div>
          <div className="stat-content">
            <div className="stat-value">
              {stats?.packets_per_second ? stats.packets_per_second.toFixed(0) + '/s' : '0/s'}
            </div>
            <div className="stat-label">Packet Rate</div>
          </div>
        </div>
      </div>

      {Object.keys(displayDistribution).length > 0 && (
        <>
          <div className="section-divider">
            <span>Attack Distribution {realTotalAttacks > 0 && '(All Time)'}</span>
          </div>
          <div className="attack-distribution">
            <div className="distribution-summary">
              <span className="distribution-total">
                Total: <strong>{formatNumber(displayTotal)}</strong> attacks detected
              </span>
              <span className="distribution-types">
                {Object.keys(displayDistribution).length} attack types
              </span>
            </div>
            <div className="distribution-list">
              {Object.entries(displayDistribution)
                .filter(([type]) => type !== 'Benign') // Exclude benign from distribution
                .sort((a, b) => b[1] - a[1])
                .map(([attackType, count]) => {
                  const percentage = ((count / displayTotal) * 100).toFixed(1);
                  return (
                    <div key={attackType} className="distribution-item">
                      <div className="distribution-label">
                        <span className="attack-type-name">{attackType}</span>
                        <span className="attack-count">
                          {formatNumber(count)} <span className="attack-percentage">({percentage}%)</span>
                        </span>
                      </div>
                      <div className="distribution-bar-container">
                        <div
                          className="distribution-bar"
                          style={{
                            width: `${percentage}%`,
                            backgroundColor: ATTACK_COLORS[attackType] || '#999',
                          }}
                        >
                          <span className="bar-percentage">{percentage}%</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Statistics;
