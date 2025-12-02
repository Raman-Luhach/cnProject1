/**
 * API Service - Communication with FastAPI backend
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Monitoring endpoints
export const monitoringAPI = {
  start: (interface_name, target_ip) => 
    api.post('/api/monitoring/start', { interface: interface_name, target_ip }),
  
  stop: () => 
    api.post('/api/monitoring/stop'),
  
  getStatus: () => 
    api.get('/api/monitoring/status'),
};

// Attack endpoints
export const attacksAPI = {
  launch: (attack_type, duration, target_ip, intensity = 50) => 
    api.post('/api/attacks/launch', { attack_type, duration, target_ip, intensity }),
  
  stop: () => 
    api.post('/api/attacks/stop'),
  
  list: () => 
    api.get('/api/attacks/list'),
};

// Statistics endpoints
export const statsAPI = {
  getSummary: () => 
    api.get('/api/stats/summary'),
  
  getRecent: (limit = 50) => 
    api.get('/api/stats/recent', { params: { limit } }),
};

// Health check
export const healthCheck = () => 
  api.get('/health');

export default api;

