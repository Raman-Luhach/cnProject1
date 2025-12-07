#!/bin/bash

echo "======================================================================"
echo "Checking IDS Monitoring System Status"
echo "======================================================================"

# Check if backend is running
echo -e "\n1. Checking if backend is running..."
if curl -s http://localhost:8000/api/vm/status > /dev/null 2>&1; then
    echo "   ✓ Backend is running on port 8000"
else
    echo "   ✗ Backend is NOT running"
    echo "   Start with: cd backend && ./run_with_sudo.sh"
    exit 1
fi

# Check monitoring status
echo -e "\n2. Checking monitoring status..."
MONITORING_STATUS=$(curl -s http://localhost:8000/api/monitoring/status)
IS_RUNNING=$(echo $MONITORING_STATUS | grep -o '"is_running":[^,}]*' | cut -d':' -f2)

if [ "$IS_RUNNING" = "true" ]; then
    echo "   ✓ Monitoring IS RUNNING"
else
    echo "   ✗ Monitoring is NOT RUNNING"
    echo "   Solution: Click 'Start Monitoring' button in the frontend"
    echo "   Or run: curl -X POST http://localhost:8000/api/monitoring/start"
fi

# Check stats
echo -e "\n3. Checking statistics..."
STATS=$(curl -s http://localhost:8000/api/stats/summary)
echo "$STATS" | python3 -m json.tool 2>/dev/null || echo "$STATS"

TOTAL_FLOWS=$(echo $STATS | grep -o '"total_flows":[0-9]*' | cut -d':' -f2)
TOTAL_DETECTIONS=$(echo $STATS | grep -o '"total_detections":[0-9]*' | cut -d':' -f2)
ACTIVE_FLOWS=$(echo $STATS | grep -o '"active_flows":[0-9]*' | cut -d':' -f2)
PACKETS=$(echo $STATS | grep -o '"packets_captured":[0-9]*' | cut -d':' -f2)

echo -e "\n4. Summary:"
echo "   Total Flows: $TOTAL_FLOWS"
echo "   Total Detections: $TOTAL_DETECTIONS"
echo "   Active Flows: $ACTIVE_FLOWS"
echo "   Packets Captured: $PACKETS"

# Diagnosis
echo -e "\n5. Diagnosis:"
if [ "$IS_RUNNING" != "true" ]; then
    echo "   🔴 ISSUE: Monitoring is not started"
    echo "   ACTION: Click 'Start Monitoring' in the frontend"
elif [ "$PACKETS" = "0" ] || [ -z "$PACKETS" ]; then
    echo "   🟡 WARNING: No packets captured"
    echo "   ACTION: Generate traffic: ping 192.168.64.3"
elif [ "$TOTAL_FLOWS" = "0" ] || [ -z "$TOTAL_FLOWS" ]; then
    echo "   🟡 WARNING: Packets captured but no flows completed"
    echo "   INFO: This is normal if monitoring just started (< 5 seconds)"
    echo "   ACTION: Wait 5-10 seconds or launch an attack"
elif [ "$TOTAL_DETECTIONS" = "0" ] || [ -z "$TOTAL_DETECTIONS" ]; then
    echo "   🟢 OK: Flows are being processed"
    echo "   INFO: No attacks detected yet (all traffic is benign)"
    echo "   ACTION: Launch an attack from the Attack Controls panel"
else
    echo "   🟢 EXCELLENT: System is working! Detections: $TOTAL_DETECTIONS"
fi

echo -e "\n======================================================================"

