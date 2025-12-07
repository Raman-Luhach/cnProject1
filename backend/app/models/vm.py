"""VM status and info models"""

from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class VMState(str, Enum):
    """VM state"""
    RUNNING = "running"
    STOPPED = "stopped"
    STARTING = "starting"
    STOPPING = "stopping"
    DELETED = "deleted"
    UNKNOWN = "unknown"


class VMServiceStatus(BaseModel):
    """Status of a service on the VM"""
    name: str
    port: int
    running: bool
    installed: bool


class VMInfo(BaseModel):
    """VM information"""
    name: str
    state: VMState
    ipv4: Optional[str] = None
    ipv6: Optional[str] = None
    cpus: int
    memory: str
    disk: str
    services: List[VMServiceStatus] = []
    created_at: Optional[datetime] = None


class VMStatus(BaseModel):
    """VM status response"""
    exists: bool
    vm_info: Optional[VMInfo] = None
    message: str


class VMCreateRequest(BaseModel):
    """Request to create a VM"""
    name: Optional[str] = "ids_target"
    cpus: Optional[int] = 2
    memory: Optional[str] = "2G"
    disk: Optional[str] = "10G"
    install_services: bool = True


class VMCreateResponse(BaseModel):
    """Response after VM creation"""
    success: bool
    vm_info: Optional[VMInfo] = None
    message: str
    setup_log: List[str] = []

