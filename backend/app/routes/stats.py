"""Statistics API routes"""

from fastapi import APIRouter
from typing import Dict
import logging

from app.services.detection_engine import get_detection_engine
from app.services.ids_model import get_model_service
from app.websocket_manager import get_websocket_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/summary")
async def get_stats_summary() -> Dict:
    """Get detection statistics summary"""
    detection_engine = get_detection_engine()
    stats = detection_engine.get_stats()
    capture_stats = stats.get('capture_stats', {})
    
    return {
        "monitoring": {
            "is_running": stats['is_running'],
            "uptime_seconds": stats['uptime_seconds'],
            "start_time": stats['start_time']
        },
        "detection": {
            "total_flows": stats['total_flows'],
            "total_detections": stats['total_detections'],
            "benign_count": stats['benign_count'],
            "attack_count": stats['attack_count'],
            "detection_rate": stats['detection_rate'],
            "active_flows": stats['active_flows']
        },
        "attacks": {
            "distribution": stats['attack_distribution']
        },
        "packets_captured": capture_stats.get('packet_count', 0),
        "bytes_captured": capture_stats.get('byte_count', 0),
        "capture_duration": stats['uptime_seconds'],
        "packets_per_second": capture_stats.get('packet_count', 0) / stats['uptime_seconds'] if stats['uptime_seconds'] > 0 else 0,
        "capture": capture_stats
    }


@router.get("/model")
async def get_model_info() -> Dict:
    """Get model information"""
    model_service = get_model_service()
    return model_service.get_model_info()


@router.get("/websocket")
async def get_websocket_stats() -> Dict:
    """Get WebSocket statistics"""
    ws_manager = get_websocket_manager()
    
    return {
        "active_connections": ws_manager.get_active_connection_count(),
        "total_connections": ws_manager.connection_count
    }


@router.get("/system")
async def get_system_stats() -> Dict:
    """Get overall system statistics"""
    detection_engine = get_detection_engine()
    model_service = get_model_service()
    ws_manager = get_websocket_manager()
    
    detection_stats = detection_engine.get_stats()
    model_info = model_service.get_model_info()
    
    return {
        "detection_engine": {
            "running": detection_stats['is_running'],
            "uptime": detection_stats['uptime_seconds']
        },
        "model": {
            "loaded": model_info['loaded'],
            "accuracy": model_info.get('accuracy', 0),
            "num_classes": model_info.get('num_classes', 0)
        },
        "websocket": {
            "connections": ws_manager.get_active_connection_count()
        },
        "totals": {
            "flows_processed": detection_stats['total_flows'],
            "attacks_detected": detection_stats['attack_count'],
            "benign_flows": detection_stats['benign_count']
        }
    }
