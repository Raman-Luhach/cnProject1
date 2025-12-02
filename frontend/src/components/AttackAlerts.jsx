/**
 * Attack Alerts Component - Display real-time attack notifications
 */
import React from 'react';

const AttackAlerts = ({ recentAttacks }) => {
  return (
    <div className="attack-alerts">
      <h2>Recent Attack Detections</h2>
      <div className="attacks-container">
        {recentAttacks.length === 0 ? (
          <p className="no-attacks">No attacks detected yet</p>
        ) : (
          recentAttacks.slice(0, 20).map((attack, index) => (
            <div key={index} className="attack-card">
              <div className="attack-header">
                <span className="attack-type">{attack.type}</span>
                <span className="attack-confidence">
                  {(attack.confidence * 100).toFixed(1)}%
                </span>
              </div>
              <div className="attack-details">
                <span>{attack.source_ip}:{attack.source_port} → {attack.dest_ip}:{attack.dest_port}</span>
                <span className="attack-protocol">{attack.protocol}</span>
              </div>
              <div className="attack-stats">
                <span>{attack.packets} packets</span>
                <span>{attack.bytes} bytes</span>
                <span>{new Date(attack.timestamp * 1000).toLocaleTimeString()}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default AttackAlerts;

