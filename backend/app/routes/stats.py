"""
Statistics endpoints for IDS monitoring data
"""
from fastapi import APIRouter
from app.models import FlowStatistics, RecentAttacksResponse, AttackDetection
from typing import List

router = APIRouter()

# Global statistics (will be updated by monitoring service)
global_stats = {
    "total_flows": 0,
    "benign_flows": 0,
    "attack_flows": 0,
    "attacks_by_type": {},
    "detection_rate": 0.0
}

# Recent attacks buffer
recent_attacks: List[AttackDetection] = []


@router.get("/summary", response_model=FlowStatistics)
async def get_statistics_summary():
    """Get overall statistics summary"""
    return FlowStatistics(**global_stats)


@router.get("/recent", response_model=RecentAttacksResponse)
async def get_recent_attacks(limit: int = 50):
    """Get recent attack detections"""
    attacks_slice = recent_attacks[:limit] if len(recent_attacks) > limit else recent_attacks
    return RecentAttacksResponse(
        attacks=attacks_slice,
        count=len(attacks_slice)
    )

