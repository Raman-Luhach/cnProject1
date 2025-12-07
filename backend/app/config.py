"""Configuration for IDS Monitoring System"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
PROJECT_ROOT = BASE_DIR.parent
MODEL_DIR = PROJECT_ROOT / "cnmodel" / "ids_ddos_model"

# VM Configuration
VM_NAME = "ids_target"  # Existing VM name
DEFAULT_VM_IP = "192.168.64.3"  # Existing VM IP (will be used as fallback)
VM_IP = DEFAULT_VM_IP  # Alias for backwards compatibility
VM_CPUS = 2
VM_MEMORY = "2G"
VM_DISK = "10G"

# Network Configuration
FLOW_TIMEOUT = 2  # seconds (VERY aggressive for continuous detection)
PACKET_BUFFER_SIZE = 1000
MAX_FLOWS = 1000  # Reduced to force more frequent cleanup

# Detection Configuration
DETECTION_CONFIDENCE_THRESHOLD = 0.15  # Lowered to detect suspicious behavior (was 0.5, original 0.7)
BATCH_SIZE = 32  # for model inference
DETECTION_INTERVAL = 1  # seconds (for flow processing)
LOG_ALL_PREDICTIONS = True  # Log predictions for all flows, not just attacks

# WebSocket Configuration
WEBSOCKET_PORT = 8000
WEBSOCKET_HOST = "0.0.0.0"

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite default port
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

# Attack Configuration
ATTACK_TOOLS_DIR = BASE_DIR / "tools"
ATTACK_LOG_DIR = BASE_DIR / "logs" / "attacks"
ATTACK_LOG_DIR.mkdir(parents=True, exist_ok=True)

# Capture Configuration
CAPTURE_LOG_DIR = BASE_DIR / "logs" / "capture"
CAPTURE_LOG_DIR.mkdir(parents=True, exist_ok=True)
PCAP_SAVE_DIR = BASE_DIR / "pcaps"
PCAP_SAVE_DIR.mkdir(parents=True, exist_ok=True)

# Feature extraction
FEATURE_COUNT = 82  # CIC-IDS2018 features before selection
SELECTED_FEATURE_COUNT = 68  # After VarianceThreshold

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Model paths
MODEL_KERAS_PATH = MODEL_DIR / "ids_model.keras"
MODEL_H5_PATH = MODEL_DIR / "ids_model.h5"
MODEL_SAVEDMODEL_PATH = MODEL_DIR / "ids_model_savedmodel"
SCALER_PATH = MODEL_DIR / "scaler.pkl"
ENCODER_PATH = MODEL_DIR / "encoder.pkl"
SELECTOR_PATH = MODEL_DIR / "selector.pkl"
METADATA_PATH = MODEL_DIR / "model_metadata.json"

# Attack class names (must match model training)
ATTACK_CLASSES = [
    "Benign",
    "Brute Force -Web",
    "Brute Force -XSS",
    "DDOS attack-HOIC",
    "DDOS attack-LOIC-UDP",
    "DDoS attacks-LOIC-HTTP",
    "DoS attacks-GoldenEye",
    "DoS attacks-Hulk",
    "DoS attacks-SlowHTTPTest",
    "DoS attacks-Slowloris",
    "FTP-BruteForce",
    "SQL Injection",
    "SSH-Bruteforce"
]

# VM Services to install
VM_SERVICES = {
    "apache2": {"port": 80, "install_cmd": "apt-get install -y apache2"},
    "ssh": {"port": 22, "install_cmd": "apt-get install -y openssh-server"},
    "ftp": {"port": 21, "install_cmd": "apt-get install -y vsftpd"},
    "mysql": {"port": 3306, "install_cmd": "apt-get install -y mysql-server"}
}

