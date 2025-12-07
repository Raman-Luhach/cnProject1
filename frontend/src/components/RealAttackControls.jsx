import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL, DEFAULT_VM_IP } from '../utils/constants';

const attackTypes = [
  { id: 'hulk', name: 'HULK HTTP Flood', description: '500 threads, obfuscated requests', color: '#f44336' },
  { id: 'goldeneye', name: 'GoldenEye HTTP Flood', description: '300 threads, keep-alive', color: '#ff9800' },
  { id: 'http_flood_bash', name: 'HTTP Flood (Bash)', description: '50 threads, curl-based', color: '#ff5722' },
  { id: 'http_flood_python', name: 'HTTP Flood (Python)', description: '50 threads, urllib', color: '#e91e63' },
  { id: 'slowloris', name: 'Slowloris', description: 'Slow HTTP attack', color: '#9c27b0' },
];

const RealAttackControls = () => {
  const [selectedAttack, setSelectedAttack] = useState('hulk');
  const [duration, setDuration] = useState(30);
  const [loading, setLoading] = useState(false);
  const [activeAttacks, setActiveAttacks] = useState([]);
  const [message, setMessage] = useState('');

  useEffect(() => {
    // Poll for active attacks
    const interval = setInterval(fetchActiveAttacks, 2000);
    return () => clearInterval(interval);
  }, []);

  const fetchActiveAttacks = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/attack-launcher/active`);
      setActiveAttacks(response.data);
    } catch (error) {
      console.error('Error fetching active attacks:', error);
    }
  };

  const handleLaunch = async () => {
    setLoading(true);
    setMessage('');
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/attack-launcher/launch`, {
        attack_type: selectedAttack,
        target_ip: DEFAULT_VM_IP,
        duration: duration
      });
      
      setMessage(`✅ ${response.data.message}`);
      await fetchActiveAttacks();
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message;
      setMessage(`❌ Failed: ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

  const handleStop = async (attackId) => {
    try {
      await axios.post(`${API_BASE_URL}/api/attack-launcher/stop/${attackId}`);
      await fetchActiveAttacks();
      setMessage('✅ Attack stopped');
    } catch (error) {
      setMessage(`❌ Failed to stop: ${error.message}`);
    }
  };

  const handleStopAll = async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/attack-launcher/stop-all`);
      await fetchActiveAttacks();
      setMessage(`✅ ${response.data.message}`);
    } catch (error) {
      setMessage(`❌ Failed to stop all: ${error.message}`);
    }
  };

  const selectedAttackInfo = attackTypes.find(a => a.id === selectedAttack);

  return (
    <div className="real-attack-controls card">
      <h2>🚀 Real Attack Tools</h2>
      
      <div className="attack-config">
        <div className="form-group">
          <label htmlFor="attack-select">Attack Type:</label>
          <select
            id="attack-select"
            value={selectedAttack}
            onChange={(e) => setSelectedAttack(e.target.value)}
            disabled={loading}
            className="attack-select"
          >
            {attackTypes.map((attack) => (
              <option key={attack.id} value={attack.id}>
                {attack.name}
              </option>
            ))}
          </select>
          {selectedAttackInfo && (
            <p className="attack-description" style={{ color: selectedAttackInfo.color }}>
              {selectedAttackInfo.description}
            </p>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="duration">Duration (seconds):</label>
          <input
            id="duration"
            type="number"
            min="10"
            max="300"
            value={duration}
            onChange={(e) => setDuration(parseInt(e.target.value))}
            disabled={loading}
            className="duration-input"
          />
        </div>

        <button
          onClick={handleLaunch}
          disabled={loading}
          className="btn-launch-real"
        >
          {loading ? '🔄 Launching...' : '🚀 Launch Attack'}
        </button>
      </div>

      {message && (
        <div className={`message ${message.startsWith('✅') ? 'success' : 'error'}`}>
          {message}
        </div>
      )}

      <div className="active-real-attacks">
        <h3>Active Attacks ({activeAttacks.length})</h3>
        {activeAttacks.length > 0 ? (
          <>
            <ul>
              {activeAttacks.map((attack) => (
                <li key={attack.attack_id} className="active-attack-item">
                  <div className="attack-info">
                    <span className="attack-name">{attack.attack_type}</span>
                    <span className="attack-target">→ {attack.target_ip}</span>
                    <span className="attack-status running">● RUNNING</span>
                  </div>
                  <button onClick={() => handleStop(attack.attack_id)} className="btn-stop-small">
                    Stop
                  </button>
                </li>
              ))}
            </ul>
            {activeAttacks.length > 1 && (
              <button onClick={handleStopAll} className="btn-stop-all">
                ⏹ Stop All Attacks
              </button>
            )}
          </>
        ) : (
          <p className="no-attacks">No active attacks</p>
        )}
      </div>

      <div className="attack-info-box">
        <h4>ℹ️ About Real Attack Tools</h4>
        <p>These attacks use real Python/Bash scripts that generate authentic attack traffic.</p>
        <ul>
          <li><strong>HULK & GoldenEye:</strong> High-volume HTTP floods</li>
          <li><strong>HTTP Flood:</strong> Simpler curl/urllib-based attacks</li>
          <li><strong>Slowloris:</strong> Slow HTTP headers attack</li>
        </ul>
        <p>✅ Your IDS should detect these attacks in real-time!</p>
      </div>
    </div>
  );
};

export default RealAttackControls;

