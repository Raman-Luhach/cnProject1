"""WebSocket manager for real-time updates"""

import json
import logging
import asyncio
from typing import Set, Dict, Any
from fastapi import WebSocket
from datetime import datetime

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and broadcasts"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.connection_count = 0
    
    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        self.connection_count += 1
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
        
        # Send welcome message
        await self.send_personal_message({
            'event_type': 'connected',
            'message': 'Connected to IDS monitoring system',
            'timestamp': datetime.now().isoformat()
        }, websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send a message to a specific WebSocket"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients"""
        if not self.active_connections:
            return
        
        disconnected = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.add(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_detection(self, detection_data: Dict[str, Any]):
        """Broadcast detection event"""
        message = {
            'event_type': 'detection',
            'timestamp': datetime.now().isoformat(),
            'data': detection_data
        }
        await self.broadcast(message)
        logger.debug(f"Broadcasted detection: {detection_data.get('prediction', 'Unknown')}")
    
    async def broadcast_vm_status(self, vm_status: Dict[str, Any]):
        """Broadcast VM status update"""
        message = {
            'event_type': 'vm_status',
            'timestamp': datetime.now().isoformat(),
            'data': vm_status
        }
        await self.broadcast(message)
        logger.debug("Broadcasted VM status")
    
    async def broadcast_attack_status(self, attack_status: Dict[str, Any]):
        """Broadcast attack status update"""
        message = {
            'event_type': 'attack_status',
            'timestamp': datetime.now().isoformat(),
            'data': attack_status
        }
        await self.broadcast(message)
        logger.debug(f"Broadcasted attack status: {attack_status.get('attack_type', 'Unknown')}")
    
    async def broadcast_stats(self, stats: Dict[str, Any]):
        """Broadcast statistics update"""
        message = {
            'event_type': 'stats',
            'timestamp': datetime.now().isoformat(),
            'data': stats
        }
        await self.broadcast(message)
        logger.debug("Broadcasted stats")
    
    async def broadcast_monitoring_status(self, is_running: bool, message_text: str = ""):
        """Broadcast monitoring status change"""
        message = {
            'event_type': 'monitoring_status',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'is_running': is_running,
                'message': message_text
            }
        }
        await self.broadcast(message)
        logger.info(f"Broadcasted monitoring status: {is_running}")
    
    def get_active_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)


# Global WebSocket manager instance
_ws_manager = None


def get_websocket_manager() -> WebSocketManager:
    """Get or create global WebSocket manager instance"""
    global _ws_manager
    if _ws_manager is None:
        _ws_manager = WebSocketManager()
    return _ws_manager
