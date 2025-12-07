"""Main FastAPI application"""

import sys
import os
from pathlib import Path

# Add parent directory to path to allow imports
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import CORS_ORIGINS, API_HOST, API_PORT, LOG_LEVEL, LOG_FORMAT
from app.routes import monitoring, attacks, vm, stats, attack_launcher
from app.websocket_manager import get_websocket_manager
from app.services.detection_engine import get_detection_engine
from app.services.ids_model import get_model_service

# Configure logging
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    logger.info("Starting IDS Monitoring System...")
    
    # Load model
    model_service = get_model_service()
    if model_service.is_loaded:
        logger.info("Model loaded successfully")
    else:
        logger.error("Failed to load model")
    
    # Register detection callback for WebSocket broadcasts
    detection_engine = get_detection_engine()
    ws_manager = get_websocket_manager()
    
    async def detection_callback(detection):
        """Callback to broadcast detections"""
        await ws_manager.broadcast_detection({
            'flow_id': detection.flow_id,
            'timestamp': detection.timestamp.isoformat(),
            'prediction': detection.prediction,
            'confidence': detection.confidence,
            'src_ip': detection.src_ip,
            'dst_ip': detection.dst_ip,
            'src_port': detection.src_port,
            'dst_port': detection.dst_port,
            'protocol': detection.protocol,
            'packet_count': detection.packet_count,
            'byte_count': detection.byte_count,
            'is_attack': detection.is_attack
        })
    
    detection_engine.register_detection_callback(detection_callback)
    
    logger.info("IDS Monitoring System started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down IDS Monitoring System...")
    
    # Stop detection if running
    if detection_engine.is_running:
        await detection_engine.stop_monitoring()
    
    logger.info("IDS Monitoring System shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="IDS Monitoring System",
    description="Live Intrusion Detection System with ML-based attack detection",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(monitoring.router)
app.include_router(attacks.router)
app.include_router(vm.router)
app.include_router(stats.router)
app.include_router(attack_launcher.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "IDS Monitoring System",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    detection_engine = get_detection_engine()
    model_service = get_model_service()
    
    return {
        "status": "healthy",
        "model_loaded": model_service.is_loaded,
        "monitoring_active": detection_engine.is_running
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    ws_manager = get_websocket_manager()
    
    await ws_manager.connect(websocket)
    
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            
            # Echo back for ping/pong
            if data == "ping":
                await websocket.send_text("pong")
            
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {API_HOST}:{API_PORT}")
    
    uvicorn.run(
        "app.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level=LOG_LEVEL.lower()
    )
