import axios from 'axios';
import { API_BASE_URL } from '../utils/constants';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Monitoring API
export const monitoringAPI = {
  start: (vmIp, networkInterface) => {
    const params = { vm_ip: vmIp };
    if (networkInterface) {
      params['interface'] = networkInterface; // Use bracket notation to avoid reserved word error
    }
    return api.post('/api/monitoring/start', null, { params });
  },
  stop: () => api.post('/api/monitoring/stop'),
  getStatus: () => api.get('/api/monitoring/status'),
};

// VM API
export const vmAPI = {
  create: (config) => api.post('/api/vm/create', config),
  start: () => api.post('/api/vm/start'),
  stop: () => api.post('/api/vm/stop'),
  delete: () => api.delete('/api/vm/delete'),
  getStatus: () => api.get('/api/vm/status'),
  getIP: () => api.get('/api/vm/ip'),
};

// Attacks API
export const attacksAPI = {
  list: () => api.get('/api/attacks/list'),
  start: (attackRequest) => api.post('/api/attacks/start', attackRequest),
  stop: (attackId) => api.post(`/api/attacks/stop/${attackId}`),
  stopAll: () => api.post('/api/attacks/stop-all'),
  getActive: () => api.get('/api/attacks/active'),
  getHistory: (limit = 100) => api.get('/api/attacks/history', { params: { limit } }),
  getStatus: (attackId) => api.get(`/api/attacks/${attackId}`),
};

// Stats API
export const statsAPI = {
  getSummary: () => api.get('/api/stats/summary'),
  getModel: () => api.get('/api/stats/model'),
  getWebSocket: () => api.get('/api/stats/websocket'),
  getSystem: () => api.get('/api/stats/system'),
};

// Health check
export const healthCheck = () => api.get('/health');

export default api;
