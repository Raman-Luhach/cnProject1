// API Configuration
export const API_BASE_URL = 'http://localhost:8000';
export const WS_URL = 'ws://localhost:8000/ws';

// Default VM Configuration
export const DEFAULT_VM_IP = '192.168.64.2';
export const DEFAULT_VM_NAME = 'ids_target';

// Attack Types
export const ATTACK_TYPES = [
  'Benign',
  'Brute Force -Web',
  'Brute Force -XSS',
  'DDOS attack-HOIC',
  'DDOS attack-LOIC-UDP',
  'DDoS attacks-LOIC-HTTP',
  'DoS attacks-GoldenEye',
  'DoS attacks-Hulk',
  'DoS attacks-SlowHTTPTest',
  'DoS attacks-Slowloris',
  'FTP-BruteForce',
  'SQL Injection',
  'SSH-Bruteforce'
];

// Attack Type Colors
export const ATTACK_COLORS = {
  'Benign': '#4caf50',
  'Brute Force -Web': '#ff9800',
  'Brute Force -XSS': '#ff5722',
  'DDOS attack-HOIC': '#f44336',
  'DDOS attack-LOIC-UDP': '#e91e63',
  'DDoS attacks-LOIC-HTTP': '#9c27b0',
  'DoS attacks-GoldenEye': '#673ab7',
  'DoS attacks-Hulk': '#3f51b5',
  'DoS attacks-SlowHTTPTest': '#2196f3',
  'DoS attacks-Slowloris': '#00bcd4',
  'FTP-BruteForce': '#009688',
  'SQL Injection': '#ff5722',
  'SSH-Bruteforce': '#795548'
};

// Chart Configuration
export const CHART_CONFIG = {
  maxDataPoints: 100,
  updateInterval: 1000, // ms
};

// WebSocket Events
export const WS_EVENTS = {
  DETECTION: 'detection',
  VM_STATUS: 'vm_status',
  ATTACK_STATUS: 'attack_status',
  STATS: 'stats',
  MONITORING_STATUS: 'monitoring_status',
  CONNECTED: 'connected'
};
