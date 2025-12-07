#!/usr/bin/env python3
"""Check packet capture permissions on macOS"""

import sys
import os
import platform
import socket

print("=" * 70)
print("Packet Capture Permission Checker")
print("=" * 70)
print()

if platform.system() != 'Darwin':
    print("This script is for macOS. On Linux, use: sudo setcap cap_net_raw+eip /usr/bin/python3")
    sys.exit(0)

print("Checking permissions...")
print()

# Check 1: Running as root
if os.geteuid() == 0:
    print("✓ Running as root - packet capture should work")
else:
    print("✗ Not running as root")
    print("  On macOS, packet capture typically requires root privileges")

print()

# Check 2: Raw socket creation
try:
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
    test_socket.close()
    print("✓ Raw socket creation successful")
except PermissionError:
    print("✗ Raw socket creation failed - need root or special permissions")
except Exception as e:
    print(f"✗ Raw socket test error: {e}")

print()

# Check 3: Scapy import
try:
    from scapy.all import get_if_list
    interfaces = get_if_list()
    print(f"✓ Scapy imported successfully")
    print(f"  Available interfaces: {', '.join(interfaces[:5])}...")
except ImportError as e:
    print("✗ Scapy not installed or not in current Python environment")
    print(f"  Error: {e}")
    print("  Make sure you're in the virtual environment:")
    print("    source venv/bin/activate")
    print("    pip install scapy")
except Exception as e:
    print(f"✗ Scapy error: {e}")

print()
print("=" * 70)
print("RECOMMENDED SOLUTION:")
print("=" * 70)
print()
print("Run the backend with sudo:")
print("  sudo python -m app.main")
print()
print("OR use the run script with sudo:")
print("  sudo python run.py")
print()
print("=" * 70)

