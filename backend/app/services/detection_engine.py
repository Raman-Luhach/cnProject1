"""Detection Engine - orchestrates the detection pipeline"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, List, Dict
from collections import defaultdict

from app.config import (
    DETECTION_CONFIDENCE_THRESHOLD,
    BATCH_SIZE,
    DETECTION_INTERVAL
)
from app.services.capture.packet_capture import PacketCapture
from app.services.capture.flow_aggregator import FlowAggregator, Flow
from app.services.capture.interface_manager import InterfaceManager
from app.services.feature_extractor import FeatureExtractor
from app.services.ids_model import get_model_service
from app.services.heuristic_detector import detect_attack_heuristic
from app.models.detection import DetectionResult

logger = logging.getLogger(__name__)


class DetectionEngine:
    """Main detection engine that coordinates all components"""
    
    def __init__(self):
        self.is_running = False
        self.start_time: Optional[datetime] = None
        
        # Components
        self.interface_manager = InterfaceManager()
        self.flow_aggregator = FlowAggregator()
        self.feature_extractor = FeatureExtractor()
        self.model_service = get_model_service()
        self.packet_capture: Optional[PacketCapture] = None
        
        # Detection statistics
        self.total_flows = 0
        self.total_detections = 0
        self.benign_count = 0
        self.attack_count = 0
        self.attack_distribution = defaultdict(int)
        
        # Detection callbacks
        self.detection_callbacks = []
        
        # Processing task
        self.processing_task = None
    
    def register_detection_callback(self, callback):
        """Register a callback for detection events"""
        self.detection_callbacks.append(callback)
    
    async def start_monitoring(
        self,
        vm_ip: Optional[str] = None,
        interface: Optional[str] = None
    ) -> bool:
        """Start the detection engine"""
        if self.is_running:
            logger.warning("Detection engine already running")
            return False
        
        try:
            # Check model is loaded
            if not self.model_service.is_loaded:
                logger.error("Model not loaded")
                return False
            
            # Get network interface
            iface = self.interface_manager.get_interface(vm_ip, interface)
            if not iface:
                logger.error("Failed to detect network interface")
                return False
            
            logger.info(f"Using network interface: {iface}")
            
            # Check capture permissions
            if not self.interface_manager.check_capture_permissions():
                logger.warning("May not have capture permissions - some features may not work")
            
            # Create packet capture
            self.packet_capture = PacketCapture(
                interface=iface,
                packet_callback=self._packet_callback,
                vm_ip=vm_ip
            )
            
            # Start packet capture
            self.packet_capture.start()
            
            # Start processing loop
            self.is_running = True
            self.start_time = datetime.now()
            self.processing_task = asyncio.create_task(self._processing_loop())
            
            logger.info("Detection engine started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start detection engine: {e}")
            self.is_running = False
            return False
    
    async def stop_monitoring(self) -> bool:
        """Stop the detection engine"""
        if not self.is_running:
            logger.warning("Detection engine not running")
            return False
        
        try:
            logger.info("Stopping detection engine...")
            
            self.is_running = False
            
            # Stop packet capture
            if self.packet_capture:
                self.packet_capture.stop()
            
            # Cancel processing task
            if self.processing_task:
                self.processing_task.cancel()
                try:
                    await self.processing_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("Detection engine stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping detection engine: {e}")
            return False
    
    def _packet_callback(self, packet_info: Dict):
        """Callback for captured packets"""
        # Add packet to flow aggregator
        completed_flow = self.flow_aggregator.add_packet(packet_info)
        
        # If flow completed, it will be processed in the processing loop
        if completed_flow:
            logger.debug(f"Flow completed: {completed_flow.flow_id}")
    
    async def _processing_loop(self):
        """Main processing loop"""
        logger.info("Processing loop started")
        
        try:
            iteration = 0
            while self.is_running:
                iteration += 1
                
                # Get completed flows (also triggers timeout cleanup)
                flows = self.flow_aggregator.get_completed_flows(limit=BATCH_SIZE)
                
                if flows:
                    logger.info(f"Got {len(flows)} completed flows to process")
                    await self._process_flows(flows)
                else:
                    # Log every 10 seconds if no flows
                    if iteration % 10 == 0:
                        active = self.flow_aggregator.get_active_flow_count()
                        logger.info(f"No completed flows. Active flows: {active}")
                
                # Sleep before next iteration
                await asyncio.sleep(DETECTION_INTERVAL)
                
        except asyncio.CancelledError:
            logger.info("Processing loop cancelled")
        except Exception as e:
            logger.error(f"Error in processing loop: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    async def _process_flows(self, flows: List[Flow]):
        """Process flows through detection pipeline"""
        try:
            logger.info(f"Processing {len(flows)} flows for detection")
            
            # Extract features
            features_df = self.feature_extractor.extract_features_from_flows(flows)
            
            if features_df.empty:
                logger.warning("No features extracted from flows")
                return
            
            logger.debug(f"Extracted features shape: {features_df.shape}")
            
            # Run inference
            predictions, probabilities = self.model_service.predict(features_df)
            
            # Log prediction summary
            prediction_counts = {}
            for pred in predictions:
                prediction_counts[pred] = prediction_counts.get(pred, 0) + 1
            logger.info(f"Predictions: {prediction_counts}")
            
            # Process results
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
                    logger.info(f"ML attack processed: {prediction} (confidence: {confidence:.2%})")
                
        except Exception as e:
            logger.error(f"Error processing flows: {e}")
    
    async def _notify_detection(self, detection: DetectionResult):
        """Notify all registered callbacks of detection"""
        for callback in self.detection_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(detection)
                else:
                    callback(detection)
            except Exception as e:
                logger.error(f"Error in detection callback: {e}")
    
    def get_stats(self) -> Dict:
        """Get detection statistics"""
        uptime = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        
        return {
            'is_running': self.is_running,
            'total_flows': self.total_flows,
            'total_detections': self.total_detections,
            'benign_count': self.benign_count,
            'attack_count': self.attack_count,
            'detection_rate': self.attack_count / self.total_detections if self.total_detections > 0 else 0,
            'attack_distribution': dict(self.attack_distribution),
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'uptime_seconds': uptime,
            'active_flows': self.flow_aggregator.get_active_flow_count(),
            'capture_stats': self.packet_capture.get_stats() if self.packet_capture else {}
        }


# Global detection engine instance
_detection_engine = None


def get_detection_engine() -> DetectionEngine:
    """Get or create global detection engine instance"""
    global _detection_engine
    if _detection_engine is None:
        _detection_engine = DetectionEngine()
    return _detection_engine

