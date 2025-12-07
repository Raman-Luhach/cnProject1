"""
API endpoints for launching real attack tools directly from frontend
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Literal
import subprocess
import logging
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/attack-launcher", tags=["attack-launcher"])

class AttackLaunchRequest(BaseModel):
    attack_type: Literal["hulk", "goldeneye", "http_flood_bash", "http_flood_python", "slowloris"]
    target_ip: str = "192.168.64.3"
    duration: int = 30  # seconds
    threads: Optional[int] = None  # Auto-set based on attack type

# Store active processes
active_attacks = {}

@router.post("/launch")
async def launch_real_attack(request: AttackLaunchRequest):
    """Launch a real attack tool (Python/Bash scripts)"""
    
    logger.info(f"Launching {request.attack_type} attack against {request.target_ip}")
    
    # Prepare command based on attack type
    if request.attack_type == "hulk":
        cmd = [
            "python3", "/tmp/attack_hulk.py",
            f"http://{request.target_ip}",
            str(request.duration)
        ]
        display_name = "HULK HTTP Flood"
    
    elif request.attack_type == "goldeneye":
        cmd = [
            "python3", "/tmp/attack_goldeneye.py",
            f"http://{request.target_ip}",
            str(request.duration)
        ]
        display_name = "GoldenEye HTTP Flood"
    
    elif request.attack_type == "http_flood_bash":
        cmd = [
            "bash", "/tmp/attack_http_flood.sh",
            request.target_ip,
            str(request.duration)
        ]
        display_name = "HTTP Flood (Bash)"
    
    elif request.attack_type == "http_flood_python":
        cmd = [
            "python3", "/tmp/attack_http_flood_python.py",
            request.target_ip,
            str(request.duration)
        ]
        display_name = "HTTP Flood (Python)"
    
    elif request.attack_type == "slowloris":
        cmd = [
            "bash", "/tmp/attack_slowloris_real.sh",
            request.target_ip,
            str(request.duration)
        ]
        display_name = "Slowloris"
    
    else:
        raise HTTPException(status_code=400, detail=f"Unknown attack type: {request.attack_type}")
    
    try:
        # Launch attack in background
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        attack_id = f"{request.attack_type}_{process.pid}"
        active_attacks[attack_id] = {
            "process": process,
            "attack_type": display_name,
            "target_ip": request.target_ip,
            "duration": request.duration,
            "pid": process.pid
        }
        
        logger.info(f"Attack launched: {attack_id} (PID: {process.pid})")
        
        return {
            "success": True,
            "attack_id": attack_id,
            "attack_type": display_name,
            "target_ip": request.target_ip,
            "duration": request.duration,
            "pid": process.pid,
            "message": f"{display_name} attack launched successfully"
        }
    
    except Exception as e:
        logger.error(f"Failed to launch attack: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to launch attack: {str(e)}")

@router.get("/active")
async def get_active_real_attacks():
    """Get list of active attack processes"""
    result = []
    to_remove = []
    
    for attack_id, info in active_attacks.items():
        process = info["process"]
        poll = process.poll()
        
        if poll is None:
            # Still running
            result.append({
                "attack_id": attack_id,
                "attack_type": info["attack_type"],
                "target_ip": info["target_ip"],
                "duration": info["duration"],
                "pid": info["pid"],
                "status": "running"
            })
        else:
            # Finished
            to_remove.append(attack_id)
    
    # Clean up finished attacks
    for attack_id in to_remove:
        del active_attacks[attack_id]
    
    return result

@router.post("/stop/{attack_id}")
async def stop_real_attack(attack_id: str):
    """Stop a running attack process"""
    
    if attack_id not in active_attacks:
        raise HTTPException(status_code=404, detail="Attack not found")
    
    info = active_attacks[attack_id]
    process = info["process"]
    
    try:
        process.terminate()
        await asyncio.sleep(1)
        
        if process.poll() is None:
            # Still running, force kill
            process.kill()
        
        del active_attacks[attack_id]
        
        logger.info(f"Attack stopped: {attack_id}")
        
        return {
            "success": True,
            "attack_id": attack_id,
            "message": "Attack stopped successfully"
        }
    
    except Exception as e:
        logger.error(f"Failed to stop attack {attack_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop attack: {str(e)}")

@router.post("/stop-all")
async def stop_all_real_attacks():
    """Stop all running attack processes"""
    
    stopped = []
    errors = []
    
    for attack_id in list(active_attacks.keys()):
        try:
            info = active_attacks[attack_id]
            process = info["process"]
            process.terminate()
            await asyncio.sleep(0.5)
            
            if process.poll() is None:
                process.kill()
            
            del active_attacks[attack_id]
            stopped.append(attack_id)
            
        except Exception as e:
            errors.append(f"{attack_id}: {str(e)}")
    
    return {
        "success": len(errors) == 0,
        "stopped": stopped,
        "errors": errors if errors else None,
        "message": f"Stopped {len(stopped)} attacks"
    }

