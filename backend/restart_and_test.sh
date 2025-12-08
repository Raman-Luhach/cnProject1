#!/bin/bash
# Quick restart and test script

echo "======================================================================"
echo "Restarting IDS System with Fixes"
echo "======================================================================"

# The backend reload happens automatically (Uvicorn --reload)
# Just need to restart monitoring

cd /Users/ramanluhach/cnProject/backend

echo "1. Stopping monitoring..."
curl -s -X POST http://localhost:8000/api/monitoring/stop > /dev/null
sleep 2

echo "2. Starting monitoring..."
curl -s -X POST http://localhost:8000/api/monitoring/start | python3 -m json.tool

sleep 3

echo ""
echo "3. Initial stats:"
curl -s http://localhost:8000/api/stats/summary | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"Flows: {d['detection']['total_flows']}, Attacks: {d['detection']['attack_count']}, Active: {d['detection']['active_flows']}\")"

echo ""
echo "4. Launching attack (30 seconds)..."
python3 /tmp/attack_hulk.py http://192.168.64.3 30 > /tmp/attack_log.txt 2>&1 &
ATTACK_PID=$!

# Monitor for 30 seconds
for i in {5..30..5}; do
    sleep 5
    STATS=$(curl -s http://localhost:8000/api/stats/summary)
    FLOWS=$(echo "$STATS" | python3 -c "import sys, json; print(json.load(sys.stdin)['detection']['total_flows'])")
    ATTACKS=$(echo "$STATS" | python3 -c "import sys, json; print(json.load(sys.stdin)['detection']['attack_count'])")
    ACTIVE=$(echo "$STATS" | python3 -c "import sys, json; print(json.load(sys.stdin)['detection']['active_flows'])")
    echo "[${i}s] Flows: $FLOWS | Attacks: $ATTACKS | Active: $ACTIVE"
done

wait $ATTACK_PID 2>/dev/null

echo ""
echo "======================================================================"
echo "FINAL RESULTS"
echo "======================================================================"
curl -s http://localhost:8000/api/stats/summary | python3 -m json.tool | grep -A 10 "detection"

echo ""
echo "======================================================================"

