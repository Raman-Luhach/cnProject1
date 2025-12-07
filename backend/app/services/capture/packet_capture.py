"""Packet capture using Scapy"""

import logging
import asyncio
from typing import Optional, Callable, Dict
from scapy.all import sniff, IP, TCP, UDP, ICMP
from scapy.packet import Packet
import threading

logger = logging.getLogger(__name__)


class PacketCapture:
    """Captures network packets using Scapy"""
    
    def __init__(
        self,
        interface: str = "any",
        packet_callback: Optional[Callable] = None,
        vm_ip: Optional[str] = None,
        buffer_size: int = 1000
    ):
        self.interface = interface
        self.packet_callback = packet_callback
        self.vm_ip = vm_ip
        self.buffer_size = buffer_size
        self.is_capturing = False
        self.capture_thread = None
        self.packet_count = 0
        self.byte_count = 0
        
    def _extract_packet_info(self, packet: Packet) -> Optional[Dict]:
        """Extract relevant information from packet"""
        try:
            if not packet.haslayer(IP):
                return None
            
            ip_layer = packet[IP]
            
            packet_info = {
                'src_ip': ip_layer.src,
                'dst_ip': ip_layer.dst,
                'protocol': 'unknown',
                'src_port': 0,
                'dst_port': 0,
                'length': len(packet),
                'flags': {},
                'timestamp': packet.time if hasattr(packet, 'time') else 0
            }
            
            # TCP
            if packet.haslayer(TCP):
                tcp_layer = packet[TCP]
                packet_info['protocol'] = 'TCP'
                packet_info['src_port'] = tcp_layer.sport
                packet_info['dst_port'] = tcp_layer.dport
                
                # TCP flags
                flags = tcp_layer.flags
                packet_info['flags'] = {
                    'S': bool(flags & 0x02),  # SYN
                    'A': bool(flags & 0x10),  # ACK
                    'F': bool(flags & 0x01),  # FIN
                    'R': bool(flags & 0x04),  # RST
                    'P': bool(flags & 0x08),  # PSH
                    'U': bool(flags & 0x20),  # URG
                }
            
            # UDP
            elif packet.haslayer(UDP):
                udp_layer = packet[UDP]
                packet_info['protocol'] = 'UDP'
                packet_info['src_port'] = udp_layer.sport
                packet_info['dst_port'] = udp_layer.dport
            
            # ICMP
            elif packet.haslayer(ICMP):
                packet_info['protocol'] = 'ICMP'
            
            # Other IP protocols
            else:
                packet_info['protocol'] = str(ip_layer.proto)
            
            return packet_info
            
        except Exception as e:
            logger.error(f"Error extracting packet info: {e}")
            return None
    
    def _should_capture_packet(self, packet_info: Dict) -> bool:
        """Check if packet should be captured"""
        if not self.vm_ip:
            return True
        
        # Filter packets to/from VM
        return (packet_info['src_ip'] == self.vm_ip or 
                packet_info['dst_ip'] == self.vm_ip)
    
    def _packet_handler(self, packet: Packet):
        """Handle captured packet"""
        try:
            packet_info = self._extract_packet_info(packet)
            
            if packet_info and self._should_capture_packet(packet_info):
                self.packet_count += 1
                self.byte_count += packet_info['length']
                
                # Log first packet
                if self.packet_count == 1:
                    logger.info(f"✓ First packet captured: {packet_info['src_ip']} → {packet_info['dst_ip']}")
                
                # Call callback if provided
                if self.packet_callback:
                    self.packet_callback(packet_info)
                
                # Log every 100 packets
                if self.packet_count % 100 == 0:
                    logger.info(f"Captured {self.packet_count} packets ({self.byte_count / 1024 / 1024:.2f} MB)")
        
        except Exception as e:
            logger.error(f"Error handling packet: {e}")
    
    def _capture_loop(self):
        """Main capture loop (runs in separate thread)"""
        try:
            logger.info(f"Starting packet capture on {self.interface}")
            if self.vm_ip:
                logger.info(f"Filtering traffic to/from {self.vm_ip}")
            
            # Build BPF filter
            bpf_filter = None
            if self.vm_ip:
                bpf_filter = f"host {self.vm_ip}"
            
            # Test if we can actually capture before starting
            try:
                from scapy.all import get_if_list
                available_interfaces = get_if_list()
                if self.interface not in available_interfaces and self.interface != "any":
                    logger.warning(f"Interface {self.interface} not in available interfaces: {available_interfaces}")
            except Exception as e:
                logger.debug(f"Could not list interfaces: {e}")
            
            # Start sniffing with error handling
            try:
                # Use stop_filter to control when to stop (no timeout)
                sniff(
                    iface=self.interface,
                    prn=self._packet_handler,
                    store=False,
                    filter=bpf_filter,
                    stop_filter=lambda x: not self.is_capturing
                )
            except OSError as e:
                if "BIOCSETIF" in str(e) or "Operation not permitted" in str(e):
                    logger.error("=" * 70)
                    logger.error("PACKET CAPTURE PERMISSION ERROR")
                    logger.error("=" * 70)
                    logger.error("On macOS, packet capture requires special permissions.")
                    logger.error("")
                    logger.error("SOLUTION 1 (Recommended for development):")
                    logger.error("  Run the backend with sudo:")
                    logger.error("    sudo python -m app.main")
                    logger.error("")
                    logger.error("SOLUTION 2 (For production):")
                    logger.error("  Grant Terminal/Python Full Disk Access:")
                    logger.error("  1. System Settings > Privacy & Security > Full Disk Access")
                    logger.error("  2. Add Terminal.app or your Python interpreter")
                    logger.error("")
                    logger.error("SOLUTION 3 (Alternative):")
                    logger.error("  Use tcpdump with sudo and pipe to Python")
                    logger.error("=" * 70)
                else:
                    logger.error(f"OS Error during capture: {e}")
                self.is_capturing = False
                return
            
            logger.info(f"Packet capture stopped. Total packets: {self.packet_count}")
            
        except PermissionError as e:
            logger.error("=" * 70)
            logger.error("PERMISSION DENIED")
            logger.error("=" * 70)
            logger.error(f"Error: {e}")
            logger.error("")
            logger.error("On macOS, you need to:")
            logger.error("  1. Run with sudo: sudo python -m app.main")
            logger.error("  2. OR grant Full Disk Access in System Settings")
            logger.error("=" * 70)
            self.is_capturing = False
        except Exception as e:
            logger.error(f"Capture error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.is_capturing = False
    
    def start(self):
        """Start packet capture"""
        if self.is_capturing:
            logger.warning("Capture already running")
            return
        
        self.is_capturing = True
        self.packet_count = 0
        self.byte_count = 0
        
        # Start capture in separate thread
        self.capture_thread = threading.Thread(
            target=self._capture_loop,
            daemon=True
        )
        self.capture_thread.start()
        
        # Give it a moment to start and check for immediate errors
        import time
        time.sleep(0.5)
        
        if not self.is_capturing:
            logger.error("Packet capture failed to start - check permissions")
            return
        
        logger.info("Packet capture started")
        
        # Log a reminder after a few seconds if no packets captured
        def check_capture():
            time.sleep(5)
            if self.is_capturing and self.packet_count == 0:
                logger.warning("No packets captured yet. This may indicate:")
                logger.warning("  1. No traffic on the interface")
                logger.warning("  2. Permission issues (run with sudo on macOS)")
                logger.warning("  3. Interface not receiving traffic")
        
        threading.Thread(target=check_capture, daemon=True).start()
    
    def stop(self):
        """Stop packet capture"""
        if not self.is_capturing:
            logger.warning("Capture not running")
            return
        
        logger.info("Stopping packet capture...")
        self.is_capturing = False
        
        # Wait for thread to finish (with timeout)
        if self.capture_thread:
            self.capture_thread.join(timeout=5)
        
        logger.info(f"Capture stopped. Total: {self.packet_count} packets, {self.byte_count / 1024 / 1024:.2f} MB")
    
    def is_running(self) -> bool:
        """Check if capture is running"""
        return self.is_capturing
    
    def get_stats(self) -> Dict:
        """Get capture statistics"""
        return {
            'is_running': self.is_capturing,
            'interface': self.interface,
            'vm_ip': self.vm_ip,
            'packet_count': self.packet_count,
            'byte_count': self.byte_count,
            'megabytes': round(self.byte_count / 1024 / 1024, 2)
        }

