#!/usr/bin/env python3
"""Test if Scapy can capture packets on bridge100"""

import sys
import time
from scapy.all import sniff, IP

print("=" * 70)
print("SCAPY PACKET CAPTURE TEST")
print("=" * 70)

packet_count = 0

def packet_handler(packet):
    global packet_count
    packet_count += 1
    if packet.haslayer(IP):
        print(f"✓ Packet #{packet_count}: {packet[IP].src} → {packet[IP].dst}")
    else:
        print(f"✓ Packet #{packet_count}: Non-IP packet")

print(f"\n🔍 Starting capture on bridge100...")
print(f"📊 Will capture for 5 seconds or until 10 packets...")
print(f"🎯 Filter: host 192.168.64.2")
print(f"\n⚠️  IMPORTANT: Run in another terminal: ping -c 5 192.168.64.2")
print()

try:
    # Capture packets
    sniff(
        iface="bridge100",
        prn=packet_handler,
        store=False,
        filter="host 192.168.64.2",
        timeout=5,
        count=10
    )
    
    print()
    print("=" * 70)
    if packet_count > 0:
        print(f"✅ SUCCESS: Captured {packet_count} packets!")
        print("   Packet capture is working correctly.")
    else:
        print(f"❌ FAILURE: Captured {packet_count} packets.")
        print("   Possible issues:")
        print("   1. Not running as root (need sudo)")
        print("   2. No traffic to/from 192.168.64.2")
        print("   3. BPF filter issue")
        print("   4. Interface not in promiscuous mode")
    print("=" * 70)
    
except PermissionError:
    print("\n❌ PERMISSION ERROR: Run with sudo!")
    print(f"   sudo {' '.join(sys.argv)}")
except Exception as e:
    print(f"\n❌ ERROR: {e}")

sys.exit(0 if packet_count > 0 else 1)

