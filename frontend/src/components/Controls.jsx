/**
 * Controls Component - Start/stop monitoring and launch attacks
 */
import React, { useState } from 'react';
import { ATTACK_TYPES, DEFAULT_TARGET_IP, DEFAULT_INTERFACE } from '../utils/constants';

const Controls = ({ onStartMonitoring, onStopMonitoring, onLaunchAttack, isMonitoring }) => {
  const [targetIp, setTargetIp] = useState(DEFAULT_TARGET_IP);
  const [interface_, setInterface] = useState(DEFAULT_INTERFACE);
  const [selectedAttack, setSelectedAttack] = useState(ATTACK_TYPES[0]);
  const [duration, setDuration] = useState(60);

  const handleStartMonitoring = () => {
    onStartMonitoring(interface_, targetIp);
  };

  const handleLaunchAttack = () => {
    onLaunchAttack(selectedAttack, duration, targetIp);
  };

  return (
    <div className="controls">
      <div className="control-section">
        <h3>Monitoring Controls</h3>
        <div className="control-group">
          <label>Network Interface:</label>
          <input 
            type="text" 
            value={interface_} 
            onChange={(e) => setInterface(e.target.value)}
            placeholder="e.g., bridge100"
            disabled={isMonitoring}
          />
        </div>
        <div className="control-group">
          <label>Target VM IP:</label>
          <input 
            type="text" 
            value={targetIp} 
            onChange={(e) => setTargetIp(e.target.value)}
            placeholder="e.g., 192.168.64.2"
            disabled={isMonitoring}
          />
        </div>
        <div className="control-buttons">
          {!isMonitoring ? (
            <button className="btn-start" onClick={handleStartMonitoring}>
              ▶ Start Monitoring
            </button>
          ) : (
            <button 
              className="btn-stop" 
              onClick={onStopMonitoring}
              style={{ 
                animation: 'pulse 2s infinite',
                fontWeight: 'bold',
                fontSize: '16px'
              }}
            >
              ⏹ Stop Monitoring (Click to Stop)
            </button>
          )}
          {isMonitoring && (
            <div style={{ 
              marginTop: '10px', 
              color: '#4caf50', 
              fontSize: '14px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <span style={{
                width: '10px',
                height: '10px',
                borderRadius: '50%',
                background: '#4caf50',
                animation: 'pulse 2s infinite'
              }}></span>
              Monitoring Active - Capturing Packets
            </div>
          )}
        </div>
      </div>

      <div className="control-section">
        <h3>Attack Launcher</h3>
        <div className="control-group">
          <label>Attack Type:</label>
          <select 
            value={selectedAttack} 
            onChange={(e) => setSelectedAttack(e.target.value)}
          >
          {ATTACK_TYPES.map(attack => (
            <option key={attack} value={attack}>{attack}</option>
          ))}
          </select>
        </div>
        <div className="control-group">
          <label>Duration (seconds):</label>
          <input 
            type="number" 
            value={duration} 
            onChange={(e) => setDuration(parseInt(e.target.value))}
            min="10"
            max="300"
          />
        </div>
        <div className="control-buttons">
          <button 
            className="btn-attack" 
            onClick={handleLaunchAttack}
            disabled={!isMonitoring}
            title={!isMonitoring ? "Start monitoring first" : "Launch attack"}
          >
            🚀 Launch Attack
          </button>
        </div>
      </div>
    </div>
  );
};

export default Controls;

