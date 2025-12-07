#!/usr/bin/env python3
"""
Comprehensive diagnostic script for IDS Monitoring System
Tests all components independently and together
"""

import sys
import os
import asyncio
import time
import logging
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from app.config import VM_IP as DEFAULT_VM_IP, FLOW_TIMEOUT
from app.services.capture.interface_manager import InterfaceManager
from app.services.capture.packet_capture import PacketCapture
from app.services.capture.flow_aggregator import FlowAggregator, Flow
from app.services.feature_extractor import FeatureExtractor
from app.services.ids_model import get_model_service
from app.services.detection_engine import get_detection_engine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_header(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def print_result(test_name, passed, message=""):
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status} - {test_name}")
    if message:
        print(f"      {message}")

async def test_1_model_loading():
    print_header("TEST 1: Model Loading")
    try:
        model_service = get_model_service()
        print_result("Model Service Created", True)
        print_result("Model Loaded", model_service.is_loaded, 
                    f"Classes: {len(model_service.class_names)}")
        print(f"      Feature count expected: 68")
        print(f"      Classes: {', '.join(model_service.class_names[:5])}...")
        return model_service.is_loaded
    except Exception as e:
        print_result("Model Loading", False, str(e))
        return False

async def test_2_interface_detection():
    print_header("TEST 2: Network Interface Detection")
    try:
        interface_manager = InterfaceManager()
        interface = interface_manager.get_interface(vm_ip=DEFAULT_VM_IP)
        print_result("Interface Detection", interface is not None, 
                    f"Interface: {interface}")
        
        has_perms = interface_manager.check_capture_permissions()
        print_result("Capture Permissions", has_perms,
                    "Root privileges detected" if has_perms else "Run with sudo")
        
        return interface is not None
    except Exception as e:
        print_result("Interface Detection", False, str(e))
        return False

async def test_3_packet_capture():
    print_header("TEST 3: Packet Capture (10 seconds)")
    try:
        interface_manager = InterfaceManager()
        interface = interface_manager.get_interface(vm_ip=DEFAULT_VM_IP)
        
        packets_captured = []
        
        def packet_callback(packet_info):
            packets_captured.append(packet_info)
            if len(packets_captured) == 1:
                logger.info(f"First packet: {packet_info['src_ip']} → {packet_info['dst_ip']}")
        
        packet_capture = PacketCapture(
            interface=interface,
            packet_callback=packet_callback,
            vm_ip=None  # Capture all traffic
        )
        
        packet_capture.start()
        logger.info("Capturing for 10 seconds...")
        
        await asyncio.sleep(10)
        
        packet_capture.stop()
        
        print_result("Packet Capture", len(packets_captured) > 0,
                    f"Captured {len(packets_captured)} packets")
        
        if len(packets_captured) > 0:
            sample = packets_captured[0]
            print(f"      Sample: {sample['src_ip']}:{sample['src_port']} → "
                  f"{sample['dst_ip']}:{sample['dst_port']} ({sample['protocol']})")
        else:
            print("      ⚠ No packets captured. Try generating traffic:")
            print(f"      ping {DEFAULT_VM_IP} (in another terminal)")
        
        return len(packets_captured) > 0
        
    except Exception as e:
        print_result("Packet Capture", False, str(e))
        import traceback
        traceback.print_exc()
        return False

async def test_4_flow_aggregation():
    print_header("TEST 4: Flow Aggregation")
    try:
        flow_aggregator = FlowAggregator(flow_timeout=FLOW_TIMEOUT)
        
        # Create synthetic packets
        logger.info("Creating synthetic flow with 25 packets...")
        start_time = time.time()
        
        for i in range(25):
            packet_info = {
                'src_ip': '192.168.1.100',
                'dst_ip': DEFAULT_VM_IP,
                'src_port': 54321,
                'dst_port': 80,
                'protocol': 'TCP',
                'length': 60 + i,
                'flags': {'S': i == 0, 'A': i > 0},
                'timestamp': start_time + (i * 0.1)
            }
            
            completed = flow_aggregator.add_packet(packet_info)
            if completed:
                logger.info(f"Flow auto-completed after {i+1} packets")
                break
            
            if i == 10:
                await asyncio.sleep(2.1)  # Wait for packet threshold
        
        active_count = flow_aggregator.get_active_flow_count()
        completed_flows = flow_aggregator.get_completed_flows()
        
        print_result("Flow Creation", active_count > 0 or len(completed_flows) > 0,
                    f"Active: {active_count}, Completed: {len(completed_flows)}")
        
        if len(completed_flows) > 0:
            flow = completed_flows[0]
            print(f"      Flow: {flow.src_ip}:{flow.src_port} → {flow.dst_ip}:{flow.dst_port}")
            print(f"      Packets: {flow.total_packets}, Bytes: {flow.total_bytes}")
            return True
        else:
            print("      ⚠ Flow not completed - may need more time")
            return False
            
    except Exception as e:
        print_result("Flow Aggregation", False, str(e))
        import traceback
        traceback.print_exc()
        return False

async def test_5_feature_extraction():
    print_header("TEST 5: Feature Extraction")
    try:
        flow_aggregator = FlowAggregator()
        feature_extractor = FeatureExtractor()
        
        # Create a realistic flow
        logger.info("Creating synthetic flow...")
        start_time = time.time()
        
        for i in range(30):
            packet_info = {
                'src_ip': '192.168.1.100',
                'dst_ip': DEFAULT_VM_IP,
                'src_port': 54321,
                'dst_port': 80,
                'protocol': 'TCP',
                'length': 60 + (i % 10),
                'flags': {
                    'S': i == 0,
                    'A': i > 0,
                    'P': i % 5 == 0 and i > 0
                },
                'timestamp': start_time + (i * 0.05)
            }
            flow_aggregator.add_packet(packet_info)
        
        # Force complete the flow
        flows = list(flow_aggregator.flows.values())
        if flows:
            flows[0].finalize()
        
        print_result("Flow Created", len(flows) > 0,
                    f"Flow has {flows[0].total_packets} packets" if flows else "")
        
        # Extract features
        features_df = feature_extractor.extract_features_from_flows(flows)
        
        print_result("Feature Extraction", not features_df.empty,
                    f"Extracted {features_df.shape[1]} features (expected 82)")
        
        if not features_df.empty:
            print(f"      Sample features: {list(features_df.columns[:5])}")
            return features_df.shape[1] == 82
        else:
            print("      ⚠ No features extracted")
            return False
            
    except Exception as e:
        print_result("Feature Extraction", False, str(e))
        import traceback
        traceback.print_exc()
        return False

async def test_6_model_prediction():
    print_header("TEST 6: Model Prediction")
    try:
        flow_aggregator = FlowAggregator()
        feature_extractor = FeatureExtractor()
        model_service = get_model_service()
        
        # Create synthetic flow (simulating DDoS-like traffic)
        logger.info("Creating synthetic DDoS-like flow...")
        start_time = time.time()
        
        for i in range(100):  # Many packets, short duration
            packet_info = {
                'src_ip': '192.168.1.100',
                'dst_ip': DEFAULT_VM_IP,
                'src_port': 54321,
                'dst_port': 80,
                'protocol': 'TCP',
                'length': 40,  # Small packets
                'flags': {'S': True},  # SYN flood
                'timestamp': start_time + (i * 0.001)  # Very fast
            }
            flow_aggregator.add_packet(packet_info)
        
        flows = list(flow_aggregator.flows.values())
        if flows:
            flows[0].finalize()
        
        # Extract and predict
        features_df = feature_extractor.extract_features_from_flows(flows)
        predictions, probabilities = model_service.predict(features_df)
        
        prediction = predictions[0]
        confidence = float(probabilities[0].max())
        is_attack = model_service.is_attack(prediction)
        
        print_result("Model Prediction", True,
                    f"Prediction: {prediction} (confidence: {confidence:.1%})")
        print(f"      Is Attack: {is_attack}")
        
        return True
        
    except Exception as e:
        print_result("Model Prediction", False, str(e))
        import traceback
        traceback.print_exc()
        return False

async def test_7_detection_engine():
    print_header("TEST 7: Detection Engine Integration (15 seconds)")
    try:
        detection_engine = get_detection_engine()
        
        logger.info("Starting detection engine...")
        success = await detection_engine.start_monitoring(vm_ip=DEFAULT_VM_IP)
        
        print_result("Detection Engine Start", success)
        
        if not success:
            return False
        
        logger.info("Monitoring for 15 seconds. Generate traffic to see detections:")
        logger.info(f"  Example: ping {DEFAULT_VM_IP}")
        logger.info(f"  Or: curl http://{DEFAULT_VM_IP}")
        
        # Monitor for 15 seconds
        for i in range(15):
            await asyncio.sleep(1)
            stats = detection_engine.get_stats()
            if i % 5 == 4:
                logger.info(f"  Flows: {stats['total_flows']}, "
                          f"Attacks: {stats['attack_count']}, "
                          f"Active: {stats['active_flows']}, "
                          f"Packets: {stats['capture_stats'].get('packet_count', 0)}")
        
        # Stop and get final stats
        await detection_engine.stop_monitoring()
        stats = detection_engine.get_stats()
        
        print_result("Detection Engine Stop", True)
        print(f"      Total Flows Processed: {stats['total_flows']}")
        print(f"      Attacks Detected: {stats['attack_count']}")
        print(f"      Benign Flows: {stats['benign_count']}")
        print(f"      Packets Captured: {stats['capture_stats'].get('packet_count', 0)}")
        
        return True
        
    except Exception as e:
        print_result("Detection Engine", False, str(e))
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("\n" + "="*80)
    print("  IDS MONITORING SYSTEM - COMPREHENSIVE DIAGNOSTICS")
    print("="*80)
    print(f"\nTarget VM IP: {DEFAULT_VM_IP}")
    print(f"Flow Timeout: {FLOW_TIMEOUT} seconds")
    print("\nRunning all tests...\n")
    
    results = {}
    
    # Run tests
    results['model'] = await test_1_model_loading()
    results['interface'] = await test_2_interface_detection()
    results['capture'] = await test_3_packet_capture()
    results['flow'] = await test_4_flow_aggregation()
    results['features'] = await test_5_feature_extraction()
    results['prediction'] = await test_6_model_prediction()
    results['engine'] = await test_7_detection_engine()
    
    # Summary
    print_header("SUMMARY")
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test, result in results.items():
        status = "✓" if result else "✗"
        print(f"  {status} {test.upper()}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is working correctly.")
        print("\nNext steps:")
        print("  1. Start the backend: cd backend && ./run_with_sudo.sh")
        print("  2. Start the frontend: cd frontend && npm run dev")
        print("  3. Open http://localhost:5173")
        print("  4. Click 'Start Monitoring'")
        print("  5. Launch attacks and watch detections!")
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
        if not results.get('capture'):
            print("\nHint: If packet capture failed, ensure:")
            print("  - You're running with sudo")
            print("  - Your VM is running and reachable")
            print("  - Network traffic is being generated")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDiagnostics interrupted by user.")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()

