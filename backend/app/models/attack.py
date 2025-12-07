"""Attack request and response models"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AttackType(str, Enum):
    """Available attack types"""
    DDOS_HOIC = "DDOS attack-HOIC"
    DDOS_LOIC_UDP = "DDOS attack-LOIC-UDP"
    DDOS_LOIC_HTTP = "DDoS attacks-LOIC-HTTP"
    DOS_GOLDENEYE = "DoS attacks-GoldenEye"
    DOS_HULK = "DoS attacks-Hulk"
    DOS_SLOWHTTPTEST = "DoS attacks-SlowHTTPTest"
    DOS_SLOWLORIS = "DoS attacks-Slowloris"
    BRUTE_FORCE_WEB = "Brute Force -Web"
    BRUTE_FORCE_XSS = "Brute Force -XSS"
    FTP_BRUTEFORCE = "FTP-BruteForce"
    SSH_BRUTEFORCE = "SSH-Bruteforce"
    SQL_INJECTION = "SQL Injection"


class AttackRequest(BaseModel):
    """Request to start an attack"""
    attack_type: AttackType
    target_ip: str
    target_port: Optional[int] = None
    duration: Optional[int] = None  # seconds
    intensity: Optional[str] = "medium"  # low, medium, high
    parameters: Optional[Dict[str, Any]] = {}


class AttackStatus(str, Enum):
    """Attack status"""
    IDLE = "idle"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


class AttackResponse(BaseModel):
    """Response for attack operations"""
    attack_id: str
    attack_type: str
    status: AttackStatus
    target_ip: str
    target_port: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    packets_sent: int = 0
    error_message: Optional[str] = None


class AttackListItem(BaseModel):
    """Attack type list item"""
    name: str
    display_name: str
    description: str
    default_port: Optional[int] = None

