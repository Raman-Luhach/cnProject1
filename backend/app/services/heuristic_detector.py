"""Heuristic-based attack detection (rule-based)"""

import logging
from typing import Tuple, Optional
from .capture.flow_aggregator import Flow

logger = logging.getLogger(__name__)


def detect_attack_heuristic(flow: Flow) -> Tuple[bool, Optional[str], float, Optional[str]]:
    """
    Heuristic-based attack detection using simple rules
    
    Returns: (is_attack, attack_type, confidence, reason)
    """
    
    # Skip if flow is too short
    if flow.total_packets < 10 or flow.duration <= 0:
        return False, None, 0.0, None
    
    # EXCLUDE KNOWN LEGITIMATE SERVICES
    # SSH (port 22) - normal terminal traffic has many small packets
    if flow.dst_port == 22 or flow.src_port == 22:
        return False, None, 0.0, None  # Skip SSH traffic
    
    # DNS (port 53) - normal DNS queries
    if flow.dst_port == 53 or flow.src_port == 53:
        return False, None, 0.0, None
    
    # Calculate rates and metrics
    pkt_rate = flow.total_packets / flow.duration
    byte_rate = flow.total_bytes / flow.duration
    avg_pkt_size = flow.total_bytes / flow.total_packets
    
    # SYN Flood detection
    # Characteristics: Many SYN packets, few ACKs, high packet rate
    if flow.syn_count > 10:
        syn_ack_ratio = flow.syn_count / max(flow.ack_count, 1)
        if syn_ack_ratio > 2.0:  # More than 2x SYN vs ACK
            confidence = min(0.95, 0.60 + (syn_ack_ratio * 0.1))
            return True, "SYN Flood", confidence, f"Excessive SYN packets ({flow.syn_count}) with few ACKs ({flow.ack_count})"
    
    # HTTP Flood detection (MORE AGGRESSIVE)
    # Characteristics: Port 80/443, high packet rate OR many packets, small packets
    if flow.dst_port in [80, 443, 8080, 8000]:
        # Lower thresholds for better detection
        if pkt_rate > 15 and avg_pkt_size < 400:  # Lowered from 30/300
            confidence = min(0.90, 0.55 + (pkt_rate / 150))
            return True, "HTTP Flood", confidence, f"High packet rate ({pkt_rate:.0f} pkt/s) to HTTP port with small packets"
        # Also detect by total packet count (even if slow)
        if flow.total_packets > 50 and avg_pkt_size < 400:
            confidence = min(0.85, 0.50 + (flow.total_packets / 500))
            return True, "HTTP Flood", confidence, f"Many HTTP requests ({flow.total_packets} packets) with small packet size"
    
    # High-rate DoS detection (LOWERED THRESHOLD)
    # Characteristics: High packet rate
    if pkt_rate > 50:  # Lowered from 100
        confidence = min(0.95, 0.55 + (pkt_rate / 300))
        return True, "High-rate DoS", confidence, f"High packet rate: {pkt_rate:.0f} pkt/s"
    
    # Asymmetric flow detection (common in DoS attacks)
    # Characteristics: Much more forward than backward traffic
    if flow.fwd_packets > 20 and flow.bwd_packets > 0:
        ratio = flow.fwd_packets / flow.bwd_packets
        if ratio > 15:  # 15:1 forward/backward ratio
            confidence = min(0.85, 0.45 + (ratio / 50))
            return True, "Asymmetric DoS", confidence, f"Asymmetric traffic: {ratio:.0f}:1 forward/backward ratio"
    
    # Small packet flood (potential DoS) - LOWER THRESHOLD
    # Characteristics: Many small packets
    if pkt_rate > 25 and avg_pkt_size < 150:  # Lowered from 50/100
        confidence = min(0.85, 0.50 + (pkt_rate / 150))
        return True, "Small Packet Flood", confidence, f"High rate ({pkt_rate:.0f} pkt/s) of small packets (avg {avg_pkt_size:.0f} bytes)"
    
    # Also detect many small packets even if not super fast
    if flow.total_packets > 40 and avg_pkt_size < 150:
        confidence = min(0.80, 0.48 + (flow.total_packets / 400))
        return True, "Packet Flood", confidence, f"Many small packets ({flow.total_packets} packets, avg {avg_pkt_size:.0f} bytes)"
    
    # UDP Flood detection
    # Characteristics: UDP protocol, high packet rate
    if flow.protocol == "UDP" and pkt_rate > 50:
        confidence = min(0.90, 0.55 + (pkt_rate / 200))
        return True, "UDP Flood", confidence, f"High UDP packet rate: {pkt_rate:.0f} pkt/s"
    
    # Suspicious HTTP behavior (possible application-layer attack)
    if flow.dst_port in [80, 443]:
        # Many requests, little response
        if flow.fwd_packets > 50 and flow.bwd_packets < 10:
            confidence = 0.65
            return True, "Suspicious HTTP Activity", confidence, "Many HTTP requests with minimal responses"
    
    return False, None, 0.0, None

