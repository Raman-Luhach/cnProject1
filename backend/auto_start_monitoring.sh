#!/bin/bash

echo "======================================================================"
echo "Auto-Starting IDS Monitoring"
echo "======================================================================"

echo -e "\n1. Checking if backend is running..."
if ! curl -s http://localhost:8000/api/vm/status > /dev/null 2>&1; then
    echo "   ✗ Backend is not running!"
    echo "   Please start it first: cd backend && ./run_with_sudo.sh"
    exit 1
fi

echo "   ✓ Backend is running"

echo -e "\n2. Starting monitoring..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/monitoring/start)
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"

SUCCESS=$(echo $RESPONSE | grep -o '"success":[^,}]*' | cut -d':' -f2)

if [ "$SUCCESS" = "true" ]; then
    echo -e "\n   ✓ Monitoring started successfully!"
    echo ""
    echo "======================================================================"
    echo "System is now monitoring network traffic!"
    echo "======================================================================"
    echo ""
    echo "What happens next:"
    echo "  1. Packets are being captured in real-time"
    echo "  2. Flows are being aggregated (completing every 2-5 seconds)"
    echo "  3. ML model is analyzing traffic"
    echo "  4. Attacks will be detected and displayed"
    echo ""
    echo "To see detections:"
    echo "  - Open http://localhost:5173 in your browser"
    echo "  - Launch an attack from the Attack Controls panel"
    echo "  - Or generate traffic: ping 192.168.64.3"
    echo ""
    echo "To check status:"
    echo "  ./check_monitoring_status.sh"
    echo ""
else
    echo -e "\n   ✗ Failed to start monitoring"
    echo "   Check backend logs for errors"
fi

