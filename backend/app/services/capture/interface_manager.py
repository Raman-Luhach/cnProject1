"""Network interface management for packet capture"""

import subprocess
import logging
import os
import platform
import socket
from typing import Optional, List

logger = logging.getLogger(__name__)

# Detect OS
IS_MACOS = platform.system() == 'Darwin'
IS_LINUX = platform.system() == 'Linux'


class InterfaceManager:
    """Manages network interface discovery and permissions"""
    
    def __init__(self):
        self.interface = None
        self.vm_ip = None
    
    def detect_multipass_interface(self) -> Optional[str]:
        """Auto-detect Multipass bridge interface"""
        try:
            # Common multipass interfaces
            candidate_interfaces = ["multipass0", "mpqemubr0", "br-multipass"]
            
            # Get all network interfaces
            if IS_MACOS:
                # Use ifconfig on macOS
                result = subprocess.run(
                    ["ifconfig"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                available_interfaces = []
                current_iface = None
                for line in result.stdout.split('\n'):
                    if line and not line.startswith(' ') and not line.startswith('\t'):
                        # New interface line
                        parts = line.split(':')
                        if len(parts) > 0:
                            current_iface = parts[0].strip()
                            if current_iface:
                                available_interfaces.append(current_iface)
            else:
                # Use ip command on Linux
                result = subprocess.run(
                    ["ip", "link", "show"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                available_interfaces = []
                for line in result.stdout.split('\n'):
                    if ':' in line and not line.startswith(' '):
                        parts = line.split(':')
                        if len(parts) >= 2:
                            iface = parts[1].strip()
                            available_interfaces.append(iface)
            
            logger.info(f"Available interfaces: {available_interfaces}")
            
            # Check for multipass interfaces
            for iface in candidate_interfaces:
                if iface in available_interfaces:
                    logger.info(f"Found Multipass interface: {iface}")
                    return iface
            
            # Try to find bridge interfaces (Multipass uses bridge100, bridge0, etc. on macOS)
            for iface in available_interfaces:
                if 'bridge' in iface.lower():
                    logger.info(f"Found bridge interface: {iface}")
                    return iface
            
            # Try to find any bridge interface (Linux naming)
            for iface in available_interfaces:
                if 'br' in iface.lower() or 'en' in iface.lower():
                    logger.info(f"Found candidate interface: {iface}")
                    return iface
            
            logger.warning("No Multipass interface found, using default")
            return None
            
        except Exception as e:
            logger.error(f"Error detecting interface: {e}")
            return None
    
    def get_interface_for_vm(self, vm_ip: str) -> Optional[str]:
        """Get network interface that routes to VM IP"""
        try:
            if IS_MACOS:
                # On macOS, use route command
                result = subprocess.run(
                    ["route", "-n", "get", vm_ip],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                # Parse output: "interface: en0"
                for line in result.stdout.split('\n'):
                    if 'interface:' in line.lower():
                        parts = line.split(':')
                        if len(parts) >= 2:
                            interface = parts[1].strip()
                            logger.info(f"Found interface for {vm_ip}: {interface}")
                            return interface
            else:
                # Use ip route on Linux
                result = subprocess.run(
                    ["ip", "route", "get", vm_ip],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                # Parse output: "... dev eth0 ..."
                for line in result.stdout.split('\n'):
                    if 'dev' in line:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part == 'dev' and i + 1 < len(parts):
                                interface = parts[i + 1]
                                logger.info(f"Found interface for {vm_ip}: {interface}")
                                return interface
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding interface for VM: {e}")
            return None
    
    def check_capture_permissions(self) -> bool:
        """Check if we have permissions for packet capture"""
        try:
            # Check if running as root
            if os.geteuid() == 0:
                logger.info("Running as root, capture permissions OK")
                return True
            
            if IS_MACOS:
                # On macOS, check if we can create a raw socket
                try:
                    test_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
                    test_socket.close()
                    logger.info("Raw socket creation successful, capture permissions OK")
                    return True
                except PermissionError:
                    logger.warning("No capture permissions - raw socket creation failed")
                    logger.info("Hint: On macOS, you may need to grant Full Disk Access or run with sudo")
                    return False
            else:
                # On Linux, check for CAP_NET_RAW capability
                try:
                    result = subprocess.run(
                        ["getcap", "/usr/bin/python3"],
                        capture_output=True,
                        text=True
                    )
                    
                    if "cap_net_raw" in result.stdout:
                        logger.info("Python has CAP_NET_RAW, capture permissions OK")
                        return True
                except FileNotFoundError:
                    pass
                
                logger.warning("No capture permissions detected")
                logger.info("Hint: Run with sudo or: sudo setcap cap_net_raw+eip /usr/bin/python3")
                return False
            
        except Exception as e:
            logger.error(f"Error checking permissions: {e}")
            return False
    
    def get_interface(self, vm_ip: Optional[str] = None, interface_name: Optional[str] = None) -> Optional[str]:
        """Get the network interface to use for capture"""
        
        # If explicit interface provided, use it
        if interface_name:
            logger.info(f"Using specified interface: {interface_name}")
            self.interface = interface_name
            return interface_name
        
        # If VM IP provided, find interface that routes to it
        if vm_ip:
            iface = self.get_interface_for_vm(vm_ip)
            if iface:
                self.interface = iface
                self.vm_ip = vm_ip
                return iface
        
        # Auto-detect multipass interface
        iface = self.detect_multipass_interface()
        if iface:
            self.interface = iface
            return iface
        
        # Fallback: try to get default interface
        if IS_MACOS:
            # On macOS, try to get default route interface
            try:
                result = subprocess.run(
                    ["route", "-n", "get", "default"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                for line in result.stdout.split('\n'):
                    if 'interface:' in line.lower():
                        parts = line.split(':')
                        if len(parts) >= 2:
                            default_iface = parts[1].strip()
                            logger.info(f"Using default route interface: {default_iface}")
                            self.interface = default_iface
                            return default_iface
            except Exception as e:
                logger.debug(f"Could not get default interface: {e}")
        
        # Last resort: try common interface names
        common_interfaces = ["en0", "eth0", "wlan0", "en1"]
        for iface in common_interfaces:
            try:
                # Try to get interface address to verify it exists
                if IS_MACOS:
                    result = subprocess.run(
                        ["ifconfig", iface],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        logger.info(f"Found interface: {iface}")
                        self.interface = iface
                        return iface
            except Exception:
                continue
        
        # Final fallback - but warn that "any" doesn't work on macOS
        if IS_MACOS:
            logger.error("Could not find suitable network interface. Please specify one manually.")
            logger.error("On macOS, you cannot use 'any' interface. Try: en0, en1, or the Multipass bridge interface.")
            return None
        else:
            logger.warning("Using fallback interface: any")
            return "any"
    
    def list_interfaces(self) -> List[str]:
        """List all available network interfaces"""
        try:
            if IS_MACOS:
                result = subprocess.run(
                    ["ifconfig"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                interfaces = []
                for line in result.stdout.split('\n'):
                    if line and not line.startswith(' ') and not line.startswith('\t'):
                        parts = line.split(':')
                        if len(parts) > 0:
                            iface = parts[0].strip()
                            if iface:
                                interfaces.append(iface)
            else:
                result = subprocess.run(
                    ["ip", "-o", "link", "show"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                interfaces = []
                for line in result.stdout.split('\n'):
                    if line.strip():
                        parts = line.split(':')
                        if len(parts) >= 2:
                            iface = parts[1].strip()
                            interfaces.append(iface)
            
            return interfaces
            
        except Exception as e:
            logger.error(f"Error listing interfaces: {e}")
            return []

