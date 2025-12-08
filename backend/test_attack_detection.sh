#!/bin/bash

echo "======================================================================"
echo "Testing Attack Detection Pipeline"
echo "======================================================================"

# Check monitoring is running
echo -e "\n1. Verifying monitoring is running..."
IS_RUNNING=$(curl -s http://localhost:8000/api/monitoring/status | grep -o '"is_running":true')
if [ -z "$IS_RUNNING" ]; then
    echo "   ✗ Monitoring is not running"
    echo "   Starting it now..."
    curl -s -X POST http://localhost:8000/api/monitoring/start > /dev/null
    sleep 2
fi
echo "   ✓ Monitoring is running"

# Get list of available attacks
echo -e "\n2. Getting available attacks..."
ATTACKS=$(curl -s http://localhost:8000/api/attacks/list)
FIRST_ATTACK=$(echo $ATTACKS | python3 -c "import sys, json; attacks=json.load(sys.stdin); print(attacks[0]['name'] if attacks else '')" 2>/dev/null)
echo "   Available: $(echo $ATTACKS | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null) attacks"
echo "   Using: $FIRST_ATTACK"

# Launch attack
echo -e "\n3. Launching attack..."
ATTACK_RESPONSE=$(curl -s -X POST http://localhost:8000/api/attacks/start \
  -H "Content-Type: application/json" \
  -d "{
    \"attack_type\": \"$FIRST_ATTACK\",
    \"target_ip\": \"192.168.64.3\",
    \"target_port\": 80,
    \"duration\": 30,
    \"intensity\": \"medium\"
  }")

echo "$ATTACK_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$ATTACK_RESPONSE"

ATTACK_ID=$(echo $ATTACK_RESPONSE | grep -o '"attack_id":"[^"]*"' | cut -d'"' -f4)

if [ -n "$ATTACK_ID" ]; then
    echo "   ✓ Attack launched: $ATTACK_ID"
else
    echo "   ✗ Failed to launch attack"
    echo "   Response: $ATTACK_RESPONSE"
    exit 1
fi

# Monitor for detections
echo -e "\n4. Monitoring for detections (30 seconds)..."
echo "   Checking every 5 seconds..."

for i in {1..6}; do
    sleep 5
    STATS=$(curl -s http://localhost:8000/api/stats/summary)
    
    TOTAL_FLOWS=$(echo $STATS | grep -o '"total_flows":[0-9]*' | cut -d':' -f2)
    ATTACK_COUNT=$(echo $STATS | grep -o '"attack_count":[0-9]*' | cut -d':' -f2)
    PACKETS=$(echo $STATS | grep -o '"packets_captured":[0-9]*' | cut -d':' -f2)
    
    echo "   [$i/6] Flows: $TOTAL_FLOWS | Attacks Detected: $ATTACK_COUNT | Packets: $PACKETS"
    
    if [ "$ATTACK_COUNT" -gt "0" ]; then
        echo -e "\n   🎉 SUCCESS! Attack detected!"
        break
    fi
done

# Final stats
echo -e "\n5. Final Statistics:"
curl -s http://localhost:8000/api/stats/summary | python3 -m json.tool 2>/dev/null

FINAL_ATTACK_COUNT=$(curl -s http://localhost:8000/api/stats/summary | grep -o '"attack_count":[0-9]*' | cut -d':' -f2)

echo -e "\n======================================================================"
if [ "$FINAL_ATTACK_COUNT" -gt "0" ]; then
    echo "✓ TEST PASSED - Attacks are being detected!"
    echo "======================================================================"
    echo ""
    echo "Your system is working correctly!"
    echo "You can now:"
    echo "  1. Open http://localhost:5173"
    echo "  2. See detections in real-time"
    echo "  3. Launch more attacks from the UI"
else
    echo "✗ TEST FAILED - No attacks detected"
    echo "======================================================================"
    echo ""
    echo "Possible issues:"
    echo "  1. Attack didn't generate enough traffic (check backend logs)"
    echo "  2. Traffic was classified as benign (normal for some attacks)"
    echo "  3. VM not reachable (check: ping 192.168.64.3)"
    echo "  4. Model threshold too high (currently 70% confidence)"
    echo ""
    echo "Check backend logs for:"
    echo "  - '🚨 ATTACK DETECTED' messages"
    echo "  - 'Prediction: X' messages"
    echo "  - 'Processing X flows for detection' messages"
fi

# Stop attack
if [ -n "$ATTACK_ID" ]; then
    echo -e "\nStopping attack..."
    curl -s -X POST http://localhost:8000/api/attacks/stop/$ATTACK_ID > /dev/null
fi

