#!/usr/bin/env python3
"""
Patch the detection engine to add heuristic detection
"""

import sys

# Read the current file
with open('app/services/detection_engine.py', 'r') as f:
    content = f.read()

# 1. Add import
if 'from app.services.heuristic_detector import detect_attack_heuristic' not in content:
    # Find the imports section
    import_line = 'from app.services.ids_model import get_model_service'
    content = content.replace(
        import_line,
        import_line + '\nfrom app.services.heuristic_detector import detect_attack_heuristic'
    )
    print("✓ Added heuristic_detector import")

# 2. Replace the flow processing logic
old_logic = """            # Process results
            for i, flow in enumerate(flows):
                prediction = predictions[i]
                confidence = float(probabilities[i].max())
                
                # Update statistics
                self.total_flows += 1
                self.total_detections += 1
                
                is_attack = self.model_service.is_attack(prediction)
                
                # Log individual predictions with more detail
                if is_attack or confidence > 0.3:  # Log attacks and uncertain predictions
                    logger.info(f"Flow {flow.src_ip}:{flow.src_port} → {flow.dst_ip}:{flow.dst_port}: "
                              f"{prediction} (conf: {confidence:.1%}), packets: {flow.total_packets}")
                
                if is_attack:
                    self.attack_count += 1
                    logger.warning(f"🚨 ATTACK DETECTED: {prediction} (confidence: {confidence:.1%}) "
                                 f"from {flow.src_ip}:{flow.src_port} → {flow.dst_ip}:{flow.dst_port}")
                    self.attack_distribution[prediction] += 1
                else:
                    self.benign_count += 1
                
                # Create detection result - now includes benign if high confidence
                # This helps verify the system is working even when traffic is benign
                if is_attack and confidence >= DETECTION_CONFIDENCE_THRESHOLD:
                    detection = DetectionResult(
                        flow_id=flow.flow_id,
                        timestamp=datetime.now(),
                        prediction=prediction,
                        confidence=confidence,
                        probabilities=probabilities[i].tolist(),
                        src_ip=flow.src_ip,
                        dst_ip=flow.dst_ip,
                        src_port=flow.src_port,
                        dst_port=flow.dst_port,
                        protocol=flow.protocol,
                        packet_count=flow.total_packets,
                        byte_count=flow.total_bytes,
                        duration=flow.duration,
                        is_attack=True
                    )
                    
                    # Notify callbacks
                    logger.info(f"Notifying callbacks for attack: {prediction}")
                    await self._notify_detection(detection)
                    
                    logger.info(f"Attack processed: {prediction} (confidence: {confidence:.2%})")"""

new_logic = """            # Process results
            class_names = self.model_service.get_class_names()
            for i, flow in enumerate(flows):
                prediction = predictions[i]
                confidence = float(probabilities[i].max())
                
                # Update statistics
                self.total_flows += 1
                self.total_detections += 1
                
                is_attack = self.model_service.is_attack(prediction)
                
                # Check for suspicious activity (any attack probability > 10%)
                attack_probs = {}
                for j, prob in enumerate(probabilities[i]):
                    if prob > 0.10 and class_names[j] != 'Benign':
                        attack_probs[class_names[j]] = float(prob)
                
                # HEURISTIC DETECTION FIRST (rule-based)
                is_heuristic_attack, h_type, h_conf, h_reason = detect_attack_heuristic(flow)
                
                if is_heuristic_attack:
                    logger.warning(f"🚨 HEURISTIC DETECTION: {h_type} ({h_conf:.1%})")
                    logger.warning(f"   {flow.src_ip}:{flow.src_port} → {flow.dst_ip}:{flow.dst_port}")
                    logger.warning(f"   Reason: {h_reason}")
                    logger.warning(f"   Packets: {flow.total_packets}, Bytes: {flow.total_bytes}, Duration: {flow.duration:.2f}s")
                    
                    # Send heuristic detection to frontend
                    detection = DetectionResult(
                        flow_id=flow.flow_id,
                        timestamp=datetime.now(),
                        prediction=f"Heuristic: {h_type}",
                        confidence=h_conf,
                        probabilities=[h_conf] + [0.0] * (len(class_names) - 1),
                        src_ip=flow.src_ip,
                        dst_ip=flow.dst_ip,
                        src_port=flow.src_port,
                        dst_port=flow.dst_port,
                        protocol=flow.protocol,
                        packet_count=flow.total_packets,
                        byte_count=flow.total_bytes,
                        duration=flow.duration,
                        is_attack=True
                    )
                    
                    self.attack_count += 1
                    self.attack_distribution[h_type] += 1
                    await self._notify_detection(detection)
                    continue  # Skip ML processing if heuristic caught it
                
                # Log suspicious activity (ML sees attack patterns but not confident)
                if attack_probs:
                    logger.warning(f"⚠️  SUSPICIOUS ACTIVITY: {flow.src_ip}:{flow.src_port} → {flow.dst_ip}:{flow.dst_port}")
                    logger.warning(f"   Attack probabilities: {attack_probs}")
                    logger.warning(f"   ML prediction: {prediction} ({confidence:.1%})")
                
                # Log individual predictions
                if is_attack or confidence > 0.3 or attack_probs:
                    logger.info(f"Flow {flow.src_ip}:{flow.src_port} → {flow.dst_ip}:{flow.dst_port}: "
                              f"{prediction} (conf: {confidence:.1%}), packets: {flow.total_packets}")
                
                # ML-based detection
                if is_attack:
                    self.attack_count += 1
                    logger.warning(f"🚨 ML ATTACK DETECTED: {prediction} (confidence: {confidence:.1%}) "
                                 f"from {flow.src_ip}:{flow.src_port} → {flow.dst_ip}:{flow.dst_port}")
                    self.attack_distribution[prediction] += 1
                else:
                    self.benign_count += 1
                
                # Create detection result for ML detections
                if is_attack and confidence >= DETECTION_CONFIDENCE_THRESHOLD:
                    detection = DetectionResult(
                        flow_id=flow.flow_id,
                        timestamp=datetime.now(),
                        prediction=prediction,
                        confidence=confidence,
                        probabilities=probabilities[i].tolist(),
                        src_ip=flow.src_ip,
                        dst_ip=flow.dst_ip,
                        src_port=flow.src_port,
                        dst_port=flow.dst_port,
                        protocol=flow.protocol,
                        packet_count=flow.total_packets,
                        byte_count=flow.total_bytes,
                        duration=flow.duration,
                        is_attack=True
                    )
                    
                    await self._notify_detection(detection)
                    logger.info(f"ML attack processed: {prediction} (confidence: {confidence:.2%})")"""

if old_logic in content:
    content = content.replace(old_logic, new_logic)
    print("✓ Patched flow processing logic")
else:
    print("✗ Could not find exact match - manual edit required")
    sys.exit(1)

# Write back
with open('app/services/detection_engine.py', 'w') as f:
    f.write(content)

print("\n✅ Detection engine patched successfully!")
print("\nNext steps:")
print("  1. Restart the backend (monitoring will auto-restart)")
print("  2. Launch an attack: python3 /tmp/attack_hulk.py http://192.168.64.3 30")
print("  3. Watch for '🚨 HEURISTIC DETECTION' in the logs")

