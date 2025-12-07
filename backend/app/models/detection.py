"""Detection result models"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class DetectionResult(BaseModel):
    """Single detection result"""
    flow_id: str
    timestamp: datetime
    prediction: str
    confidence: float
    probabilities: List[float]
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    packet_count: int
    byte_count: int
    duration: float
    is_attack: bool


class DetectionEvent(BaseModel):
    """WebSocket detection event"""
    event_type: str = "detection"
    detection: DetectionResult
    total_detections: int
    attack_detections: int


class DetectionStats(BaseModel):
    """Detection statistics"""
    total_flows: int
    total_detections: int
    benign_count: int
    attack_count: int
    detection_rate: float
    attack_distribution: dict
    start_time: Optional[datetime] = None
    uptime_seconds: float

