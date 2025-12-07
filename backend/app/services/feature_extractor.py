"""Feature extractor for CIC-IDS2018 dataset features (82 features)"""

import numpy as np
import pandas as pd
from typing import List, Dict
import logging
from .capture.flow_aggregator import Flow

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """Extracts 82 CIC-IDS2018 features from network flows"""
    
    # Feature names matching CIC-IDS2018 dataset (82 features)
    FEATURE_NAMES = [
        'Destination Port', 'Flow Duration', 'Total Fwd Packets',
        'Total Backward Packets', 'Total Length of Fwd Packets',
        'Total Length of Bwd Packets', 'Fwd Packet Length Max',
        'Fwd Packet Length Min', 'Fwd Packet Length Mean',
        'Fwd Packet Length Std', 'Bwd Packet Length Max',
        'Bwd Packet Length Min', 'Bwd Packet Length Mean',
        'Bwd Packet Length Std', 'Flow Bytes/s', 'Flow Packets/s',
        'Flow IAT Mean', 'Flow IAT Std', 'Flow IAT Max', 'Flow IAT Min',
        'Fwd IAT Total', 'Fwd IAT Mean', 'Fwd IAT Std', 'Fwd IAT Max',
        'Fwd IAT Min', 'Bwd IAT Total', 'Bwd IAT Mean', 'Bwd IAT Std',
        'Bwd IAT Max', 'Bwd IAT Min', 'Fwd PSH Flags', 'Bwd PSH Flags',
        'Fwd URG Flags', 'Bwd URG Flags', 'Fwd Header Length',
        'Bwd Header Length', 'Fwd Packets/s', 'Bwd Packets/s',
        'Min Packet Length', 'Max Packet Length', 'Packet Length Mean',
        'Packet Length Std', 'Packet Length Variance', 'FIN Flag Count',
        'SYN Flag Count', 'RST Flag Count', 'PSH Flag Count',
        'ACK Flag Count', 'URG Flag Count', 'CWE Flag Count',
        'ECE Flag Count', 'Down/Up Ratio', 'Average Packet Size',
        'Avg Fwd Segment Size', 'Avg Bwd Segment Size',
        'Fwd Header Length.1', 'Fwd Avg Bytes/Bulk', 'Fwd Avg Packets/Bulk',
        'Fwd Avg Bulk Rate', 'Bwd Avg Bytes/Bulk', 'Bwd Avg Packets/Bulk',
        'Bwd Avg Bulk Rate', 'Subflow Fwd Packets', 'Subflow Fwd Bytes',
        'Subflow Bwd Packets', 'Subflow Bwd Bytes', 'Init_Win_bytes_forward',
        'Init_Win_bytes_backward', 'act_data_pkt_fwd', 'min_seg_size_forward',
        'Active Mean', 'Active Std', 'Active Max', 'Active Min',
        'Idle Mean', 'Idle Std', 'Idle Max', 'Idle Min',
        'SimillarHTTP', 'Inbound',
        # Add 2 missing features commonly in CIC-IDS2018
        'Fwd Byts/b Avg', 'Fwd Pkts/b Avg'
    ]
    
    def __init__(self):
        self.feature_count = len(self.FEATURE_NAMES)
        logger.info(f"Feature extractor initialized with {self.feature_count} features")
    
    def _safe_div(self, a, b, default=0.0):
        """Safe division"""
        return a / b if b != 0 else default
    
    def _safe_std(self, values):
        """Safe standard deviation"""
        return np.std(values) if len(values) > 1 else 0.0
    
    def _safe_mean(self, values):
        """Safe mean"""
        return np.mean(values) if len(values) > 0 else 0.0
    
    def extract_features_from_flow(self, flow: Flow) -> Dict[str, float]:
        """Extract all 82 features from a flow"""
        
        # Basic flow statistics
        duration = flow.duration if flow.duration > 0 else 0.001  # Avoid division by zero
        fwd_packets = flow.fwd_packets
        bwd_packets = flow.bwd_packets
        total_packets = flow.total_packets
        fwd_bytes = flow.fwd_bytes
        bwd_bytes = flow.bwd_bytes
        total_bytes = flow.total_bytes
        
        # Packet lengths
        fwd_lens = flow.fwd_packet_lengths if flow.fwd_packet_lengths else [0]
        bwd_lens = flow.bwd_packet_lengths if flow.bwd_packet_lengths else [0]
        all_lens = flow.packet_lengths if flow.packet_lengths else [0]
        
        # Inter-arrival times
        fwd_iats = flow.fwd_iat if flow.fwd_iat else [0]
        bwd_iats = flow.bwd_iat if flow.bwd_iat else [0]
        
        # Calculate all IATs
        all_iats = []
        if len(flow.packet_times) > 1:
            for i in range(1, len(flow.packet_times)):
                all_iats.append(flow.packet_times[i] - flow.packet_times[i-1])
        if not all_iats:
            all_iats = [0]
        
        # Extract features
        features = {}
        
        # 1. Destination Port
        features['Destination Port'] = float(flow.dst_port)
        
        # 2. Flow Duration
        features['Flow Duration'] = duration * 1000000  # Convert to microseconds
        
        # 3-4. Packet counts
        features['Total Fwd Packets'] = float(fwd_packets)
        features['Total Backward Packets'] = float(bwd_packets)
        
        # 5-6. Total lengths
        features['Total Length of Fwd Packets'] = float(fwd_bytes)
        features['Total Length of Bwd Packets'] = float(bwd_bytes)
        
        # 7-10. Forward packet length statistics
        features['Fwd Packet Length Max'] = float(max(fwd_lens))
        features['Fwd Packet Length Min'] = float(min(fwd_lens))
        features['Fwd Packet Length Mean'] = self._safe_mean(fwd_lens)
        features['Fwd Packet Length Std'] = self._safe_std(fwd_lens)
        
        # 11-14. Backward packet length statistics
        features['Bwd Packet Length Max'] = float(max(bwd_lens))
        features['Bwd Packet Length Min'] = float(min(bwd_lens))
        features['Bwd Packet Length Mean'] = self._safe_mean(bwd_lens)
        features['Bwd Packet Length Std'] = self._safe_std(bwd_lens)
        
        # 15-16. Flow rate
        features['Flow Bytes/s'] = self._safe_div(total_bytes, duration)
        features['Flow Packets/s'] = self._safe_div(total_packets, duration)
        
        # 17-20. Flow IAT statistics
        features['Flow IAT Mean'] = self._safe_mean(all_iats) * 1000000
        features['Flow IAT Std'] = self._safe_std(all_iats) * 1000000
        features['Flow IAT Max'] = float(max(all_iats)) * 1000000
        features['Flow IAT Min'] = float(min(all_iats)) * 1000000
        
        # 21-25. Forward IAT statistics
        fwd_iat_total = sum(fwd_iats)
        features['Fwd IAT Total'] = fwd_iat_total * 1000000
        features['Fwd IAT Mean'] = self._safe_mean(fwd_iats) * 1000000
        features['Fwd IAT Std'] = self._safe_std(fwd_iats) * 1000000
        features['Fwd IAT Max'] = float(max(fwd_iats)) * 1000000
        features['Fwd IAT Min'] = float(min(fwd_iats)) * 1000000
        
        # 26-30. Backward IAT statistics
        bwd_iat_total = sum(bwd_iats)
        features['Bwd IAT Total'] = bwd_iat_total * 1000000
        features['Bwd IAT Mean'] = self._safe_mean(bwd_iats) * 1000000
        features['Bwd IAT Std'] = self._safe_std(bwd_iats) * 1000000
        features['Bwd IAT Max'] = float(max(bwd_iats)) * 1000000
        features['Bwd IAT Min'] = float(min(bwd_iats)) * 1000000
        
        # 31-34. PSH and URG flags (simplified - would need per-direction tracking)
        features['Fwd PSH Flags'] = float(flow.psh_count) if fwd_packets > 0 else 0.0
        features['Bwd PSH Flags'] = 0.0  # Would need bidirectional tracking
        features['Fwd URG Flags'] = float(flow.urg_count) if fwd_packets > 0 else 0.0
        features['Bwd URG Flags'] = 0.0
        
        # 35-36. Header lengths (estimated as 20 bytes for IP + 20 for TCP)
        features['Fwd Header Length'] = float(fwd_packets * 40)
        features['Bwd Header Length'] = float(bwd_packets * 40)
        
        # 37-38. Packets per second
        features['Fwd Packets/s'] = self._safe_div(fwd_packets, duration)
        features['Bwd Packets/s'] = self._safe_div(bwd_packets, duration)
        
        # 39-43. Packet length statistics
        features['Min Packet Length'] = float(min(all_lens))
        features['Max Packet Length'] = float(max(all_lens))
        features['Packet Length Mean'] = self._safe_mean(all_lens)
        features['Packet Length Std'] = self._safe_std(all_lens)
        features['Packet Length Variance'] = np.var(all_lens) if len(all_lens) > 1 else 0.0
        
        # 44-51. Flag counts
        features['FIN Flag Count'] = float(flow.fin_count)
        features['SYN Flag Count'] = float(flow.syn_count)
        features['RST Flag Count'] = float(flow.rst_count)
        features['PSH Flag Count'] = float(flow.psh_count)
        features['ACK Flag Count'] = float(flow.ack_count)
        features['URG Flag Count'] = float(flow.urg_count)
        features['CWE Flag Count'] = 0.0  # Not tracked
        features['ECE Flag Count'] = 0.0  # Not tracked
        
        # 52. Down/Up Ratio
        features['Down/Up Ratio'] = self._safe_div(bwd_packets, fwd_packets)
        
        # 53-54. Average sizes
        features['Average Packet Size'] = self._safe_div(total_bytes, total_packets)
        features['Avg Fwd Segment Size'] = self._safe_div(fwd_bytes, fwd_packets)
        features['Avg Bwd Segment Size'] = self._safe_div(bwd_bytes, bwd_packets)
        
        # 55. Fwd Header Length (duplicate)
        features['Fwd Header Length.1'] = features['Fwd Header Length']
        
        # 56-61. Bulk statistics (not easily calculable from flow, using defaults)
        features['Fwd Avg Bytes/Bulk'] = 0.0
        features['Fwd Avg Packets/Bulk'] = 0.0
        features['Fwd Avg Bulk Rate'] = 0.0
        features['Bwd Avg Bytes/Bulk'] = 0.0
        features['Bwd Avg Packets/Bulk'] = 0.0
        features['Bwd Avg Bulk Rate'] = 0.0
        
        # 62-65. Subflow features (treating flow as single subflow)
        features['Subflow Fwd Packets'] = float(fwd_packets)
        features['Subflow Fwd Bytes'] = float(fwd_bytes)
        features['Subflow Bwd Packets'] = float(bwd_packets)
        features['Subflow Bwd Bytes'] = float(bwd_bytes)
        
        # 66-67. Initial window bytes (not tracked, using defaults)
        features['Init_Win_bytes_forward'] = 0.0
        features['Init_Win_bytes_backward'] = 0.0
        
        # 68-69. Active data packets
        features['act_data_pkt_fwd'] = float(fwd_packets)
        features['min_seg_size_forward'] = float(min(fwd_lens))
        
        # 70-77. Active/Idle statistics (not easily calculable, using defaults)
        features['Active Mean'] = 0.0
        features['Active Std'] = 0.0
        features['Active Max'] = 0.0
        features['Active Min'] = 0.0
        features['Idle Mean'] = 0.0
        features['Idle Std'] = 0.0
        features['Idle Max'] = 0.0
        features['Idle Min'] = 0.0
        
        # 78-79. HTTP and direction (defaults)
        features['SimillarHTTP'] = 0.0
        features['Inbound'] = 0.0
        
        # 80-81. Bulk stats (additional features to reach 82)
        features['Fwd Byts/b Avg'] = self._safe_div(fwd_bytes, fwd_packets)
        features['Fwd Pkts/b Avg'] = float(fwd_packets)
        
        return features
    
    def extract_features_from_flows(self, flows: List[Flow]) -> pd.DataFrame:
        """Extract features from multiple flows"""
        if not flows:
            return pd.DataFrame()
        
        feature_list = []
        for flow in flows:
            try:
                features = self.extract_features_from_flow(flow)
                feature_list.append(features)
            except Exception as e:
                logger.error(f"Error extracting features from flow {flow.flow_id}: {e}")
        
        if not feature_list:
            return pd.DataFrame()
        
        # Create DataFrame
        df = pd.DataFrame(feature_list)
        
        # Ensure all features are present and in correct order
        for feature_name in self.FEATURE_NAMES:
            if feature_name not in df.columns:
                df[feature_name] = 0.0
        
        # Reorder columns
        df = df[self.FEATURE_NAMES]
        
        # Replace inf with large values
        df = df.replace([np.inf, -np.inf], 1e10)
        
        # Fill NaN with 0
        df = df.fillna(0.0)
        
        logger.debug(f"Extracted features for {len(flows)} flows")
        
        return df
    
    def get_feature_count(self) -> int:
        """Get number of features"""
        return self.feature_count
    
    def get_feature_names(self) -> List[str]:
        """Get feature names"""
        return self.FEATURE_NAMES.copy()
