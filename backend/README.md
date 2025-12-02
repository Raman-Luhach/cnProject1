# IDS Backend - FastAPI Server

This is the FastAPI backend for the IDS Real-Time Monitoring System.

## Features

- RESTful API for monitoring control
- WebSocket support for real-time updates
- ML model integration for attack detection
- Packet capture and feature extraction
- Attack orchestration for testing

## Structure

```
app/
├── main.py                     # FastAPI application
├── models.py                   # Pydantic models
├── websocket_manager.py        # WebSocket connections
├── routes/                     # API endpoints
│   ├── monitoring.py          # Monitoring control
│   ├── attacks.py             # Attack management
│   └── stats.py               # Statistics
└── services/                   # Core services
    ├── ids_monitor.py         # IDS monitoring engine
    ├── feature_extractor.py   # Feature extraction (68 features)
    └── attack_orchestrator.py # Attack simulation
```

## Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# With sudo (for packet capture)
sudo venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Environment Variables

Create `.env` file:

```env
MODEL_DIR=../cnmodel/ids_ddos_model
TARGET_VM_IP=192.168.64.2
NETWORK_INTERFACE=bridge100
```

## Development

```bash
# Format code
black app/

# Type checking
mypy app/

# Run tests
pytest
```

