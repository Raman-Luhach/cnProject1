"""
Monitoring endpoints for starting/stopping IDS monitoring
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import time
import os
import sys

from app.models import MonitoringStatus
from app.routes import stats

router = APIRouter()


class StartMonitoringRequest(BaseModel):
    """Request to start monitoring"""
    interface: str
    target_ip: str


@router.post("/start", response_model=MonitoringStatus)
async def start_monitoring(request: StartMonitoringRequest):
    """Start IDS monitoring"""
    from app.main import monitoring_service, ws_manager
    
    if monitoring_service and monitoring_service.is_running:
        raise HTTPException(status_code=400, detail="Monitoring is already running")
    
    # Initialize monitoring service
    # Get absolute path to model directory
    # From backend/app/routes/monitoring.py -> go up to project root -> cnmodel/ids_ddos_model
    current_file = os.path.abspath(__file__)  # backend/app/routes/monitoring.py
    routes_dir = os.path.dirname(current_file)  # backend/app/routes
    app_dir = os.path.dirname(routes_dir)  # backend/app
    backend_dir = os.path.dirname(app_dir)  # backend
    project_root = os.path.dirname(backend_dir)  # cnProject
    model_dir = os.path.join(project_root, 'cnmodel', 'ids_ddos_model')
    
    # Verify model directory exists
    if not os.path.exists(model_dir):
        raise HTTPException(
            status_code=500, 
            detail=f"Model directory not found: {model_dir}. Please check the path."
        )
    
    try:
        # Verify model files exist
        required_files = ['ids_model.keras', 'scaler.pkl', 'selector.pkl', 'encoder.pkl', 'model_metadata.json']
        missing_files = [f for f in required_files if not os.path.exists(os.path.join(model_dir, f))]
        if missing_files:
            raise HTTPException(
                status_code=500,
                detail=f"Missing model files: {', '.join(missing_files)} in {model_dir}"
            )
        
        from app.services.ids_monitor import RealTimeIDSMonitor
        
        # Create new monitoring service instance
        new_monitoring_service = RealTimeIDSMonitor(
            model_dir=model_dir,
            target_vm_ip=request.target_ip,
            interface=request.interface
        )
        
        # Set callbacks for WebSocket broadcasting
        def attack_callback(attack_data):
            ws_manager.broadcast_sync({
                'type': 'attack',
                **attack_data
            })
            # Update stats
            stats.global_stats['total_flows'] += 1
            stats.global_stats['attack_flows'] += 1
            if attack_data['type'] not in stats.global_stats['attacks_by_type']:
                stats.global_stats['attacks_by_type'][attack_data['type']] = 0
            stats.global_stats['attacks_by_type'][attack_data['type']] += 1
            # Add to recent attacks
            from app.models import AttackDetection
            stats.recent_attacks.insert(0, AttackDetection(**attack_data))
            if len(stats.recent_attacks) > 100:
                stats.recent_attacks.pop()
        
        def benign_callback(flow_data):
            ws_manager.broadcast_sync({
                'type': 'benign',
                **flow_data
            })
            # Update stats
            stats.global_stats['total_flows'] += 1
            stats.global_stats['benign_flows'] += 1
        
        new_monitoring_service.set_callbacks(attack_callback, benign_callback)
        new_monitoring_service.start()
        
        # Update global reference
        import app.main as main_module
        main_module.monitoring_service = new_monitoring_service
        
        return MonitoringStatus(
            is_running=True,
            interface=request.interface,
            target_ip=request.target_ip,
            start_time=time.time()
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error starting monitoring: {error_details}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to start monitoring: {str(e)}. Model dir: {model_dir}"
        )


@router.post("/stop", response_model=MonitoringStatus)
async def stop_monitoring():
    """Stop IDS monitoring"""
    from app.main import monitoring_service
    
    if not monitoring_service or not monitoring_service.is_running:
        raise HTTPException(status_code=400, detail="Monitoring is not running")
    
    monitoring_service.stop()
    
    return MonitoringStatus(
        is_running=False,
        interface=None,
        target_ip=None,
        start_time=None
    )


@router.get("/status", response_model=MonitoringStatus)
async def get_monitoring_status():
    """Get current monitoring status"""
    from app.main import monitoring_service
    
    if monitoring_service and monitoring_service.is_running:
        return MonitoringStatus(
            is_running=True,
            interface=monitoring_service.interface,
            target_ip=monitoring_service.target_vm_ip,
            start_time=None
        )
    else:
        return MonitoringStatus(
            is_running=False,
            interface=None,
            target_ip=None,
            start_time=None
        )

