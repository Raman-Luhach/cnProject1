"""
Feature Extraction Service - Extract 82 features from network flows
Note: Selector expects 82 features and reduces to 68 for model input
"""
import numpy as np
import pandas as pd
from collections import defaultdict
import time


class NetworkFlowFeatureExtractor:
    """Extract features from network flows for IDS model"""
    
    def __init__(self):
        self.flow_stats = defaultdict(lambda: {
            'fwd_packets': [],
            'bwd_packets': [],
            'fwd_bytes': 0,
            'bwd_bytes': 0,
            'fwd_timestamps': [],
            'bwd_timestamps': [],
            'fwd_packet_lengths': [],
            'bwd_packet_lengths': [],
            'flags': [],
            'start_time': None,
            'end_time': None
        })
    
    def update_flow(self, flow_key, packet, packet_len, direction='fwd', flags=None):
        """Update flow statistics with packet"""
        flow = self.flow_stats[flow_key]
        
        if flow['start_time'] is None:
            flow['start_time'] = time.time()
        
        flow['end_time'] = time.time()
        
        if direction == 'fwd':
            flow['fwd_packets'].append(packet)
            flow['fwd_bytes'] += packet_len
            flow['fwd_timestamps'].append(time.time())
            flow['fwd_packet_lengths'].append(packet_len)
        else:
            flow['bwd_packets'].append(packet)
            flow['bwd_bytes'] += packet_len
            flow['bwd_timestamps'].append(time.time())
            flow['bwd_packet_lengths'].append(packet_len)
        
        if flags is not None:
            flow['flags'].append(flags)
    
    def extract_features(self, flow_key, flow_data):
        """Extract all 82 features from flow data (selector expects 82, outputs 68)"""
        if flow_data['start_time'] is None:
            return None
        
        # Calculate duration
        duration = (flow_data['end_time'] - flow_data['start_time']) or 0.001
        
        # Forward packets
        fwd_packets = flow_data['fwd_packets']
        fwd_bytes = flow_data['fwd_bytes']
        fwd_count = len(fwd_packets)
        fwd_lengths = flow_data['fwd_packet_lengths'] if flow_data['fwd_packet_lengths'] else [0]
        
        # Backward packets
        bwd_packets = flow_data['bwd_packets']
        bwd_bytes = flow_data['bwd_bytes']
        bwd_count = len(bwd_packets)
        bwd_lengths = flow_data['bwd_packet_lengths'] if flow_data['bwd_packet_lengths'] else [0]
        
        # Total
        total_packets = fwd_count + bwd_count
        total_bytes = fwd_bytes + bwd_bytes
        
        # Timestamps
        fwd_times = flow_data['fwd_timestamps']
        bwd_times = flow_data['bwd_timestamps']
        all_times = sorted(fwd_times + bwd_times)
        
        # Calculate inter-arrival times
        fwd_iat = np.diff(fwd_times) if len(fwd_times) > 1 else np.array([0])
        bwd_iat = np.diff(bwd_times) if len(bwd_times) > 1 else np.array([0])
        flow_iat = np.diff(all_times) if len(all_times) > 1 else np.array([0])
        
        # Active/Idle times (simplified)
        active_mean = np.mean(flow_iat) if len(flow_iat) > 0 else 0
        active_std = np.std(flow_iat) if len(flow_iat) > 0 else 0
        active_max = np.max(flow_iat) if len(flow_iat) > 0 else 0
        active_min = np.min(flow_iat) if len(flow_iat) > 0 else 0
        
        # Idle time (gaps > threshold)
        idle_times = flow_iat[flow_iat > 1.0] if len(flow_iat) > 0 else np.array([0])
        idle_mean = np.mean(idle_times) if len(idle_times) > 0 else 0
        idle_std = np.std(idle_times) if len(idle_times) > 0 else 0
        idle_max = np.max(idle_times) if len(idle_times) > 0 else 0
        idle_min = np.min(idle_times) if len(idle_times) > 0 else 0
        
        # TCP flags
        flags = flow_data['flags']
        fin_count = sum(1 for f in flags if f & 0x01) if flags else 0
        syn_count = sum(1 for f in flags if f & 0x02) if flags else 0
        rst_count = sum(1 for f in flags if f & 0x04) if flags else 0
        psh_count = sum(1 for f in flags if f & 0x08) if flags else 0
        ack_count = sum(1 for f in flags if f & 0x10) if flags else 0
        urg_count = sum(1 for f in flags if f & 0x20) if flags else 0
        cwe_count = sum(1 for f in flags if f & 0x40) if flags else 0
        ece_count = sum(1 for f in flags if f & 0x80) if flags else 0
        
        # Build feature dictionary (68 features)
        features = {
            # Flow basics
            'Flow Duration': duration * 1000000,  # Convert to microseconds
            'Total Fwd Packets': fwd_count,
            'Total Backward Packets': bwd_count,
            'Total Length of Fwd Packets': fwd_bytes,
            'Total Length of Bwd Packets': bwd_bytes,
            
            # Forward packet length stats
            'Fwd Packet Length Max': np.max(fwd_lengths),
            'Fwd Packet Length Min': np.min(fwd_lengths),
            'Fwd Packet Length Mean': np.mean(fwd_lengths),
            'Fwd Packet Length Std': np.std(fwd_lengths),
            
            # Backward packet length stats
            'Bwd Packet Length Max': np.max(bwd_lengths),
            'Bwd Packet Length Min': np.min(bwd_lengths),
            'Bwd Packet Length Mean': np.mean(bwd_lengths),
            'Bwd Packet Length Std': np.std(bwd_lengths),
            
            # Flow bytes/packet rates
            'Flow Bytes/s': total_bytes / duration if duration > 0 else 0,
            'Flow Packets/s': total_packets / duration if duration > 0 else 0,
            'Flow IAT Mean': np.mean(flow_iat) * 1000000 if len(flow_iat) > 0 else 0,
            'Flow IAT Std': np.std(flow_iat) * 1000000 if len(flow_iat) > 0 else 0,
            'Flow IAT Max': np.max(flow_iat) * 1000000 if len(flow_iat) > 0 else 0,
            'Flow IAT Min': np.min(flow_iat) * 1000000 if len(flow_iat) > 0 else 0,
            
            # Forward IAT
            'Fwd IAT Total': np.sum(fwd_iat) * 1000000 if len(fwd_iat) > 0 else 0,
            'Fwd IAT Mean': np.mean(fwd_iat) * 1000000 if len(fwd_iat) > 0 else 0,
            'Fwd IAT Std': np.std(fwd_iat) * 1000000 if len(fwd_iat) > 0 else 0,
            'Fwd IAT Max': np.max(fwd_iat) * 1000000 if len(fwd_iat) > 0 else 0,
            'Fwd IAT Min': np.min(fwd_iat) * 1000000 if len(fwd_iat) > 0 else 0,
            
            # Backward IAT
            'Bwd IAT Total': np.sum(bwd_iat) * 1000000 if len(bwd_iat) > 0 else 0,
            'Bwd IAT Mean': np.mean(bwd_iat) * 1000000 if len(bwd_iat) > 0 else 0,
            'Bwd IAT Std': np.std(bwd_iat) * 1000000 if len(bwd_iat) > 0 else 0,
            'Bwd IAT Max': np.max(bwd_iat) * 1000000 if len(bwd_iat) > 0 else 0,
            'Bwd IAT Min': np.min(bwd_iat) * 1000000 if len(bwd_iat) > 0 else 0,
            
            # TCP Flags
            'FIN Flag Count': fin_count,
            'SYN Flag Count': syn_count,
            'RST Flag Count': rst_count,
            'PSH Flag Count': psh_count,
            'ACK Flag Count': ack_count,
            'URG Flag Count': urg_count,
            'CWE Flag Count': cwe_count,
            'ECE Flag Count': ece_count,
            
            # Down/Up Ratio
            'Down/Up Ratio': bwd_bytes / fwd_bytes if fwd_bytes > 0 else 0,
            'Average Packet Size': total_bytes / total_packets if total_packets > 0 else 0,
            'Avg Fwd Segment Size': fwd_bytes / fwd_count if fwd_count > 0 else 0,
            'Avg Bwd Segment Size': bwd_bytes / bwd_count if bwd_count > 0 else 0,
            
            # Header lengths (estimated)
            'Fwd Header Length': fwd_count * 20,  # Simplified
            'Bwd Header Length': bwd_count * 20,
            
            # Packets/s
            'Fwd Packets/s': fwd_count / duration if duration > 0 else 0,
            'Bwd Packets/s': bwd_count / duration if duration > 0 else 0,
            
            # Packet length stats
            'Min Packet Length': min(np.min(fwd_lengths), np.min(bwd_lengths)),
            'Max Packet Length': max(np.max(fwd_lengths), np.max(bwd_lengths)),
            'Packet Length Mean': np.mean(fwd_lengths + bwd_lengths),
            'Packet Length Std': np.std(fwd_lengths + bwd_lengths),
            'Packet Length Variance': np.var(fwd_lengths + bwd_lengths),
            
            # Subflow features
            'Subflow Fwd Packets': fwd_count,
            'Subflow Fwd Bytes': fwd_bytes,
            'Subflow Bwd Packets': bwd_count,
            'Subflow Bwd Bytes': bwd_bytes,
            
            # Init window bytes
            'Init_Win_bytes_forward': fwd_bytes if fwd_count > 0 else 0,
            'Init_Win_bytes_backward': bwd_bytes if bwd_count > 0 else 0,
            
            # Act data packets
            'act_data_pkt_fwd': fwd_count,
            'min_seg_size_forward': np.min(fwd_lengths) if len(fwd_lengths) > 0 else 0,
            
            # Active/Idle
            'Active Mean': active_mean * 1000000,
            'Active Std': active_std * 1000000,
            'Active Max': active_max * 1000000,
            'Active Min': active_min * 1000000,
            'Idle Mean': idle_mean * 1000000,
            'Idle Std': idle_std * 1000000,
            'Idle Max': idle_max * 1000000,
            'Idle Min': idle_min * 1000000,
            
            # Additional features to reach 82 (selector expects 82, selects 68)
            'Total Length of Packets': total_bytes,
            'act_data_pkt_bwd': bwd_count,
            'Fwd Avg Bytes/Bulk': fwd_bytes / fwd_count if fwd_count > 0 else 0,
            'Fwd Avg Packets/Bulk': 1.0 if fwd_count > 0 else 0,
            'Fwd Avg Bulk Rate': fwd_bytes / duration if duration > 0 else 0,
            'Bwd Avg Bytes/Bulk': bwd_bytes / bwd_count if bwd_count > 0 else 0,
            'Bwd Avg Packets/Bulk': 1.0 if bwd_count > 0 else 0,
            'Bwd Avg Bulk Rate': bwd_bytes / duration if duration > 0 else 0,
            'Total Avg Bytes/Bulk': total_bytes / total_packets if total_packets > 0 else 0,
            'Total Avg Packets/Bulk': 1.0,
            'Total Avg Bulk Rate': total_bytes / duration if duration > 0 else 0,
            'Fwd Packet Length Variance': np.var(fwd_lengths) if len(fwd_lengths) > 0 else 0,
            'Bwd Packet Length Variance': np.var(bwd_lengths) if len(bwd_lengths) > 0 else 0,
            'Fwd Header Length.1': fwd_count * 20,  # Duplicate for selector
            'Bwd Header Length.1': bwd_count * 20,   # Duplicate for selector
            'Total Fwd Packets.1': fwd_count,        # Duplicate for selector
        }
        
        return pd.DataFrame([features])

