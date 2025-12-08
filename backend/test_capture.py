#!/usr/bin/env python3
"""Test packet capture independently"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from scapy.all import sniff, IP
import time

print("=" * 70)
print("Testing Packet Capture")
print("=" * 70)
print()

VM_IP = "192.168.64.3"
INTERFACE = "bridge100"
DURATION = 10

packet_count = 0

def packet_handler(packet):
    global packet_count
    if packet.haslayer(IP):
        ip = packet[IP]
        packet_count += 1
        print(f"Packet {packet_count}: {ip.src} → {ip.dst}")

print(f"Capturing packets on {INTERFACE} for {DURATION} seconds...")
print(f"Filtering traffic to/from {VM_IP}")
print()
print("Generating traffic in another terminal:")
print(f"  ping {VM_IP}")
print()

try:
    sniff(
        iface=INTERFACE,
        prn=packet_handler,
        filter=f"host {VM_IP}",
        timeout=DURATION,
        store=False
    )
except PermissionError:
    print("\n" + "=" * 70)
    print("ERROR: Permission denied!")
    print("=" * 70)
    print("Run with sudo:")
    print(f"  sudo python {__file__}")
    sys.exit(1)
except Exception as e:
    print(f"\nERROR: {e}")
    sys.exit(1)

print()
print("=" * 70)
print(f"Captured {packet_count} packets")
print("=" * 70)

if packet_count == 0:
    print()
    print("No packets captured. Possible reasons:")
    print(f"  1. No traffic on {INTERFACE}")
    print(f"  2. VM {VM_IP} is not sending/receiving traffic")
    print(f"  3. Filter 'host {VM_IP}' is too restrictive")
    print()
    print("Try generating traffic:")
    print(f"  ping {VM_IP}")
else:
    print()
    print("✓ Packet capture is working!")

