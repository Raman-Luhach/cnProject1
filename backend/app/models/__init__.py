"""Pydantic models for API requests and responses"""

from .detection import DetectionResult, DetectionEvent
from .attack import AttackRequest, AttackResponse, AttackStatus
from .vm import VMStatus, VMInfo

__all__ = [
    'DetectionResult',
    'DetectionEvent',
    'AttackRequest',
    'AttackResponse',
    'AttackStatus',
    'VMStatus',
    'VMInfo'
]

