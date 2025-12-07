import React, { useState, useEffect } from 'react';
import { vmAPI } from '../services/api';
import { DEFAULT_VM_IP, DEFAULT_VM_NAME } from '../utils/constants';

const VMStatus = ({ vmStatus }) => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchStatus();
  }, []);

  useEffect(() => {
    if (vmStatus) {
      setStatus({
        exists: true,
        vm_info: {
          name: vmStatus.name,
          state: vmStatus.state,
          ipv4: vmStatus.ipv4,
        },
      });
    }
  }, [vmStatus]);

  const fetchStatus = async () => {
    try {
      const response = await vmAPI.getStatus();
      setStatus(response.data);
    } catch (error) {
      console.error('Error fetching VM status:', error);
    }
  };

  const handleCreateVM = async () => {
    setLoading(true);
    try {
      await vmAPI.create({
        name: DEFAULT_VM_NAME,
        cpus: 2,
        memory: '2G',
        disk: '10G',
        install_services: true,
      });
      await fetchStatus();
      alert('VM created successfully');
    } catch (error) {
      console.error('Error creating VM:', error);
      alert('Failed to create VM: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleStartVM = async () => {
    setLoading(true);
    try {
      await vmAPI.start();
      await fetchStatus();
    } catch (error) {
      console.error('Error starting VM:', error);
      alert('Failed to start VM: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleStopVM = async () => {
    setLoading(true);
    try {
      await vmAPI.stop();
      await fetchStatus();
    } catch (error) {
      console.error('Error stopping VM:', error);
      alert('Failed to stop VM: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="vm-status card">
      <h2>VM Status</h2>
      {status && status.exists ? (
        <div className="vm-info">
          <div className="info-row">
            <span className="label">Name:</span>
            <span className="value">{status.vm_info?.name || 'N/A'}</span>
          </div>
          <div className="info-row">
            <span className="label">State:</span>
            <span className={`value state-${status.vm_info?.state}`}>
              {status.vm_info?.state || 'Unknown'}
            </span>
          </div>
          <div className="info-row">
            <span className="label">IP:</span>
            <span className="value">{status.vm_info?.ipv4 || 'N/A'}</span>
          </div>
          <div className="vm-controls">
            {status.vm_info?.state === 'running' ? (
              <button onClick={handleStopVM} disabled={loading}>
                Stop VM
              </button>
            ) : (
              <button onClick={handleStartVM} disabled={loading}>
                Start VM
              </button>
            )}
          </div>
        </div>
      ) : (
        <div className="vm-not-found">
          <p>Using existing VM</p>
          <div className="info-row">
            <span className="label">Name:</span>
            <span className="value">{DEFAULT_VM_NAME}</span>
          </div>
          <div className="info-row">
            <span className="label">IP:</span>
            <span className="value">{DEFAULT_VM_IP}</span>
          </div>
          <p className="info-text">VM exists but not managed by this system</p>
        </div>
      )}
    </div>
  );
};

export default VMStatus;

