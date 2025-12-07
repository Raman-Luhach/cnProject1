import React, { useState, useEffect } from 'react';
import { attacksAPI } from '../services/api';
import { DEFAULT_VM_IP } from '../utils/constants';

const AttackControls = ({ vmStatus }) => {
  const [availableAttacks, setAvailableAttacks] = useState([]);
  const [selectedAttack, setSelectedAttack] = useState('');
  const [activeAttacks, setActiveAttacks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [attacksLoaded, setAttacksLoaded] = useState(false);

  useEffect(() => {
    fetchAvailableAttacks();
    const interval = setInterval(fetchActiveAttacks, 3000);
    return () => clearInterval(interval);
  }, []);

  const fetchAvailableAttacks = async () => {
    try {
      const response = await attacksAPI.list();
      const attacks = response.data || [];
      setAvailableAttacks(attacks);
      setAttacksLoaded(true);
      if (attacks.length > 0) {
        // Always set first attack as default if none selected
        if (!selectedAttack || selectedAttack === '') {
          setSelectedAttack(attacks[0].name);
        }
      }
    } catch (error) {
      console.error('Error fetching attacks:', error);
      setAttacksLoaded(true);
      // Set default attacks if API fails (using exact enum values)
      const defaultAttacks = [
        { name: 'DoS attacks-Slowloris', display_name: 'DoS - Slowloris' },
        { name: 'DoS attacks-Hulk', display_name: 'DoS - Hulk' },
        { name: 'DDoS attacks-LOIC-HTTP', display_name: 'DDoS - LOIC HTTP' },
        { name: 'DDOS attack-HOIC', display_name: 'DDoS - HOIC' },
        { name: 'SSH-Bruteforce', display_name: 'SSH Brute Force' },
        { name: 'SQL Injection', display_name: 'SQL Injection' },
      ];
      setAvailableAttacks(defaultAttacks);
      if (!selectedAttack || selectedAttack === '') {
        setSelectedAttack(defaultAttacks[0].name);
      }
    }
  };

  const fetchActiveAttacks = async () => {
    try {
      const response = await attacksAPI.getActive();
      setActiveAttacks(response.data);
    } catch (error) {
      console.error('Error fetching active attacks:', error);
    }
  };

  const handleStartAttack = async () => {
    // Validate attack type is selected
    if (!selectedAttack || selectedAttack === '') {
      alert('Please select an attack type first');
      return;
    }

    // Use VM IP from status, or fallback to default
    const targetIp = vmStatus?.ipv4 || DEFAULT_VM_IP;
    
    if (!targetIp) {
      alert('VM IP not available');
      return;
    }

    setLoading(true);
    try {
      await attacksAPI.start({
        attack_type: selectedAttack,
        target_ip: targetIp,
        duration: 300,
        intensity: 'medium',
      });
      await fetchActiveAttacks();
      alert(`Attack "${selectedAttack}" started successfully!`);
    } catch (error) {
      console.error('Error starting attack:', error);
      const errorMsg = error.response?.data?.detail || error.message || 'Unknown error';
      alert('Failed to start attack: ' + (typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg)));
    } finally {
      setLoading(false);
    }
  };

  const handleStopAttack = async (attackId) => {
    try {
      await attacksAPI.stop(attackId);
      await fetchActiveAttacks();
    } catch (error) {
      console.error('Error stopping attack:', error);
      alert('Failed to stop attack: ' + error.message);
    }
  };

  const handleStopAll = async () => {
    try {
      await attacksAPI.stopAll();
      await fetchActiveAttacks();
    } catch (error) {
      console.error('Error stopping attacks:', error);
      alert('Failed to stop attacks: ' + error.message);
    }
  };

  return (
    <div className="attack-controls card">
      <h2>Attack Controls</h2>
      
      <div className="attack-launcher">
        <select
          value={selectedAttack}
          onChange={(e) => setSelectedAttack(e.target.value)}
          disabled={loading}
          className="attack-select"
        >
          {availableAttacks.length === 0 ? (
            <option value="">Loading attacks...</option>
          ) : (
            availableAttacks.map((attack) => (
              <option key={attack.name} value={attack.name}>
                {attack.display_name || attack.name}
              </option>
            ))
          )}
        </select>
        
        <button 
          onClick={handleStartAttack} 
          disabled={loading || !selectedAttack || selectedAttack === '' || !attacksLoaded}
          className="btn-launch"
          title={!attacksLoaded ? 'Loading attacks...' : !selectedAttack ? 'Please select an attack type' : 'Launch attack'}
        >
          {loading ? 'Launching...' : !attacksLoaded ? 'Loading...' : '🚀 Launch Attack'}
        </button>
      </div>

      <div className="active-attacks">
        <h3>Active Attacks ({activeAttacks.length})</h3>
        {activeAttacks.length > 0 ? (
          <>
            <ul>
              {activeAttacks.map((attack) => (
                <li key={attack.attack_id}>
                  <span>{attack.attack_type}</span>
                  <span className={`status-${attack.status}`}>{attack.status}</span>
                  <button onClick={() => handleStopAttack(attack.attack_id)}>
                    Stop
                  </button>
                </li>
              ))}
            </ul>
            {activeAttacks.length > 1 && (
              <button onClick={handleStopAll} className="btn-stop-all">
                Stop All
              </button>
            )}
          </>
        ) : (
          <p>No active attacks</p>
        )}
      </div>
    </div>
  );
};

export default AttackControls;

