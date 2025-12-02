/**
 * Constants for the IDS Dashboard
 */

export const ATTACK_TYPES = [
  'DDOS attack-HOIC',
  'DDOS attack-LOIC-UDP',
  'DDoS attacks-LOIC-HTTP',
  'DoS attacks-GoldenEye',
  'DoS attacks-Hulk',
  'DoS attacks-SlowHTTPTest',
  'DoS attacks-Slowloris',
  'Brute Force -Web',
  'Brute Force -XSS',
  'FTP-BruteForce',
  'SQL Injection',
  'SSH-Bruteforce',
];

export const ATTACK_COLORS = {
  'DDOS attack-HOIC': '#ff4444',
  'DDOS attack-LOIC-UDP': '#ff6b6b',
  'DDoS attacks-LOIC-HTTP': '#ee5a6f',
  'DoS attacks-GoldenEye': '#c44569',
  'DoS attacks-Hulk': '#f8b500',
  'DoS attacks-SlowHTTPTest': '#ffa502',
  'DoS attacks-Slowloris': '#ff6348',
  'Brute Force -Web': '#ff4757',
  'Brute Force -XSS': '#ff6348',
  'FTP-BruteForce': '#ff4757',
  'SQL Injection': '#ee5a6f',
  'SSH-Bruteforce': '#c44569',
  'Benign': '#4caf50',
};

export const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const DEFAULT_TARGET_IP = '192.168.64.2';

export const DEFAULT_INTERFACE = 'bridge100';

