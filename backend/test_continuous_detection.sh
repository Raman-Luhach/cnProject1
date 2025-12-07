#!/bin/bash
# Test script to verify continuous detection

echo "======================================================================"
echo "Testing Continuous Attack Detection"
echo "======================================================================"
echo ""

TARGET_IP="192.168.64.3"

# Function to check stats
check_stats() {
    local label=$1
    echo ""
    echo "📊 Statistics $label:"
    stats=$(curl -s http://localhost:8000/api/stats/summary)
    total_flows=$(echo "$stats" | python3 -c "import sys, json; print(json.load(sys.stdin)['detection']['total_flows'])")
    attacks=$(echo "$stats" | python3 -c "import sys, json; print(json.load(sys.stdin)['detection']['attack_count'])")
    packets=$(echo "$stats" | python3 -c "import sys, json; print(json.load(sys.stdin)['packets_captured'])")
    
    echo "   Total Flows: $total_flows"
    echo "   Attacks Detected: $attacks"
    echo "   Packets Captured: $packets"
    echo ""
}

# Initial stats
check_stats "BEFORE attacks"

# Attack 1
echo "🚀 Launching Attack #1 (HULK - 20 seconds)..."
python3 /tmp/attack_hulk.py http://$TARGET_IP 20 2>&1 | head -3 &
ATTACK1_PID=$!

sleep 22

check_stats "AFTER Attack #1"

# Wait for flows to complete
echo "⏳ Waiting 5 seconds for flows to complete..."
sleep 5

check_stats "AFTER 5s wait"

# Attack 2
echo "🚀 Launching Attack #2 (HTTP Flood - 20 seconds)..."
timeout 20 bash /tmp/attack_http_flood.sh 2>&1 | head -3 &
ATTACK2_PID=$!

sleep 22

check_stats "AFTER Attack #2"

# Wait for flows to complete
echo "⏳ Waiting 5 seconds for flows to complete..."
sleep 5

check_stats "AFTER 5s wait (final)"

echo ""
echo "======================================================================"
echo "✅ Test Complete!"
echo "======================================================================"
echo ""
echo "If continuous detection is working:"
echo "  - Total Flows should INCREASE after each attack"
echo "  - Attacks Detected should INCREASE after each attack"
echo "  - Each attack should show NEW detections in logs"
echo ""
echo "Check backend logs for:"
echo "  grep '🚨 HEURISTIC DETECTION' /Users/ramanluhach/.cursor/projects/Users-ramanluhach-cnProject/terminals/9.txt | tail -20"
echo ""
