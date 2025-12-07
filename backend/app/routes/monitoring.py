"""Monitoring API routes"""

from fastapi import APIRouter, HTTPException
from typing import Dict
import logging

from app.services.detection_engine import get_detection_engine
from app.services.vm_manager import get_vm_manager
from app.websocket_manager import get_websocket_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])


@router.post("/start")
async def start_monitoring(vm_ip: str = None, interface: str = None) -> Dict:
    """Start packet capture and detection"""
    from app.config import VM_IP
    
    detection_engine = get_detection_engine()
    ws_manager = get_websocket_manager()
    
    # If no VM IP provided, try to get from VM manager, then use default
    if not vm_ip:
        vm_manager = get_vm_manager()
        vm_ip = await vm_manager.get_vm_ip()
        
        # If still no IP, use the configured default
        if not vm_ip:
            vm_ip = VM_IP
            logger.info(f"Using configured default VM IP: {vm_ip}")
        
        if not vm_ip:
            raise HTTPException(
                status_code=400,
                detail="VM IP not provided and no running VM found"
            )
    
    success = await detection_engine.start_monitoring(vm_ip, interface)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to start monitoring")
    
    # Broadcast status
    await ws_manager.broadcast_monitoring_status(True, "Monitoring started")
    
    return {
        "success": True,
        "message": "Monitoring started",
        "vm_ip": vm_ip,
        "interface": detection_engine.interface_manager.interface
    }


@router.post("/stop")
async def stop_monitoring() -> Dict:
    """Stop packet capture and detection"""
    detection_engine = get_detection_engine()
    ws_manager = get_websocket_manager()
    
    success = await detection_engine.stop_monitoring()
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to stop monitoring")
    
    # Broadcast status
    await ws_manager.broadcast_monitoring_status(False, "Monitoring stopped")
    
    stats = detection_engine.get_stats()
    
    return {
        "success": True,
        "message": "Monitoring stopped",
        "stats": stats
    }


@router.get("/status")
async def get_monitoring_status() -> Dict:
    """Get monitoring status"""
    detection_engine = get_detection_engine()
    
    return {
        "is_running": detection_engine.is_running,
        "stats": detection_engine.get_stats()
    }
