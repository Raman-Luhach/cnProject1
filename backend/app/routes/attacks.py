"""
Attack control endpoints for launching attacks
"""
from fastapi import APIRouter, HTTPException
from app.models import AttackRequest, AttackListResponse
import threading

router = APIRouter()

# List of available attacks
AVAILABLE_ATTACKS = [
    "DDOS attack-HOIC",
    "DDOS attack-LOIC-UDP",
    "DDoS attacks-LOIC-HTTP",
    "DoS attacks-GoldenEye",
    "DoS attacks-Hulk",
    "DoS attacks-SlowHTTPTest",
    "DoS attacks-Slowloris",
    "Brute Force -Web",
    "Brute Force -XSS",
    "FTP-BruteForce",
    "SQL Injection",
    "SSH-Bruteforce"
]


@router.post("/launch")
async def launch_attack(request: AttackRequest):
    """Launch an attack against the target"""
    if request.attack_type not in AVAILABLE_ATTACKS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid attack type. Available: {', '.join(AVAILABLE_ATTACKS)}"
        )
    
    try:
        from app.services.attack_orchestrator import AttackOrchestrator
        
        print(f"🚀 Launching: {request.attack_type} → {request.target_ip} ({request.duration}s)")
        
        # Create orchestrator for this target
        orchestrator = AttackOrchestrator(request.target_ip)
        
        # Launch attack in background thread
        def run_attack():
            try:
                orchestrator.launch_attack(request.attack_type, request.duration)
            except Exception as e:
                print(f"❌ Attack execution error: {e}")
                import traceback
                traceback.print_exc()
        
        thread = threading.Thread(target=run_attack, daemon=True, name=f"Attack-{request.attack_type}")
        thread.start()
        
        return {
            "status": "launched",
            "attack_type": request.attack_type,
            "target_ip": request.target_ip,
            "duration": request.duration,
            "message": f"Attack {request.attack_type} launched against {request.target_ip}"
        }
    except Exception as e:
        print(f"❌ Error launching attack: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to launch attack: {str(e)}")


@router.post("/stop")
async def stop_attack():
    """Stop all running attacks"""
    # Note: This is a simplified version - in production you'd track all orchestrators
    return {
        "status": "stopped",
        "message": "Attack stop requested. Note: Attacks run for their duration."
    }


@router.get("/list", response_model=AttackListResponse)
async def list_attacks():
    """Get list of available attack types"""
    return AttackListResponse(attacks=AVAILABLE_ATTACKS)

