"""
Pydantic models for the IDS monitoring system
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime


class AttackDetection(BaseModel):
    """Model for attack detection event"""
    type: str = Field(..., description="Attack type classification")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    source_ip: str = Field(..., description="Source IP address")
    dest_ip: str = Field(..., description="Destination IP address")
    source_port: int = Field(..., description="Source port")
    dest_port: int = Field(..., description="Destination port")
    protocol: str = Field(..., description="Protocol (TCP/UDP)")
    packets: int = Field(..., description="Number of packets in flow")
    bytes: int = Field(..., description="Total bytes in flow")
    timestamp: float = Field(..., description="Unix timestamp")


class FlowStatistics(BaseModel):
    """Model for flow statistics"""
    total_flows: int = Field(default=0, description="Total number of flows")
    benign_flows: int = Field(default=0, description="Number of benign flows")
    attack_flows: int = Field(default=0, description="Number of attack flows")
    attacks_by_type: Dict[str, int] = Field(default_factory=dict, description="Attack count by type")
    detection_rate: float = Field(default=0.0, description="Attack detection rate percentage")


class MonitoringStatus(BaseModel):
    """Model for monitoring status"""
    is_running: bool = Field(..., description="Whether monitoring is active")
    interface: Optional[str] = Field(None, description="Network interface being monitored")
    target_ip: Optional[str] = Field(None, description="Target VM IP address")
    start_time: Optional[float] = Field(None, description="Monitoring start time")


class AttackRequest(BaseModel):
    """Model for attack launch request"""
    attack_type: str = Field(..., description="Type of attack to launch")
    duration: int = Field(default=60, ge=1, le=300, description="Attack duration in seconds")
    target_ip: str = Field(..., description="Target IP address")
    intensity: Optional[int] = Field(default=50, ge=1, le=100, description="Attack intensity (1-100)")


class AttackListResponse(BaseModel):
    """Model for available attacks list"""
    attacks: List[str] = Field(..., description="List of available attack types")


class HealthResponse(BaseModel):
    """Model for health check response"""
    status: str = Field(..., description="Service status")
    timestamp: float = Field(..., description="Current timestamp")
    model_loaded: bool = Field(..., description="Whether ML model is loaded")


class RecentAttacksResponse(BaseModel):
    """Model for recent attacks response"""
    attacks: List[AttackDetection] = Field(..., description="List of recent attacks")
    count: int = Field(..., description="Number of attacks")

