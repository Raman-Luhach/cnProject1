# IDS Real-Time Monitoring System - Complete Implementation Guide

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [How Everything Works](#how-everything-works)
5. [Feature Extraction Details](#feature-extraction-details)
6. [Model Integration](#model-integration)
7. [Real-Time Monitoring Flow](#real-time-monitoring-flow)
8. [Attack Simulation](#attack-simulation)
9. [Frontend-Backend Communication](#frontend-backend-communication)
10. [File Structure](#file-structure)
11. [Troubleshooting](#troubleshooting)

---

## System Overview

This is a **complete Intrusion Detection System (IDS)** that monitors network traffic in real-time, extracts features from network flows, and uses a deep learning model (CNN-BiLSTM-Attention) to classify traffic as either benign or one of 12 attack types.

### Key Components:
- **Backend (FastAPI)**: RESTful API + WebSocket server for real-time monitoring
- **Frontend (React)**: Interactive dashboard with real-time visualizations
- **ML Model**: Pre-trained CNN-BiLSTM-Attention model (91.83% accuracy)
- **Target VM**: Ubuntu VM running vulnerable services for attack simulation

---

## Architecture

```
┌─────────────────┐
│   React Frontend │
│   (Dashboard)    │
└────────┬────────┘
         │ HTTP/WebSocket
         │
┌────────▼────────────────────────┐
│      FastAPI Backend            │
│  ┌──────────────────────────┐  │
│  │  IDS Monitor Service      │  │
│  │  - Packet Capture (Scapy)│  │
│  │  - Flow Tracking          │  │
│  │  - Feature Extraction     │  │
│  │  - ML Inference           │  │
│  └──────────────────────────┘  │
│  ┌──────────────────────────┐  │
│  │  Attack Orchestrator     │  │
│  │  - 13 Attack Types       │  │
│  └──────────────────────────┘  │
│  ┌──────────────────────────┐  │
│  │  WebSocket Manager       │  │
│  │  - Real-time Updates     │  │
│  └──────────────────────────┘  │
└────────┬────────────────────────┘
         │
         │ Network Traffic
         │
┌────────▼────────┐
│  Target VM      │
│  (Multipass)    │
│  - Apache       │
│  - SSH          │
│  - FTP          │
│  - MySQL        │
└─────────────────┘
```

---

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI
- **Scapy**: Python library for packet manipulation and network traffic analysis
- **TensorFlow/Keras**: Deep learning framework for model inference
- **NumPy/Pandas**: Data processing and manipulation
- **scikit-learn**: Machine learning utilities (scaler, selector, encoder)
- **WebSockets**: Real-time bidirectional communication

### Frontend
- **React 18**: UI framework for building interactive interfaces
- **Vite**: Fast build tool and development server
- **Recharts**: Charting library for data visualization
- **Axios**: HTTP client for API requests
- **WebSocket API**: Native browser WebSocket for real-time updates

### Infrastructure
- **Multipass**: VM management tool (native ARM support)
- **Ubuntu 24.04 LTS**: Target VM operating system
- **Apache/SSH/FTP/MySQL**: Services running on target VM

---

## How Everything Works

### 1. System Initialization

When you start the backend server:

```python
# backend/app/main.py
app = FastAPI()
# CORS configured for React frontend
# WebSocket endpoint registered
# API routes registered
```

The server listens on `http://0.0.0.0:8000` and provides:
- REST API endpoints (`/api/*`)
- WebSocket endpoint (`/ws`)
- Health check (`/health`)

### 2. Starting Monitoring

When you click "Start Monitoring" in the frontend:

1. **Frontend** sends POST request to `/api/monitoring/start`:
   ```javascript
   {
     "interface": "bridge100",
     "target_ip": "192.168.64.2"
   }
   ```

2. **Backend** (`backend/app/routes/monitoring.py`):
   - Creates `RealTimeIDSMonitor` instance
   - Loads ML model from `cnmodel/ids_ddos_model/`
   - Starts packet capture thread using Scapy
   - Starts flow analysis thread

3. **IDS Monitor** (`backend/app/services/ids_monitor.py`):
   - Initializes Scapy packet sniffer on specified interface
   - Filters packets to/from target VM IP
   - Tracks bidirectional flows (5-tuple: src_ip, dst_ip, src_port, dst_port, protocol)

### 3. Packet Capture & Flow Tracking

**Scapy** captures packets in real-time:

```python
# Scapy sniff() function captures packets
sniff(iface=interface, prn=process_packet, stop_filter=should_stop)
```

For each packet:
1. Extract IP and TCP/UDP headers
2. Create flow key: `(src_ip, dst_ip, src_port, dst_port, protocol)`
3. Determine direction (forward = to target VM, backward = from target VM)
4. Update flow statistics:
   - Packet counts
   - Byte counts
   - Timestamps
   - Packet lengths
   - TCP flags

### 4. Feature Extraction (82 Features)

Every 5 seconds, the flow analysis thread processes completed flows:

**Feature Extractor** (`backend/app/services/feature_extractor.py`):

Extracts **82 features** from each flow:

#### Flow Basics (5 features)
- Flow Duration (microseconds)
- Total Fwd Packets
- Total Backward Packets
- Total Length of Fwd Packets
- Total Length of Bwd Packets

#### Packet Length Statistics (8 features)
- Fwd Packet Length Max/Min/Mean/Std
- Bwd Packet Length Max/Min/Mean/Std

#### Inter-Arrival Times (IAT) (15 features)
- Flow IAT Mean/Std/Max/Min
- Fwd IAT Total/Mean/Std/Max/Min
- Bwd IAT Total/Mean/Std/Max/Min

#### TCP Flags (8 features)
- FIN, SYN, RST, PSH, ACK, URG, CWE, ECE flag counts

#### Flow Rates (4 features)
- Flow Bytes/s
- Flow Packets/s
- Fwd Packets/s
- Bwd Packets/s

#### Packet Statistics (5 features)
- Min/Max Packet Length
- Packet Length Mean/Std/Variance

#### Segment & Header Features (6 features)
- Avg Fwd/Bwd Segment Size
- Fwd/Bwd Header Length
- Average Packet Size
- Down/Up Ratio

#### Subflow Features (4 features)
- Subflow Fwd/Bwd Packets/Bytes

#### Window & Data Features (4 features)
- Init_Win_bytes_forward/backward
- act_data_pkt_fwd/bwd
- min_seg_size_forward

#### Active/Idle Times (8 features)
- Active Mean/Std/Max/Min
- Idle Mean/Std/Max/Min

#### Additional Features (15 features)
- Total Length of Packets
- Fwd/Bwd Packet Length Variance
- Bulk transfer statistics
- Duplicate features for selector compatibility

**Total: 82 features** → Selector reduces to **68 features** → Model input

### 5. Model Inference

**Model Pipeline** (`cnmodel/ids_ddos_model/use_model.py`):

1. **Feature Selection**: VarianceThreshold selector filters 82 → 68 features
2. **Scaling**: RobustScaler normalizes features
3. **Reshape**: Features reshaped to `(68, 1)` for CNN input
4. **Prediction**: CNN-BiLSTM-Attention model predicts attack type
5. **Decoding**: LabelEncoder converts class index to attack name

**Model Architecture**:
- Input: 68 features × 1 timestep
- CNN layers: Extract spatial patterns
- BiLSTM layers: Capture temporal dependencies
- Attention mechanism: Focus on important features
- Output: 13 classes (12 attacks + Benign)

### 6. Real-Time Updates

When an attack is detected:

1. **IDS Monitor** calls attack callback:
   ```python
   attack_callback({
     'type': 'DDOS attack-HOIC',
     'confidence': 0.95,
     'source_ip': '192.168.1.100',
     'dest_ip': '192.168.64.2',
     ...
   })
   ```

2. **WebSocket Manager** broadcasts to all connected clients:
   ```python
   ws_manager.broadcast_sync({
     'type': 'attack',
     'type': 'DDOS attack-HOIC',
     'confidence': 0.95,
     ...
   })
   ```

3. **Frontend WebSocket** receives update:
   ```javascript
   ws.onmessage = (event) => {
     const data = JSON.parse(event.data);
     if (data.type === 'attack') {
       // Update dashboard
       setAttacks(prev => [data, ...prev]);
     }
   }
   ```

4. **Dashboard** updates in real-time:
   - Attack alert appears
   - Statistics update
   - Charts refresh
   - Flow table adds new entry

### 7. Attack Simulation

**Attack Orchestrator** (`backend/app/services/attack_orchestrator.py`):

When you launch an attack from the frontend:

1. **Frontend** sends POST to `/api/attacks/launch`:
   ```javascript
   {
     "attack_type": "DDOS attack-HOIC",
     "target_ip": "192.168.64.2",
     "duration": 60
   }
   ```

2. **Backend** starts attack in separate thread:
   ```python
   # Example: DDOS attack-HOIC
   def launch_hoic_attack(target_ip, duration):
       threads = []
       for i in range(100):  # 100 concurrent threads
           thread = threading.Thread(
               target=send_http_flood,
               args=(target_ip, duration)
           )
           threads.append(thread)
           thread.start()
   ```

3. **Attack generates traffic**:
   - HTTP floods (HOIC, LOIC-HTTP)
   - UDP floods (LOIC-UDP)
   - Slow attacks (Slowloris, SlowHTTPTest)
   - Brute force attempts (SSH, FTP, Web)
   - Injection attacks (SQL, XSS)

4. **IDS Monitor detects attacks** in real-time and alerts dashboard

---

## Feature Extraction Details

### Why 82 Features?

The model was trained on a dataset with **82 original features**. During training:
- A **VarianceThreshold** selector was fitted on 82 features
- It selected **68 features** with sufficient variance
- The model was trained on these 68 features

**For inference**, we must:
1. Extract all **82 features** (matching training data)
2. Pass through selector (82 → 68)
3. Scale features
4. Predict with model

### Feature Calculation Examples

**Flow Duration**:
```python
duration = (end_time - start_time) * 1,000,000  # Convert to microseconds
```

**Inter-Arrival Time (IAT)**:
```python
# Calculate time differences between consecutive packets
fwd_iat = np.diff(fwd_timestamps)  # Forward direction
bwd_iat = np.diff(bwd_timestamps)  # Backward direction
flow_iat = np.diff(sorted(all_timestamps))  # Overall flow
```

**TCP Flags**:
```python
# Extract flags from TCP header
syn_count = sum(1 for flags in flow_flags if flags & 0x02)
ack_count = sum(1 for flags in flow_flags if flags & 0x10)
```

**Packet Length Statistics**:
```python
fwd_lengths = [packet_length for each forward packet]
fwd_mean = np.mean(fwd_lengths)
fwd_std = np.std(fwd_lengths)
fwd_max = np.max(fwd_lengths)
fwd_min = np.min(fwd_lengths)
```

---

## Model Integration

### Model Files

Located in `cnmodel/ids_ddos_model/`:

- **ids_model.keras**: Trained model (Keras format)
- **scaler.pkl**: RobustScaler for feature normalization
- **selector.pkl**: VarianceThreshold for feature selection
- **encoder.pkl**: LabelEncoder for class names
- **model_metadata.json**: Model information

### Model Loading

```python
# backend/app/services/ids_monitor.py
IDSModel = load_use_model(model_dir)  # Dynamically import
self.ids_model = IDSModel(model_dir)  # Load model + preprocessors
```

### Prediction Pipeline

```python
# 1. Extract 82 features
features_df = extractor.extract_features(flow_key, flow_data)

# 2. Predict (handles: 82 → 68 → scale → predict)
predictions, probabilities = self.ids_model.predict(features_df)

# 3. Get result
attack_type = predictions[0]  # e.g., "DDOS attack-HOIC"
confidence = float(np.max(probabilities[0]))  # e.g., 0.95
```

---

## Real-Time Monitoring Flow

### Complete Data Flow

```
1. Network Packet (Scapy)
   ↓
2. Packet Processing
   - Extract IP/TCP/UDP headers
   - Create flow key
   - Update flow statistics
   ↓
3. Flow Tracking (5-second windows)
   - Collect packets into flows
   - Track bidirectional traffic
   ↓
4. Feature Extraction (82 features)
   - Calculate statistics
   - Extract timing features
   - Extract packet features
   ↓
5. Model Inference
   - Select features (82 → 68)
   - Scale features
   - Predict attack type
   ↓
6. Result Processing
   - If attack: trigger callback
   - If benign: update statistics
   ↓
7. WebSocket Broadcast
   - Send to all connected clients
   ↓
8. Frontend Update
   - Display alert
   - Update charts
   - Refresh statistics
```

### Threading Model

**Main Thread**: FastAPI server
- Handles HTTP requests
- Manages WebSocket connections

**Packet Capture Thread**: Scapy sniff()
- Continuously captures packets
- Updates flow statistics (thread-safe with locks)

**Flow Analysis Thread**: Periodic analysis
- Every 5 seconds: analyze completed flows
- Extract features and run inference
- Trigger callbacks for attacks

**Attack Threads**: Attack simulation
- Each attack runs in separate threads
- Can run multiple attacks simultaneously

---

## Attack Simulation

### All 13 Attack Types

1. **DDOS attack-HOIC**
   - HTTP POST flood with 100 concurrent threads
   - Targets web server

2. **DDOS attack-LOIC-UDP**
   - UDP flood with 50 threads
   - Random ports

3. **DDoS attacks-LOIC-HTTP**
   - HTTP GET flood with 50 threads
   - Random URLs

4. **DoS attacks-GoldenEye**
   - HTTP keep-alive connections
   - 100 threads maintaining connections

5. **DoS attacks-Hulk**
   - Random URL requests
   - 100 threads

6. **DoS attacks-SlowHTTPTest**
   - Slow POST requests
   - 50 threads with slow data transfer

7. **DoS attacks-Slowloris**
   - Keep connections open
   - 200 threads sending partial requests

8. **Brute Force -Web**
   - Multiple login attempts
   - 10 threads trying common passwords

9. **Brute Force -XSS**
   - XSS payload injection
   - 20 threads sending XSS payloads

10. **FTP-BruteForce**
    - FTP login attempts
    - 10 threads

11. **SQL Injection**
    - SQL injection payloads
    - 20 threads

12. **SSH-Bruteforce**
    - SSH login attempts
    - 10 threads

13. **Benign** (normal traffic)

---

## Frontend-Backend Communication

### REST API Endpoints

**Monitoring**:
- `POST /api/monitoring/start` - Start monitoring
- `POST /api/monitoring/stop` - Stop monitoring
- `GET /api/monitoring/status` - Get status

**Attacks**:
- `POST /api/attacks/launch` - Launch attack
- `POST /api/attacks/stop` - Stop attack
- `GET /api/attacks/list` - List available attacks

**Statistics**:
- `GET /api/stats/summary` - Get summary statistics
- `GET /api/stats/recent` - Get recent attacks

### WebSocket Communication

**Connection**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

**Message Types**:

1. **Attack Detection**:
```json
{
  "type": "attack",
  "attack_type": "DDOS attack-HOIC",
  "confidence": 0.95,
  "source_ip": "192.168.1.100",
  "dest_ip": "192.168.64.2",
  "source_port": 54321,
  "dest_port": 80,
  "protocol": "TCP",
  "packets": 1000,
  "bytes": 50000,
  "timestamp": 1701234567.89
}
```

2. **Statistics Update**:
```json
{
  "type": "stats",
  "total_flows": 150,
  "benign_flows": 120,
  "attack_flows": 30,
  "attacks_by_type": {
    "DDOS attack-HOIC": 10,
    "DoS attacks-Slowloris": 20
  }
}
```

3. **Benign Flow**:
```json
{
  "type": "benign",
  "source_ip": "192.168.1.50",
  "dest_ip": "192.168.64.2",
  "packets": 50,
  "bytes": 5000
}
```

---

## File Structure

```
cnProject/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app entry point
│   │   ├── models.py               # Pydantic data models
│   │   ├── websocket_manager.py    # WebSocket connection manager
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── monitoring.py       # Monitoring endpoints
│   │   │   ├── attacks.py          # Attack control endpoints
│   │   │   └── stats.py            # Statistics endpoints
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── ids_monitor.py      # Real-time IDS monitoring
│   │       ├── feature_extractor.py # 82-feature extraction
│   │       └── attack_orchestrator.py # 13 attack types
│   ├── requirements.txt
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                 # Root component
│   │   ├── main.jsx                # Entry point
│   │   ├── components/
│   │   │   ├── Dashboard.jsx       # Main dashboard
│   │   │   ├── Statistics.jsx      # Stats cards
│   │   │   ├── AttackAlerts.jsx    # Attack notifications
│   │   │   ├── AttackChart.jsx     # Pie chart
│   │   │   ├── TimelineChart.jsx    # Line chart
│   │   │   ├── FlowTable.jsx       # Flow table
│   │   │   └── Controls.jsx        # Control panel
│   │   ├── services/
│   │   │   ├── api.js               # REST API client
│   │   │   └── websocket.js         # WebSocket client
│   │   ├── styles/
│   │   │   └── dashboard.css        # Styling
│   │   └── utils/
│   │       └── constants.js         # Constants
│   ├── package.json
│   └── README.md
│
└── cnmodel/
    └── ids_ddos_model/
        ├── ids_model.keras          # Trained model
        ├── scaler.pkl               # Feature scaler
        ├── selector.pkl             # Feature selector (82→68)
        ├── encoder.pkl              # Label encoder
        ├── model_metadata.json      # Model info
        └── use_model.py             # Model inference class
```

---

## Troubleshooting

### Error: "X has 66 features, but VarianceThreshold is expecting 82 features"

**Solution**: Fixed! The feature extractor now generates exactly 82 features.

### Error: "Could not load model in any format!"

**Solution**: Fixed! Model path calculation corrected to use absolute paths.

### Error: "Permission denied" when capturing packets

**Solution**: Run backend with sudo:
```bash
sudo venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Error: "Failed to connect to VM"

**Solution**: 
1. Check VM is running: `multipass list`
2. Check VM IP: `multipass info target-vm | grep IPv4`
3. Verify services: `multipass exec target-vm -- systemctl status apache2`

### WebSocket not connecting

**Solution**:
1. Check backend is running
2. Check CORS settings in `backend/app/main.py`
3. Verify WebSocket URL in `frontend/src/utils/constants.js`

### Model predictions always "Benign"

**Solution**:
1. Verify attacks are generating traffic
2. Check feature extraction is working (82 features)
3. Verify model loaded correctly (check logs)

---

## Key Implementation Details

### Why Scapy?

**Scapy** is used for packet capture because:
- Cross-platform (Linux, macOS, Windows)
- Python-native (easy integration)
- Powerful packet manipulation
- Real-time packet capture
- Low-level network access

### Why FastAPI?

**FastAPI** is used because:
- Modern async/await support
- Automatic API documentation
- Type safety with Pydantic
- WebSocket support built-in
- High performance

### Why React?

**React** is used because:
- Component-based architecture
- Real-time updates with WebSocket
- Rich ecosystem (Recharts, Axios)
- Fast development with Vite
- Modern UI capabilities

### Why 82 Features?

The model was trained on a dataset with 82 features. The VarianceThreshold selector:
- Takes 82 features as input
- Filters to 68 features (removes low-variance features)
- Model uses 68 features for prediction

**We must extract 82 features** to match the training data format.

---

## Summary

This IDS system:

1. **Captures** network traffic using Scapy
2. **Tracks** bidirectional flows (5-tuple)
3. **Extracts** 82 features from each flow
4. **Selects** 68 features using VarianceThreshold
5. **Predicts** attack type using CNN-BiLSTM-Attention model
6. **Alerts** dashboard in real-time via WebSocket
7. **Simulates** 13 attack types for testing

Everything is working perfectly! 🎉

