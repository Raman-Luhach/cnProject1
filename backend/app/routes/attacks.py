"""Attack API routes"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List
import logging

from app.models.attack import AttackRequest, AttackResponse, AttackListItem
from app.services.attack_orchestrator import get_attack_orchestrator
from app.websocket_manager import get_websocket_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/attacks", tags=["attacks"])


@router.get("/list")
async def list_available_attacks() -> List[AttackListItem]:
    """Get list of available attack types"""
    orchestrator = get_attack_orchestrator()
    attacks = orchestrator.get_available_attacks()
    
    return [AttackListItem(**attack) for attack in attacks]


@router.post("/start")
async def start_attack(request: AttackRequest) -> AttackResponse:
    """Start an attack"""
    orchestrator = get_attack_orchestrator()
    ws_manager = get_websocket_manager()
    
    # Start attack
    attack = await orchestrator.start_attack(
        attack_type=request.attack_type,
        target_ip=request.target_ip,
        target_port=request.target_port,
        duration=request.duration,
        intensity=request.intensity,
        **request.parameters
    )
    
    if not attack:
        raise HTTPException(status_code=500, detail="Failed to start attack")
    
    # Get status
    status = attack.get_status()
    
    # Broadcast status
    await ws_manager.broadcast_attack_status(status)
    
    return AttackResponse(**status)


@router.post("/stop/{attack_id}")
async def stop_attack(attack_id: str) -> Dict:
    """Stop a specific attack"""
    orchestrator = get_attack_orchestrator()
    ws_manager = get_websocket_manager()
    
    success = await orchestrator.stop_attack(attack_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Attack not found")
    
    # Broadcast status
    await ws_manager.broadcast_attack_status({
        'attack_id': attack_id,
        'status': 'stopped'
    })
    
    return {
        "success": True,
        "message": f"Attack {attack_id} stopped"
    }


@router.post("/stop-all")
async def stop_all_attacks() -> Dict:
    """Stop all active attacks"""
    orchestrator = get_attack_orchestrator()
    ws_manager = get_websocket_manager()
    
    count = await orchestrator.stop_all_attacks()
    
    # Broadcast status
    await ws_manager.broadcast_attack_status({
        'status': 'all_stopped',
        'count': count
    })
    
    return {
        "success": True,
        "message": f"Stopped {count} attacks"
    }


@router.get("/active")
async def get_active_attacks() -> List[Dict]:
    """Get all active attacks"""
    orchestrator = get_attack_orchestrator()
    return orchestrator.get_active_attacks()


@router.get("/history")
async def get_attack_history(limit: int = 100) -> List[Dict]:
    """Get attack history"""
    orchestrator = get_attack_orchestrator()
    return orchestrator.get_attack_history(limit)


@router.get("/{attack_id}")
async def get_attack_status(attack_id: str) -> Dict:
    """Get status of specific attack"""
    orchestrator = get_attack_orchestrator()
    status = orchestrator.get_attack_status(attack_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Attack not found")
    
    return status
