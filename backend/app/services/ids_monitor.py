"""
Real-Time IDS Monitoring Service
"""
import sys
import os
import time
import numpy as np
from scapy.all import sniff, IP, TCP, UDP
from collections import defaultdict
from threading import Thread, Lock
import pandas as pd

from app.services.feature_extractor import NetworkFlowFeatureExtractor

# Import use_model from the model directory
def load_use_model(model_dir):
    """Dynamically import use_model from the model directory"""
    import importlib.util
    use_model_path = os.path.join(model_dir, 'use_model.py')
    if not os.path.exists(use_model_path):
        raise ValueError(f"use_model.py not found in {model_dir}")
    
    spec = importlib.util.spec_from_file_location("use_model", use_model_path)
    use_model_module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, model_dir)  # Add model dir to path for imports
    spec.loader.exec_module(use_model_module)
    return use_model_module.IDSModel


class RealTimeIDSMonitor:
    """Real-time IDS monitoring with packet capture and ML inference"""
    
    def __init__(self, model_dir, target_vm_ip=None, interface=None):
        print("Initializing IDS Monitor...")
        print(f"Model directory: {model_dir}")
        print(f"Model directory exists: {os.path.exists(model_dir)}")
        
        # Verify model directory
        if not os.path.exists(model_dir):
            raise ValueError(f"Model directory does not exist: {model_dir}")
        
        # Load ML model
        try:
            IDSModel = load_use_model(model_dir)
            self.ids_model = IDSModel(model_dir)
            print("✅ Model loaded successfully in IDS Monitor")
        except Exception as e:
            print(f"Error loading model: {e}")
            import traceback
            traceback.print_exc()
            raise
        
        # Configuration
        self.target_vm_ip = target_vm_ip
        self.interface = interface
        
        # Feature extractor
        self.feature_extractor = NetworkFlowFeatureExtractor()
        
        # Flow tracking
        self.flows = defaultdict(lambda: {
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
            'end_time': None,
            'src_ip': None,
            'dst_ip': None,
            'src_port': None,
            'dest_port': None,
            'protocol': None
        })
        
        self.lock = Lock()
        self.window_size = 5  # seconds
        self.is_running = False
        
        # Callbacks
        self.attack_callback = None
        self.benign_callback = None
        
        # Analysis thread
        self.analysis_thread = None
    
    def set_callbacks(self, attack_callback=None, benign_callback=None):
        """Set callbacks for attack/benign detection"""
        self.attack_callback = attack_callback
        self.benign_callback = benign_callback
    
    def process_packet(self, packet):
        """Process captured packets"""
        if not packet.haslayer(IP):
            return
            
        ip = packet[IP]
        
        # Filter for target VM if specified
        if self.target_vm_ip and self.target_vm_ip not in [ip.src, ip.dst]:
            return
        
        # Track packet count silently
        if not hasattr(self, '_packet_count'):
            self._packet_count = 0
        self._packet_count += 1
        
        # Determine flow key and direction
        if packet.haslayer(TCP):
            tcp = packet[TCP]
            flow_key = (ip.src, ip.dst, tcp.sport, tcp.dport, 'TCP')
            direction = 'fwd' if ip.dst == self.target_vm_ip else 'bwd'
            flags = int(tcp.flags) if hasattr(tcp, 'flags') else 0
        elif packet.haslayer(UDP):
            udp = packet[UDP]
            flow_key = (ip.src, ip.dst, udp.sport, udp.dport, 'UDP')
            direction = 'fwd' if ip.dst == self.target_vm_ip else 'bwd'
            flags = 0
        else:
            return
        
        # Update flow
        with self.lock:
            flow = self.flows[flow_key]
            if flow['start_time'] is None:
                flow['start_time'] = time.time()
                flow['src_ip'] = ip.src
                flow['dst_ip'] = ip.dst
                flow['src_port'] = flow_key[2]
                flow['dest_port'] = flow_key[3]
                flow['protocol'] = flow_key[4]
            
            flow['end_time'] = time.time()
            packet_len = len(packet)
            
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
            
            if flags:
                flow['flags'].append(flags)
    
    def analyze_flows(self):
        """Periodically analyze flows"""
        print("🔍 Flow analysis started")
        analysis_count = 0
        total_analyzed = 0
        total_attacks = 0
        
        while self.is_running:
            time.sleep(self.window_size)
            analysis_count += 1
            
            with self.lock:
                flows_to_analyze = dict(self.flows)
                self.flows.clear()
                current_packet_count = getattr(self, '_packet_count', 0)
            
            if not flows_to_analyze:
                # Show status every 30 seconds
                if analysis_count % 6 == 0:
                    print(f"📊 Status: {current_packet_count} packets captured | Waiting for traffic...")
                continue
            
            flows_analyzed = 0
            attacks_found = 0
            
            # Only analyze flows with minimum packets (at least 5 packets)
            for flow_key, flow_data in flows_to_analyze.items():
                if flow_data['start_time'] is None:
                    continue
                
                total_packets = len(flow_data['fwd_packets']) + len(flow_data['bwd_packets'])
                if total_packets < 5:  # Skip flows with too few packets
                    continue
                    
                try:
                    src_ip = flow_data['src_ip']
                    dst_ip = flow_data['dst_ip']
                    src_port = flow_data['src_port']
                    dst_port = flow_data['dest_port']
                    protocol = flow_data['protocol']
                    fwd_packets = len(flow_data['fwd_packets'])
                    bwd_packets = len(flow_data['bwd_packets'])
                    total_bytes = flow_data['fwd_bytes'] + flow_data['bwd_bytes']
                    
                    # Extract features
                    features_df = self.feature_extractor.extract_features(flow_key, flow_data)
                    if features_df is None:
                        continue
                    
                    # Predict
                    predictions, probabilities = self.ids_model.predict(features_df)
                    prediction = predictions[0]
                    confidence = float(np.max(probabilities[0]))
                    
                    # Create detection event
                    detection_data = {
                        'type': prediction,
                        'confidence': confidence,
                        'source_ip': flow_data['src_ip'],
                        'dest_ip': flow_data['dst_ip'],
                        'source_port': flow_data['src_port'],
                        'dest_port': flow_data['dest_port'],
                        'protocol': flow_data['protocol'],
                        'packets': len(flow_data['fwd_packets']) + len(flow_data['bwd_packets']),
                        'bytes': flow_data['fwd_bytes'] + flow_data['bwd_bytes'],
                        'timestamp': time.time()
                    }
                    
                    flows_analyzed += 1
                    
                    # Handle results
                    if prediction != 'Benign':
                        attacks_found += 1
                        print(f"🚨 ATTACK: {prediction} ({confidence:.1%}) | {src_ip}:{src_port} → {dst_ip}:{dst_port} | {total_packets} pkts, {total_bytes:,} bytes")
                        
                        if self.attack_callback:
                            self.attack_callback(detection_data)
                    else:
                        # Only log benign if confidence is low (might be misclassified)
                        if confidence < 0.95:
                            print(f"⚠️  Low confidence benign: {confidence:.1%} | {src_ip}:{src_port} → {dst_ip}:{dst_port}")
                        if self.benign_callback:
                            self.benign_callback(detection_data)
                        
                except Exception as e:
                    # Only log errors, not full traceback
                    print(f"❌ Error analyzing flow: {e}")
            
            # Summary every analysis cycle
            if flows_analyzed > 0:
                total_analyzed += flows_analyzed
                total_attacks += attacks_found
                print(f"📊 Analyzed {flows_analyzed} flows ({attacks_found} attacks) | Total: {total_analyzed} flows, {total_attacks} attacks detected")
    
    def start(self):
        """Start monitoring"""
        if self.is_running:
            print("Monitoring is already running")
            return
        
        self.is_running = True
        print(f"\n{'='*60}")
        print("Real-Time IDS Monitoring Started")
        print(f"{'='*60}")
        if self.target_vm_ip:
            print(f"Target VM IP: {self.target_vm_ip}")
        print(f"Interface: {self.interface or 'default'}")
        print(f"{'='*60}\n")
        
        # Start analysis thread
        self.analysis_thread = Thread(target=self.analyze_flows, daemon=True)
        self.analysis_thread.start()
        
        # Start packet capture in separate thread
        capture_thread = Thread(target=self._capture_packets, daemon=True)
        capture_thread.start()
    
    def _capture_packets(self):
        """Capture packets (runs in separate thread)"""
        try:
            # Build filter to capture traffic to/from target VM
            if self.target_vm_ip:
                # Capture packets where target VM is source or destination
                filter_str = f"host {self.target_vm_ip}"
            else:
                filter_str = None
            
            print(f"📡 Capturing packets on {self.interface}" + (f" (filter: {filter_str})" if filter_str else ""))
            
            sniff(
                prn=self.process_packet, 
                iface=self.interface, 
                store=False, 
                filter=filter_str,
                stop_filter=lambda x: not self.is_running
            )
        except Exception as e:
            print(f"❌ Packet capture error: {e}")
            self.is_running = False
    
    def stop(self):
        """Stop monitoring"""
        if not self.is_running:
            print("⚠️  Monitoring is not running")
            return
        
        print(f"\n{'='*60}")
        print("🛑 Stopping IDS Monitoring...")
        print(f"{'='*60}\n")
        
        self.is_running = False
        
        # Wait for threads to finish (with timeout)
        if self.analysis_thread and self.analysis_thread.is_alive():
            self.analysis_thread.join(timeout=2.0)
        
        # Clear flows
        with self.lock:
            self.flows.clear()
        
        print("✅ IDS Monitoring stopped successfully\n")

