"""VM management API routes"""

from fastapi import APIRouter, HTTPException
from typing import Dict
import logging

from app.models.vm import VMStatus, VMCreateRequest, VMCreateResponse
from app.services.vm_manager import get_vm_manager
from app.websocket_manager import get_websocket_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/vm", tags=["vm"])


@router.post("/create")
async def create_vm(request: VMCreateRequest) -> VMCreateResponse:
    """Create a new VM"""
    vm_manager = get_vm_manager()
    ws_manager = get_websocket_manager()
    
    success, vm_info, setup_log = await vm_manager.create_vm(
        cpus=request.cpus,
        memory=request.memory,
        disk=request.disk,
        install_services=request.install_services
    )
    
    # Broadcast VM status
    if vm_info:
        await ws_manager.broadcast_vm_status({
            'name': vm_info.name,
            'state': vm_info.state.value,
            'ipv4': vm_info.ipv4
        })
    
    return VMCreateResponse(
        success=success,
        vm_info=vm_info,
        message="VM created successfully" if success else "Failed to create VM",
        setup_log=setup_log
    )


@router.post("/start")
async def start_vm() -> Dict:
    """Start the VM"""
    vm_manager = get_vm_manager()
    ws_manager = get_websocket_manager()
    
    success = await vm_manager.start_vm()
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to start VM")
    
    vm_info = await vm_manager.get_vm_info()
    
    # Broadcast VM status
    if vm_info:
        await ws_manager.broadcast_vm_status({
            'name': vm_info.name,
            'state': vm_info.state.value,
            'ipv4': vm_info.ipv4
        })
    
    return {
        "success": True,
        "message": "VM started",
        "vm_info": vm_info.dict() if vm_info else None
    }


@router.post("/stop")
async def stop_vm() -> Dict:
    """Stop the VM"""
    vm_manager = get_vm_manager()
    ws_manager = get_websocket_manager()
    
    success = await vm_manager.stop_vm()
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to stop VM")
    
    # Broadcast VM status
    await ws_manager.broadcast_vm_status({
        'name': vm_manager.vm_name,
        'state': 'stopped',
        'ipv4': None
    })
    
    return {
        "success": True,
        "message": "VM stopped"
    }


@router.delete("/delete")
async def delete_vm() -> Dict:
    """Delete the VM"""
    vm_manager = get_vm_manager()
    ws_manager = get_websocket_manager()
    
    success = await vm_manager.delete_vm()
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete VM")
    
    # Broadcast VM status
    await ws_manager.broadcast_vm_status({
        'name': vm_manager.vm_name,
        'state': 'deleted',
        'ipv4': None
    })
    
    return {
        "success": True,
        "message": "VM deleted"
    }


@router.get("/status")
async def get_vm_status() -> VMStatus:
    """Get VM status"""
    vm_manager = get_vm_manager()
    
    exists = await vm_manager.vm_exists()
    vm_info = None
    message = "VM not found"
    
    if exists:
        vm_info = await vm_manager.get_vm_info()
        message = f"VM is {vm_info.state.value}" if vm_info else "VM found but info unavailable"
    
    return VMStatus(
        exists=exists,
        vm_info=vm_info,
        message=message
    )


@router.get("/ip")
async def get_vm_ip() -> Dict:
    """Get VM IP address"""
    vm_manager = get_vm_manager()
    
    ip = await vm_manager.get_vm_ip()
    
    if not ip:
        raise HTTPException(status_code=404, detail="VM not running or IP not available")
    
    return {
        "vm_name": vm_manager.vm_name,
        "ipv4": ip
    }

