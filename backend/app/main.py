"""
FastAPI main application for IDS Real-Time Monitoring System
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time

from app.models import HealthResponse
from app.routes import monitoring, attacks, stats
from app.websocket_manager import WebSocketManager

# Global WebSocket manager
ws_manager = WebSocketManager()

# Global monitoring service (will be initialized)
monitoring_service = None

# Global attack orchestrator (will be initialized per attack)
attack_orchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler"""
    # Startup
    print("🚀 Starting IDS Monitoring System")
    yield
    # Shutdown
    print("🛑 Shutting down IDS Monitoring System")
    if monitoring_service and monitoring_service.is_running:
        monitoring_service.stop()


app = FastAPI(
    title="IDS Real-Time Monitoring API",
    description="Real-time intrusion detection system with ML-based attack classification",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["monitoring"])
app.include_router(attacks.router, prefix="/api/attacks", tags=["attacks"])
app.include_router(stats.router, prefix="/api/stats", tags=["statistics"])


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        model_loaded=True
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        model_loaded=True
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back for heartbeat
            await websocket.send_text(f"pong: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        print("Client disconnected")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

