#!/bin/bash
# Final comprehensive test of IDS system with heuristic detection

echo "======================================================================"
echo "FINAL IDS SYSTEM TEST"
echo "======================================================================"
echo ""

VM_IP="192.168.64.3"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "📋 PRE-FLIGHT CHECKS"
echo "----------------------------------------------------------------------"

# 1. Check if backend is running
if curl -s http://localhost:8000/api/monitoring/status > /dev/null; then
    echo -e "${GREEN}✓${NC} Backend is running"
else
    echo -e "${RED}✗${NC} Backend is NOT running"
    echo "   Please start it: cd backend && sudo ./run_with_sudo.sh"
    exit 1
fi

# 2. Check if monitoring is running
IS_RUNNING=$(curl -s http://localhost:8000/api/monitoring/status | python3 -c "import sys, json; print(json.load(sys.stdin)['is_running'])")

if [ "$IS_RUNNING" = "True" ]; then
    echo -e "${GREEN}✓${NC} Monitoring is active"
else
    echo -e "${YELLOW}⚠${NC}  Monitoring is stopped - starting it now..."
    curl -s -X POST http://localhost:8000/api/monitoring/start > /dev/null
    sleep 2
    echo -e "${GREEN}✓${NC} Monitoring started"
fi

# 3. Check frontend
if curl -s http://localhost:5173 > /dev/null; then
    echo -e "${GREEN}✓${NC} Frontend is running"
else
    echo -e "${YELLOW}⚠${NC}  Frontend might not be running"
    echo "   Start it: cd frontend && npm run dev"
fi

# 4. Check if VM is reachable
if ping -c 1 -W 1 "$VM_IP" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} VM ($VM_IP) is reachable"
else
    echo -e "${RED}✗${NC} VM is not reachable"
    echo "   Check: multipass list"
    exit 1
fi

echo ""
echo "======================================================================"
echo "🚀 LAUNCHING ATTACK (HTTP Flood - HULK Style)"
echo "======================================================================"
echo ""
echo "Attack Details:"
echo "  Type: HTTP Flood (HULK)"
echo "  Target: http://$VM_IP"
echo "  Threads: 500"
echo "  Duration: 30 seconds"
echo ""
echo "Expected detections:"
echo "  - Heuristic: HTTP Flood / High-rate DoS"
echo "  - Frontend: Attacks should appear in real-time"
echo "  - Logs: '🚨 HEURISTIC DETECTION' messages"
echo ""

read -p "Press ENTER to launch attack..."

# Launch attack in background
python3 /tmp/attack_hulk.py http://$VM_IP 30 > /tmp/attack_output.txt 2>&1 &
ATTACK_PID=$!

echo -e "${GREEN}✓${NC} Attack launched (PID: $ATTACK_PID)"
echo ""
echo "======================================================================"
echo "📊 MONITORING DETECTIONS (30 seconds)"
echo "======================================================================"
echo ""

# Monitor for 30 seconds
for i in {1..6}; do
    sleep 5
    
    # Get stats
    STATS=$(curl -s http://localhost:8000/api/stats/summary)
    TOTAL_FLOWS=$(echo "$STATS" | python3 -c "import sys, json; print(json.load(sys.stdin)['detection']['total_flows'])")
    ATTACKS=$(echo "$STATS" | python3 -c "import sys, json; print(json.load(sys.stdin)['detection']['attack_count'])")
    PACKETS=$(echo "$STATS" | python3 -c "import sys, json; print(json.load(sys.stdin)['packets_captured'])")
    
    echo "[${i}x5s] Flows: $TOTAL_FLOWS | Attacks Detected: $ATTACKS | Packets: $PACKETS"
    
    if [ "$ATTACKS" -gt 0 ]; then
        echo -e "${GREEN}✓ Attacks are being detected!${NC}"
    fi
done

wait $ATTACK_PID 2>/dev/null

echo ""
echo "======================================================================"
echo "📈 FINAL RESULTS"
echo "======================================================================"
echo ""

# Get final stats
FINAL_STATS=$(curl -s http://localhost:8000/api/stats/summary)
echo "$FINAL_STATS" | python3 -m json.tool

TOTAL_FLOWS=$(echo "$FINAL_STATS" | python3 -c "import sys, json; print(json.load(sys.stdin)['detection']['total_flows'])")
ATTACKS=$(echo "$FINAL_STATS" | python3 -c "import sys, json; print(json.load(sys.stdin)['detection']['attack_count'])")
BENIGN=$(echo "$FINAL_STATS" | python3 -c "import sys, json; print(json.load(sys.stdin)['detection']['benign_count'])")
PACKETS=$(echo "$FINAL_STATS" | python3 -c "import sys, json; print(json.load(sys.stdin)['packets_captured'])")

echo ""
echo "======================================================================"
echo "VERDICT"
echo "======================================================================"
echo ""

if [ "$ATTACKS" -gt 0 ]; then
    echo -e "${GREEN}✅ SUCCESS!${NC}"
    echo ""
    echo "   Attacks Detected: $ATTACKS"
    echo "   Total Flows: $TOTAL_FLOWS"
    echo "   Benign Flows: $BENIGN"
    echo "   Packets Captured: $PACKETS"
    echo ""
    echo "   Detection Rate: $(echo "scale=1; $ATTACKS * 100 / $TOTAL_FLOWS" | bc)%"
    echo ""
    echo "🎉 Your IDS system is working correctly!"
    echo ""
    echo "Next steps:"
    echo "  - Check frontend dashboard: http://localhost:5173"
    echo "  - View detections in 'Recent Detections' panel"
    echo "  - Try other attacks: slowloris, goldeneye, etc."
    echo ""
else
    echo -e "${RED}❌ NO ATTACKS DETECTED${NC}"
    echo ""
    echo "   Total Flows: $TOTAL_FLOWS"
    echo "   Packets Captured: $PACKETS"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check backend logs for 'HEURISTIC DETECTION':"
    echo "     tail -50 terminals/9.txt | grep 'HEURISTIC\\|SUSPICIOUS'"
    echo ""
    echo "  2. Verify heuristic_detector.py exists:"
    echo "     ls -la app/services/heuristic_detector.py"
    echo ""
    echo "  3. Check if detection threshold is too high:"
    echo "     grep DETECTION_CONFIDENCE_THRESHOLD app/config.py"
    echo ""
    echo "  4. Re-run the patch:"
    echo "     python3 patch_detection_engine.py"
    echo ""
fi

echo "======================================================================"

# Show attack output
if [ -f /tmp/attack_output.txt ]; then
    echo ""
    echo "Attack tool output:"
    cat /tmp/attack_output.txt
fi

