"""Flow aggregator - groups packets into network flows"""

import time
import logging
from typing import Dict, Optional, Tuple, List
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Flow:
    """Represents a network flow"""
    flow_id: str
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    
    # Flow statistics
    start_time: float = 0.0
    last_seen: float = 0.0
    duration: float = 0.0
    
    # Packet counts
    fwd_packets: int = 0
    bwd_packets: int = 0
    total_packets: int = 0
    
    # Byte counts
    fwd_bytes: int = 0
    bwd_bytes: int = 0
    total_bytes: int = 0
    
    # Packet lengths
    packet_lengths: List[int] = field(default_factory=list)
    fwd_packet_lengths: List[int] = field(default_factory=list)
    bwd_packet_lengths: List[int] = field(default_factory=list)
    
    # Inter-arrival times
    packet_times: List[float] = field(default_factory=list)
    fwd_iat: List[float] = field(default_factory=list)
    bwd_iat: List[float] = field(default_factory=list)
    
    # TCP flags
    syn_count: int = 0
    ack_count: int = 0
    fin_count: int = 0
    rst_count: int = 0
    psh_count: int = 0
    urg_count: int = 0
    
    # Additional metadata
    completed: bool = False
    
    def add_packet(self, packet_info: Dict, is_forward: bool):
        """Add a packet to this flow"""
        current_time = time.time()
        
        if self.start_time == 0:
            self.start_time = current_time
        
        # Update timing
        if self.packet_times:
            iat = current_time - self.last_seen
            if is_forward:
                self.fwd_iat.append(iat)
            else:
                self.bwd_iat.append(iat)
        
        self.last_seen = current_time
        self.packet_times.append(current_time)
        
        # Update packet counts
        self.total_packets += 1
        if is_forward:
            self.fwd_packets += 1
        else:
            self.bwd_packets += 1
        
        # Update byte counts
        pkt_len = packet_info.get('length', 0)
        self.total_bytes += pkt_len
        self.packet_lengths.append(pkt_len)
        
        if is_forward:
            self.fwd_bytes += pkt_len
            self.fwd_packet_lengths.append(pkt_len)
        else:
            self.bwd_bytes += pkt_len
            self.bwd_packet_lengths.append(pkt_len)
        
        # Update TCP flags
        flags = packet_info.get('flags', {})
        if flags.get('S'):
            self.syn_count += 1
        if flags.get('A'):
            self.ack_count += 1
        if flags.get('F'):
            self.fin_count += 1
        if flags.get('R'):
            self.rst_count += 1
        if flags.get('P'):
            self.psh_count += 1
        if flags.get('U'):
            self.urg_count += 1
    
    def finalize(self):
        """Finalize flow statistics"""
        if self.start_time > 0 and self.last_seen > 0:
            self.duration = self.last_seen - self.start_time
        self.completed = True


class FlowAggregator:
    """Aggregates packets into flows"""
    
    def __init__(self, flow_timeout: int = 60, max_flows: int = 10000):
        self.flow_timeout = flow_timeout
        self.max_flows = max_flows
        self.flows: Dict[str, Flow] = {}
        self.completed_flows: List[Flow] = []
        self.flow_count = 0
        self._cleanup_interval = 0.5  # Cleanup every 0.5 seconds (VERY aggressive)
        self._last_cleanup_time = time.time()
        
    def _get_flow_key(self, packet_info: Dict) -> Tuple[str, bool]:
        """
        Generate flow key from packet
        Returns (flow_id, is_forward)
        """
        src_ip = packet_info.get('src_ip', '')
        dst_ip = packet_info.get('dst_ip', '')
        src_port = packet_info.get('src_port', 0)
        dst_port = packet_info.get('dst_port', 0)
        protocol = packet_info.get('protocol', 'unknown')
        
        # Create bidirectional flow key (sorted by IP)
        if src_ip < dst_ip or (src_ip == dst_ip and src_port < dst_port):
            flow_id = f"{src_ip}:{src_port}-{dst_ip}:{dst_port}-{protocol}"
            is_forward = True
        else:
            flow_id = f"{dst_ip}:{dst_port}-{src_ip}:{src_port}-{protocol}"
            is_forward = False
        
        return flow_id, is_forward
    
    def add_packet(self, packet_info: Dict) -> Optional[Flow]:
        """
        Add packet to flow aggregator
        Returns completed flow if any
        """
        # Periodically cleanup old flows
        current_time = time.time()
        if current_time - self._last_cleanup_time > self._cleanup_interval:
            self._cleanup_old_flows()
            self._last_cleanup_time = current_time
        
        flow_id, is_forward = self._get_flow_key(packet_info)
        
        # Get or create flow
        if flow_id not in self.flows:
            if len(self.flows) >= self.max_flows:
                # Remove oldest flow
                self._cleanup_old_flows(force=True)
            
            # Create new flow
            if is_forward:
                src_ip = packet_info.get('src_ip', '')
                dst_ip = packet_info.get('dst_ip', '')
                src_port = packet_info.get('src_port', 0)
                dst_port = packet_info.get('dst_port', 0)
            else:
                dst_ip = packet_info.get('src_ip', '')
                src_ip = packet_info.get('dst_ip', '')
                dst_port = packet_info.get('src_port', 0)
                src_port = packet_info.get('dst_port', 0)
            
            self.flows[flow_id] = Flow(
                flow_id=flow_id,
                src_ip=src_ip,
                dst_ip=dst_ip,
                src_port=src_port,
                dst_port=dst_port,
                protocol=packet_info.get('protocol', 'unknown')
            )
            self.flow_count += 1
        
        # Add packet to flow
        flow = self.flows[flow_id]
        flow.add_packet(packet_info, is_forward)
        
        # Check if flow is completed (FIN or RST flag)
        flags = packet_info.get('flags', {})
        if flags.get('F') or flags.get('R'):
            flow.finalize()
            completed = self.flows.pop(flow_id)
            self.completed_flows.append(completed)
            logger.debug(f"Flow {flow_id} completed (FIN/RST)")
            return completed
        
        # Also complete flows that have enough packets for analysis (helps with attack detection)
        current_time = time.time()
        if flow.total_packets >= 10 and current_time - flow.start_time >= 0.5:  # 10 packets and 0.5 seconds old
            flow.finalize()
            completed = self.flows.pop(flow_id)
            self.completed_flows.append(completed)
            logger.debug(f"Flow {flow_id} completed (packet threshold)")
            return completed
        
        # VERY AGGRESSIVE CLEANUP: Complete flows that are old enough (prevents accumulation)
        if current_time - flow.start_time >= 1.5:  # Any flow older than 1.5 seconds
            flow.finalize()
            completed = self.flows.pop(flow_id)
            self.completed_flows.append(completed)
            logger.debug(f"Flow {flow_id} completed (age threshold)")
            return completed
        
        return None
    
    def _cleanup_old_flows(self, force: bool = False):
        """Remove old flows that have timed out"""
        current_time = time.time()
        
        to_remove = []
        if force:
            # Force remove OLDEST flows (when max_flows is reached)
            # Sort by last_seen time and remove oldest 50%
            flows_by_age = sorted(self.flows.items(), key=lambda x: x[1].last_seen)
            num_to_remove = max(1, len(flows_by_age) // 2)  # Remove oldest 50%
            to_remove = [flow_id for flow_id, _ in flows_by_age[:num_to_remove]]
            if to_remove:
                logger.info(f"Force cleanup: removing {len(to_remove)} oldest flows")
        else:
            # Normal cleanup: remove flows older than timeout
            for flow_id, flow in list(self.flows.items()):  # Use list() to avoid dict size change during iteration
                if current_time - flow.last_seen > self.flow_timeout:
                    to_remove.append(flow_id)
        
        for flow_id in to_remove:
            if flow_id in self.flows:  # Check if still exists
                flow = self.flows.pop(flow_id)
                flow.finalize()
                self.completed_flows.append(flow)
                logger.debug(f"Flow {flow_id} cleaned up")
    
    def get_completed_flows(self, limit: Optional[int] = None) -> List[Flow]:
        """Get completed flows and clear the buffer"""
        # First cleanup old flows
        self._cleanup_old_flows()
        
        # Return completed flows
        if limit:
            flows = self.completed_flows[:limit]
            self.completed_flows = self.completed_flows[limit:]
        else:
            flows = self.completed_flows
            self.completed_flows = []
        
        return flows
    
    def get_active_flow_count(self) -> int:
        """Get number of active flows"""
        return len(self.flows)
    
    def get_total_flow_count(self) -> int:
        """Get total number of flows processed"""
        return self.flow_count
    
    def clear(self):
        """Clear all flows"""
        self.flows.clear()
        self.completed_flows.clear()

