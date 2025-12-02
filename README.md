# IDS Real-Time Monitoring System

A comprehensive real-time Intrusion Detection System (IDS) with ML-based attack classification, featuring a React frontend dashboard and FastAPI backend for monitoring network traffic and detecting 13 types of cyber attacks.

## Features

- **Real-time Network Monitoring**: Captures and analyzes network packets in real-time
- **ML-Based Detection**: Uses a trained CNN-BiLSTM-Attention model for attack classification
- **13 Attack Types**: Detects DDoS, DoS, brute force, SQL injection, XSS, and more
- **Interactive Dashboard**: React-based UI with real-time updates via WebSockets
- **Attack Orchestrator**: Built-in tools to launch controlled attacks for testing
- **Comprehensive Analytics**: Statistics, charts, and flow tables

## Architecture

```
cnProject/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── models.py          # Pydantic models
│   │   ├── websocket_manager.py
│   │   ├── routes/            # API endpoints
│   │   └── services/          # Core services
│   │       ├── ids_monitor.py          # Real-time monitoring
│   │       ├── feature_extractor.py    # Feature extraction (68 features)
│   │       └── attack_orchestrator.py  # Attack simulation
│   └── requirements.txt
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── services/          # API & WebSocket clients
│   │   ├── styles/            # CSS styling
│   │   └── utils/             # Constants & utilities
│   └── package.json
└── cnmodel/                    # ML model files
    └── ids_ddos_model/
        ├── ids_model.keras     # Trained model
        ├── scaler.pkl          # Feature scaler
        ├── selector.pkl        # Feature selector
        ├── encoder.pkl         # Label encoder
        ├── model_metadata.json # Model info
        └── use_model.py        # Model inference class
```

## Detected Attack Types

1. DDOS attack-HOIC
2. DDOS attack-LOIC-UDP
3. DDoS attacks-LOIC-HTTP
4. DoS attacks-GoldenEye
5. DoS attacks-Hulk
6. DoS attacks-SlowHTTPTest
7. DoS attacks-Slowloris
8. Brute Force -Web
9. Brute Force -XSS
10. FTP-BruteForce
11. SQL Injection
12. SSH-Bruteforce
13. Benign (normal traffic)

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- Multipass VM (for target) or VirtualBox
- Network access for packet capture (may require sudo)

## Installation

### 1. Backend Setup

```bash
cd cnProject/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Frontend Setup

```bash
cd cnProject/frontend

# Install dependencies
npm install
```

### 3. Target VM Setup (Multipass)

```bash
# Create Ubuntu VM
multipass launch --name target-vm --mem 2G --disk 20G

# Get VM IP
multipass info target-vm | grep IPv4

# Setup vulnerable services
multipass shell target-vm

# Inside VM, run:
sudo apt update && sudo apt upgrade -y
sudo apt install -y apache2 openssh-server vsftpd mysql-server php libapache2-mod-php
sudo systemctl start apache2 ssh vsftpd mysql
sudo systemctl enable apache2 ssh vsftpd mysql

# Create test web app
sudo mkdir -p /var/www/html/test
echo '<?php if(isset($_GET["id"])) echo "<h2>User ID: " . $_GET["id"] . "</h2>"; ?>' | sudo tee /var/www/html/test/index.php
```

## Configuration

### Backend Configuration

Create `.env` file in `backend/` directory:

```env
MODEL_DIR=../cnmodel/ids_ddos_model
TARGET_VM_IP=192.168.64.2
NETWORK_INTERFACE=bridge100
```

### Frontend Configuration

Create `.env` file in `frontend/` directory:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

## Running the System

### 1. Start Backend

```bash
cd cnProject/backend
source venv/bin/activate

# Run with uvicorn (may need sudo for packet capture)
sudo venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### 2. Start Frontend

```bash
cd cnProject/frontend

# Run development server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

### 3. Using the Dashboard

1. **Open Dashboard**: Navigate to `http://localhost:5173`
2. **Configure Settings**:
   - Network Interface: `bridge100` (for Multipass) or `en0` (for Wi-Fi)
   - Target VM IP: Your VM's IP (e.g., `192.168.64.2`)
3. **Start Monitoring**: Click "Start Monitoring" button
4. **Launch Attacks**: Select attack type and click "Launch Attack"
5. **View Results**: Real-time attack detections appear in dashboard

## API Endpoints

### Monitoring

- `POST /api/monitoring/start` - Start IDS monitoring
- `POST /api/monitoring/stop` - Stop monitoring
- `GET /api/monitoring/status` - Get monitoring status

### Attacks

- `POST /api/attacks/launch` - Launch an attack
- `POST /api/attacks/stop` - Stop all attacks
- `GET /api/attacks/list` - List available attacks

### Statistics

- `GET /api/stats/summary` - Get statistics summary
- `GET /api/stats/recent` - Get recent attacks

### WebSocket

- `WS /ws` - Real-time attack detection updates

## Feature Extraction

The system extracts 68 features from network flows:

- **Flow Duration**: Time duration of the flow
- **Packet Counts**: Forward/backward packet counts
- **Byte Counts**: Total bytes transferred
- **Packet Length Statistics**: Max, min, mean, std for packet lengths
- **Inter-Arrival Times (IAT)**: Time between packets
- **TCP Flags**: SYN, ACK, FIN, RST, PSH, URG counts
- **Packet Rates**: Packets/second, bytes/second
- **Active/Idle Times**: Flow activity patterns
- **Additional Features**: Header lengths, packet ratios, etc.

## Model Performance

- **Accuracy**: 91.83%
- **Precision**: 94.74%
- **Recall**: 91.83%
- **F1-Score**: 90.85%

## Troubleshooting

### Permission Issues (Packet Capture)

```bash
# Run backend with sudo
sudo venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### WebSocket Connection Failed

- Check backend is running
- Verify WebSocket URL in frontend `.env`
- Check firewall settings

### Model Loading Errors

- Ensure model files exist in `cnmodel/ids_ddos_model/`
- Check TensorFlow/Keras installation
- Verify Python version compatibility

### Network Interface Not Found

```bash
# List available interfaces
ifconfig

# On Mac, common interfaces:
# - en0: Wi-Fi
# - en1: Ethernet
# - bridge100: Multipass bridge

# Update interface in dashboard controls
```

## Development

### Backend Development

```bash
cd backend

# Run tests (if available)
pytest

# Format code
black app/

# Type checking
mypy app/
```

### Frontend Development

```bash
cd frontend

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Production Deployment

### Backend

```bash
# Install production dependencies
pip install -r requirements.txt

# Run with gunicorn
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend

```bash
# Build for production
npm run build

# Deploy dist/ folder to web server (nginx, Apache, etc.)
```

## Security Considerations

- **This system is for educational/testing purposes only**
- Run attack scripts only on your own networks and VMs
- Ensure proper network isolation for testing
- Use firewall rules to limit scope
- Do not use on production networks without authorization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational purposes. See LICENSE file for details.

## Acknowledgments

- TensorFlow/Keras for ML framework
- FastAPI for backend framework
- React and Recharts for frontend
- Scapy for packet capture
- Multipass for VM management

## Support

For issues or questions:
- Check documentation above
- Review API docs at `/docs`
- Check console logs for errors
- Ensure all services are running

## Project Status

- ✅ Backend API implemented
- ✅ Feature extraction (68 features)
- ✅ Real-time IDS monitoring
- ✅ Attack orchestrator (13 attack types)
- ✅ React dashboard
- ✅ WebSocket real-time updates
- ✅ Complete documentation

## Future Enhancements

- [ ] Database persistence for attack history
- [ ] User authentication and authorization
- [ ] Multiple VM monitoring support
- [ ] Advanced visualization options
- [ ] Export reports (PDF, CSV)
- [ ] Email/SMS alerts
- [ ] Custom attack scripts
- [ ] Model retraining interface

# cnProject1
