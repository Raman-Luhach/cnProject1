#!/usr/bin/env python3
"""Verify that the feature extraction fix is working"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 70)
print("IDS System Verification")
print("=" * 70)
print()

# Test 1: Feature Extractor
print("1. Checking Feature Extractor...")
try:
    from app.services.feature_extractor import FeatureExtractor
    fe = FeatureExtractor()
    feature_count = fe.get_feature_count()
    print(f"   Feature count: {feature_count}")
    if feature_count == 82:
        print("   ✓ PASS - Correct feature count (82)")
    else:
        print(f"   ✗ FAIL - Expected 82, got {feature_count}")
        sys.exit(1)
except Exception as e:
    print(f"   ✗ FAIL - Error: {e}")
    sys.exit(1)

print()

# Test 2: Model Selector
print("2. Checking Model Selector...")
try:
    import pickle
    from pathlib import Path
    selector_path = Path(__file__).parent.parent / "cnmodel" / "ids_ddos_model" / "selector.pkl"
    with open(selector_path, 'rb') as f:
        import warnings
        warnings.filterwarnings('ignore')
        selector = pickle.load(f)
    expected_features = selector.n_features_in_
    output_features = selector.get_support().sum()
    print(f"   Selector expects: {expected_features} features")
    print(f"   Selector outputs: {output_features} features")
    if expected_features == 82:
        print("   ✓ PASS - Selector expects 82 features")
    else:
        print(f"   ✗ FAIL - Selector expects {expected_features}, not 82")
        sys.exit(1)
except Exception as e:
    print(f"   ✗ FAIL - Error: {e}")
    sys.exit(1)

print()

# Test 3: Feature Extraction Test
print("3. Testing Feature Extraction...")
try:
    from app.services.capture.flow_aggregator import Flow
    import time
    
    # Create a mock flow
    flow = Flow(
        flow_id="test_flow",
        src_ip="192.168.1.1",
        dst_ip="192.168.64.3",
        src_port=12345,
        dst_port=80,
        protocol="TCP"
    )
    
    # Add some packets
    flow.add_packet({
        'src_ip': '192.168.1.1',
        'dst_ip': '192.168.64.3',
        'src_port': 12345,
        'dst_port': 80,
        'protocol': 'TCP',
        'length': 64,
        'flags': {'S': True, 'A': False, 'F': False, 'R': False, 'P': False, 'U': False},
        'timestamp': time.time()
    }, is_forward=True)
    
    # Extract features
    features = fe.extract_features_from_flow(flow)
    extracted_count = len(features)
    
    print(f"   Extracted {extracted_count} features from test flow")
    if extracted_count == 82:
        print("   ✓ PASS - Extracted correct number of features")
    else:
        print(f"   ✗ FAIL - Expected 82, got {extracted_count}")
        print(f"   Missing features: {82 - extracted_count}")
        sys.exit(1)
        
except Exception as e:
    print(f"   ✗ FAIL - Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 4: Model Files Exist
print("4. Checking Model Files...")
try:
    from pathlib import Path
    model_dir = Path(__file__).parent.parent / "cnmodel" / "ids_ddos_model"
    required_files = ['ids_model.keras', 'scaler.pkl', 'encoder.pkl', 'selector.pkl', 'model_metadata.json']
    missing = []
    for file in required_files:
        if not (model_dir / file).exists():
            missing.append(file)
    
    if missing:
        print(f"   ✗ FAIL - Missing files: {missing}")
        sys.exit(1)
    else:
        print(f"   ✓ PASS - All required model files present")
except Exception as e:
    print(f"   ✗ FAIL - Error: {e}")
    sys.exit(1)

print()
print("=" * 70)
print("✓ ALL CHECKS PASSED")
print("=" * 70)
print()
print("The system is ready to use!")
print()
print("Next steps:")
print("  1. Start backend: ./run_with_sudo.sh")
print("  2. Generate traffic: ./generate_traffic.sh")
print("  3. Start frontend: cd ../frontend && npm run dev")
print("  4. Open browser: http://localhost:5173")
print()

