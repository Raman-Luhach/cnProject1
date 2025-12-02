/**
 * WebSocket Service - Real-time updates from backend
 */

class WebSocketService {
  constructor() {
    this.socket = null;
    this.listeners = {
      attack: [],
      benign: [],
      stats: [],
      connect: [],
      disconnect: [],
      error: [],
    };
    this.reconnectInterval = 3000;
    this.reconnectTimer = null;
  }

  connect(url = 'ws://localhost:8000/ws') {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    console.log('Connecting to WebSocket:', url);
    this.socket = new WebSocket(url);

    this.socket.onopen = () => {
      console.log('WebSocket connected');
      this.notifyListeners('connect', { connected: true });
      if (this.reconnectTimer) {
        clearTimeout(this.reconnectTimer);
        this.reconnectTimer = null;
      }
    };

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.handleMessage(data);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.notifyListeners('error', error);
    };

    this.socket.onclose = () => {
      console.log('WebSocket disconnected');
      this.notifyListeners('disconnect', { connected: false });
      this.scheduleReconnect(url);
    };
  }

  scheduleReconnect(url) {
    if (this.reconnectTimer) {
      return;
    }
    
    this.reconnectTimer = setTimeout(() => {
      console.log('Attempting to reconnect...');
      this.connect(url);
    }, this.reconnectInterval);
  }

  handleMessage(data) {
    // Determine message type and notify appropriate listeners
    if (data.type === 'attack') {
      this.notifyListeners('attack', data);
    } else if (data.type === 'benign' || data.type === 'Benign') {
      this.notifyListeners('benign', data);
    } else if (data.type === 'stats') {
      this.notifyListeners('stats', data);
    } else {
      // Default to attack detection
      if (data.type && data.type !== 'Benign') {
        this.notifyListeners('attack', data);
      } else {
        this.notifyListeners('benign', data);
      }
    }
  }

  on(event, callback) {
    if (this.listeners[event]) {
      this.listeners[event].push(callback);
    }
  }

  off(event, callback) {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    }
  }

  notifyListeners(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(callback => callback(data));
    }
  }

  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket not connected');
    }
  }

  disconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}

export default new WebSocketService();

