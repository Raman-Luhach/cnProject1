import { WS_URL, WS_EVENTS } from '../utils/constants';

class WebSocketService {
  constructor() {
    this.ws = null;
    this.reconnectInterval = 3000;
    this.reconnectTimer = null;
    this.listeners = {};
    this.isConnecting = false;
  }

  connect() {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    if (this.isConnecting) {
      return;
    }

    this.isConnecting = true;
    console.log('Connecting to WebSocket...');

    try {
      this.ws = new WebSocket(WS_URL);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.isConnecting = false;
        this.clearReconnectTimer();
        this.notifyListeners('connection', { status: 'connected' });
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          const eventType = data.event_type;
          
          if (eventType) {
            this.notifyListeners(eventType, data);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.isConnecting = false;
        this.notifyListeners('connection', { status: 'error', error });
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.isConnecting = false;
        this.notifyListeners('connection', { status: 'disconnected' });
        this.scheduleReconnect();
      };
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      this.isConnecting = false;
      this.scheduleReconnect();
    }
  }

  disconnect() {
    this.clearReconnectTimer();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  scheduleReconnect() {
    this.clearReconnectTimer();
    console.log(`Reconnecting in ${this.reconnectInterval}ms...`);
    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, this.reconnectInterval);
  }

  clearReconnectTimer() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  on(eventType, callback) {
    if (!this.listeners[eventType]) {
      this.listeners[eventType] = [];
    }
    this.listeners[eventType].push(callback);
  }

  off(eventType, callback) {
    if (!this.listeners[eventType]) {
      return;
    }
    this.listeners[eventType] = this.listeners[eventType].filter(
      (cb) => cb !== callback
    );
  }

  notifyListeners(eventType, data) {
    if (this.listeners[eventType]) {
      this.listeners[eventType].forEach((callback) => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in listener for ${eventType}:`, error);
        }
      });
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(typeof data === 'string' ? data : JSON.stringify(data));
    } else {
      console.warn('WebSocket not connected');
    }
  }

  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN;
  }
}

// Create singleton instance
const wsService = new WebSocketService();

export default wsService;
