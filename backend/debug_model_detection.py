#!/usr/bin/env python3
"""
Debug script to understand why HTTP flood attacks aren't being detected
"""

import sys
import os
import asyncio
import time
import logging
import numpy as np
import pandas as pd

# Add the backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.services.capture.flow_aggregator import Flow
from app.services.feature_extractor import FeatureExtractor
from app.services.ids_model import IDSModelService
from app.config import VM_IP

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def create_http_flood_flow():
    """Create a synthetic HTTP flood flow based on attack characteristics"""
    flow = Flow(
        flow_id="test_http_flood",
        src_ip="192.168.1.100",
        dst_ip=VM_IP,
        src_port=54321,
        dst_port=80,  # HTTP
        protocol="TCP",
        start_time=time.time() - 1,
        last_seen=time.time(),
        duration=1.0
    )
    
    # HTTP flood characteristics:
    # - Many rapid requests (high packet rate)
    # - Small packets (HTTP GET requests)
    # - Minimal inter-arrival time
    # - Mostly forward direction
    # - Many SYN/ACK packets
    
    current_time = time.time() - 1
    for i in range(100):  # 100 packets in 1 second = very high rate
        packet_info = {
            'src_ip': "192.168.1.100",
            'dst_ip': VM_IP,
            'protocol': 'TCP',
            'src_port': 54321,
            'dst_port': 80,
            'length': 60 + (i % 20),  # Small packets (60-80 bytes)
            'flags': {
                'S': i % 10 == 0,  # SYN every 10 packets
                'A': True,          # ACK on all
                'F': False,
                'R': False,
                'P': i % 3 == 0,    # PSH on many
                'U': False
            },
            'timestamp': current_time + (i * 0.01)  # 10ms apart
        }
        flow.add_packet(packet_info, is_forward=True)
        
        # Add occasional backward packets (responses)
        if i % 5 == 0:
            resp_packet = {
                'src_ip': VM_IP,
                'dst_ip': "192.168.1.100",
                'protocol': 'TCP',
                'src_port': 80,
                'dst_port': 54321,
                'length': 40,
                'flags': {'S': False, 'A': True, 'F': False, 'R': False, 'P': False, 'U': False},
                'timestamp': current_time + (i * 0.01) + 0.005
            }
            flow.add_packet(resp_packet, is_forward=False)
    
    flow.finalize()
    return flow

def create_normal_flow():
    """Create a normal benign flow for comparison"""
    flow = Flow(
        flow_id="test_normal",
        src_ip="192.168.1.100",
        dst_ip=VM_IP,
        src_port=54322,
        dst_port=443,  # HTTPS
        protocol="TCP",
        start_time=time.time() - 5,
        last_seen=time.time(),
        duration=5.0
    )
    
    # Normal browsing characteristics:
    # - Moderate packet rate
    # - Varied packet sizes
    # - Bidirectional (balanced)
    # - Normal TCP handshake
    
    current_time = time.time() - 5
    for i in range(20):  # 20 packets over 5 seconds = 4 pkt/s
        packet_info = {
            'src_ip': "192.168.1.100",
            'dst_ip': VM_IP,
            'protocol': 'TCP',
            'src_port': 54322,
            'dst_port': 443,
            'length': 500 + (i * 50),  # Larger, varied packets
            'flags': {
                'S': i == 0,
                'A': True,
                'F': i == 19,
                'R': False,
                'P': i % 5 == 0,
                'U': False
            },
            'timestamp': current_time + (i * 0.25)  # 250ms apart
        }
        flow.add_packet(packet_info, is_forward=True)
        
        # Balanced backward traffic
        resp_packet = {
            'src_ip': VM_IP,
            'dst_ip': "192.168.1.100",
            'protocol': 'TCP',
            'src_port': 443,
            'dst_port': 54322,
            'length': 1000 + (i * 100),
            'flags': {'S': False, 'A': True, 'F': False, 'R': False, 'P': i % 3 == 0, 'U': False},
            'timestamp': current_time + (i * 0.25) + 0.05
        }
        flow.add_packet(resp_packet, is_forward=False)
    
    flow.finalize()
    return flow

def main():
    logger.info("=" * 80)
    logger.info("HTTP FLOOD DETECTION DEBUG")
    logger.info("=" * 80)
    
    # Load model
    logger.info("\n1. Loading IDS model...")
    model_service = IDSModelService()
    model_service.load_model()
    
    if not model_service.is_loaded:
        logger.error("Failed to load model. Exiting.")
        return
    
    logger.info(f"✓ Model loaded: {len(model_service.get_class_names())} classes")
    logger.info(f"  Classes: {model_service.get_class_names()}")
    
    # Create flows
    logger.info("\n2. Creating synthetic flows...")
    http_flood = create_http_flood_flow()
    normal_flow = create_normal_flow()
    
    logger.info(f"✓ HTTP Flood flow: {http_flood.total_packets} packets, {http_flood.duration:.2f}s duration")
    logger.info(f"  Packet rate: {http_flood.total_packets / http_flood.duration:.1f} pkt/s")
    logger.info(f"  Bytes: {http_flood.total_bytes}, Avg size: {http_flood.total_bytes / http_flood.total_packets:.0f} bytes")
    logger.info(f"  SYN: {http_flood.syn_count}, ACK: {http_flood.ack_count}, PSH: {http_flood.psh_count}")
    
    logger.info(f"✓ Normal flow: {normal_flow.total_packets} packets, {normal_flow.duration:.2f}s duration")
    logger.info(f"  Packet rate: {normal_flow.total_packets / normal_flow.duration:.1f} pkt/s")
    logger.info(f"  Bytes: {normal_flow.total_bytes}, Avg size: {normal_flow.total_bytes / normal_flow.total_packets:.0f} bytes")
    
    # Extract features
    logger.info("\n3. Extracting features...")
    extractor = FeatureExtractor()
    
    # HTTP flood features
    http_features = extractor.extract_features_from_flow(http_flood)
    http_df = pd.DataFrame([http_features])
    logger.info(f"✓ Extracted {len(http_df.columns)} features from HTTP flood")
    
    # Normal features
    normal_features = extractor.extract_features_from_flow(normal_flow)
    normal_df = pd.DataFrame([normal_features])
    logger.info(f"✓ Extracted {len(normal_df.columns)} features from normal flow")
    
    # Show key distinguishing features
    logger.info("\n4. Key Feature Comparison:")
    logger.info(f"{'Feature':<30} {'HTTP Flood':<20} {'Normal':<20}")
    logger.info("-" * 70)
    key_features = [
        'Flow Duration', 'Total Fwd Packets', 'Total Backward Packets',
        'Flow Packets/s', 'Flow Bytes/s', 'Average Packet Size',
        'SYN Flag Count', 'ACK Flag Count', 'PSH Flag Count',
        'Destination Port'
    ]
    for feat in key_features:
        if feat in http_df.columns and feat in normal_df.columns:
            logger.info(f"{feat:<30} {http_df[feat].iloc[0]:<20.2f} {normal_df[feat].iloc[0]:<20.2f}")
    
    # Predict
    logger.info("\n5. Model Predictions:")
    logger.info("-" * 80)
    
    # HTTP Flood
    predictions, probabilities = model_service.predict(http_df)
    http_pred = predictions[0]
    http_conf = float(probabilities[0].max())
    http_is_attack = model_service.is_attack(http_pred)
    
    logger.info(f"HTTP FLOOD:")
    logger.info(f"  Prediction: {http_pred}")
    logger.info(f"  Confidence: {http_conf:.1%}")
    logger.info(f"  Is Attack: {http_is_attack}")
    logger.info(f"  Top 5 probabilities:")
    class_names = model_service.get_class_names()
    top5_indices = np.argsort(probabilities[0])[-5:][::-1]
    for idx in top5_indices:
        logger.info(f"    {class_names[idx]:<30}: {probabilities[0][idx]:.1%}")
    
    # Normal
    predictions, probabilities = model_service.predict(normal_df)
    normal_pred = predictions[0]
    normal_conf = float(probabilities[0].max())
    normal_is_attack = model_service.is_attack(normal_pred)
    
    logger.info(f"\nNORMAL FLOW:")
    logger.info(f"  Prediction: {normal_pred}")
    logger.info(f"  Confidence: {normal_conf:.1%}")
    logger.info(f"  Is Attack: {normal_is_attack}")
    logger.info(f"  Top 5 probabilities:")
    top5_indices = np.argsort(probabilities[0])[-5:][::-1]
    for idx in top5_indices:
        logger.info(f"    {class_names[idx]:<30}: {probabilities[0][idx]:.1%}")
    
    # Analysis
    logger.info("\n6. Analysis:")
    logger.info("=" * 80)
    if http_is_attack:
        logger.info("✅ SUCCESS: HTTP flood was correctly detected as an attack!")
    else:
        logger.info("❌ PROBLEM: HTTP flood was classified as benign!")
        logger.info("\nPossible reasons:")
        logger.info("  1. The model was trained on different HTTP flood patterns")
        logger.info("  2. Real HTTP flood from curl/requests looks too normal")
        logger.info("  3. Feature extraction might be missing key attack indicators")
        logger.info("  4. The attack intensity is too low (spread across many flows)")
        logger.info("\nSolutions:")
        logger.info("  - Try more aggressive attacks (higher rate, more connections)")
        logger.info("  - Use specialized DDoS tools (hping3, slowloris)")
        logger.info("  - Lower the detection threshold (currently 50%)")
        logger.info("  - Check if flows are being properly aggregated")
    
    if not normal_is_attack:
        logger.info("✅ GOOD: Normal flow was correctly classified as benign")
    else:
        logger.info("⚠️  WARNING: Normal flow was misclassified as attack")
    
    logger.info("=" * 80)

if __name__ == "__main__":
    main()

