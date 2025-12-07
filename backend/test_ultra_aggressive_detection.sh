#!/bin/bash
# Test script for ultra-aggressive continuous detection

echo "══════════════════════════════════════════════════════════════════════"
echo "Testing Ultra-Aggressive Continuous Detection"
echo "══════════════════════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Check monitoring status
echo "1. Checking monitoring status..."
status=$(curl -s http://localhost:8000/api/monitoring/status | python3 -c "import sys,json; print(json.load(sys.stdin)['is_running'])")

if [ "$status" = "True" ]; then
    echo -e "   ${GREEN}✓${NC} Monitoring is ACTIVE"
else
    echo -e "   ${RED}✗${NC} Monitoring is STOPPED. Starting it..."
    curl -s -X POST http://localhost:8000/api/monitoring/start > /dev/null
    sleep 2
    echo -e "   ${GREEN}✓${NC} Monitoring started"
fi

echo ""

# 2. Get baseline stats
echo "2. Getting baseline statistics..."
baseline=$(curl -s http://localhost:8000/api/stats/summary)
baseline_packets=$(echo "$baseline" | python3 -c "import sys,json; print(json.load(sys.stdin)['packets_captured'])")
baseline_flows=$(echo "$baseline" | python3 -c "import sys,json; print(json.load(sys.stdin)['detection']['total_flows'])")
baseline_attacks=$(echo "$baseline" | python3 -c "import sys,json; print(json.load(sys.stdin)['detection']['attack_count'])")

echo "   Packets: $baseline_packets"
echo "   Flows: $baseline_flows"
echo "   Attacks: $baseline_attacks"
echo ""

# 3. Launch attack
echo "3. Launching HULK attack (30 seconds)..."
echo -e "   ${YELLOW}Attack starting...${NC}"
python3 /tmp/attack_hulk.py http://192.168.64.3 30 > /tmp/attack_output.txt 2>&1 &
ATTACK_PID=$!

# 4. Monitor for 35 seconds (5s buffer)
echo ""
echo "4. Monitoring detection (will check every 5 seconds)..."
echo "   ─────────────────────────────────────────────────────────────────"
echo "   Time | Packets  | Flows   | Active | Attacks | Rate   | Status"
echo "   ─────────────────────────────────────────────────────────────────"

for i in {1..7}; do
    sleep 5
    
    stats=$(curl -s http://localhost:8000/api/stats/summary)
    packets=$(echo "$stats" | python3 -c "import sys,json; print(json.load(sys.stdin)['packets_captured'])")
    flows=$(echo "$stats" | python3 -c "import sys,json; print(json.load(sys.stdin)['detection']['total_flows'])")
    active=$(echo "$stats" | python3 -c "import sys,json; print(json.load(sys.stdin)['detection']['active_flows'])")
    attacks=$(echo "$stats" | python3 -c "import sys,json; print(json.load(sys.stdin)['detection']['attack_count'])")
    
    # Calculate rate
    if [ "$packets" -gt 0 ]; then
        rate=$(python3 -c "print(f'{($flows / $packets * 100):.2f}')")
    else
        rate="0.00"
    fi
    
    # Determine status
    if (( $(echo "$rate > 1.0" | bc -l) )); then
        status="${GREEN}GREAT${NC}"
    elif (( $(echo "$rate > 0.5" | bc -l) )); then
        status="${YELLOW}OK${NC}"
    else
        status="${RED}LOW${NC}"
    fi
    
    time=$((i * 5))
    printf "   ${time}s   | %-8s | %-7s | %-6s | %-7s | %-6s%% | " "$packets" "$flows" "$active" "$attacks" "$rate"
    echo -e "$status"
done

echo "   ─────────────────────────────────────────────────────────────────"
echo ""

# Wait for attack to finish
wait $ATTACK_PID 2>/dev/null

# 5. Get final stats
echo "5. Getting final statistics..."
sleep 2
final=$(curl -s http://localhost:8000/api/stats/summary)
final_packets=$(echo "$final" | python3 -c "import sys,json; print(json.load(sys.stdin)['packets_captured'])")
final_flows=$(echo "$final" | python3 -c "import sys,json; print(json.load(sys.stdin)['detection']['total_flows'])")
final_active=$(echo "$final" | python3 -c "import sys,json; print(json.load(sys.stdin)['detection']['active_flows'])")
final_attacks=$(echo "$final" | python3 -c "import sys,json; print(json.load(sys.stdin)['detection']['attack_count'])")

# Calculate final rate
if [ "$final_packets" -gt 0 ]; then
    final_rate=$(python3 -c "print(f'{($final_flows / $final_packets * 100):.3f}')")
else
    final_rate="0.000"
fi

echo ""
echo "   Final Packets: $final_packets"
echo "   Final Flows: $final_flows"
echo "   Final Active: $final_active"
echo "   Final Attacks: $final_attacks"
echo "   Processing Rate: $final_rate%"
echo ""

# 6. Calculate deltas
new_packets=$((final_packets - baseline_packets))
new_flows=$((final_flows - baseline_flows))
new_attacks=$((final_attacks - baseline_attacks))

echo "6. Changes during attack:"
echo "   New Packets: $new_packets"
echo "   New Flows: $new_flows"
echo "   New Attacks: $new_attacks"
echo ""

# 7. Evaluate results
echo "══════════════════════════════════════════════════════════════════════"
echo "RESULTS:"
echo "══════════════════════════════════════════════════════════════════════"

success_count=0
total_checks=4

# Check 1: Processing rate
if (( $(echo "$final_rate > 1.0" | bc -l) )); then
    echo -e "${GREEN}✓${NC} Processing Rate: $final_rate% (target: > 1%)"
    success_count=$((success_count + 1))
else
    echo -e "${RED}✗${NC} Processing Rate: $final_rate% (target: > 1%)"
fi

# Check 2: Active flows
if [ "$final_active" -lt 100 ]; then
    echo -e "${GREEN}✓${NC} Active Flows: $final_active (target: < 100)"
    success_count=$((success_count + 1))
else
    echo -e "${RED}✗${NC} Active Flows: $final_active (target: < 100)"
fi

# Check 3: Attacks detected
if [ "$new_attacks" -gt 10 ]; then
    echo -e "${GREEN}✓${NC} Attacks Detected: $new_attacks (target: > 10)"
    success_count=$((success_count + 1))
else
    echo -e "${RED}✗${NC} Attacks Detected: $new_attacks (target: > 10)"
fi

# Check 4: Flows created
if [ "$new_flows" -gt 500 ]; then
    echo -e "${GREEN}✓${NC} Flows Created: $new_flows (target: > 500)"
    success_count=$((success_count + 1))
else
    echo -e "${RED}✗${NC} Flows Created: $new_flows (target: > 500)"
fi

echo ""
echo "══════════════════════════════════════════════════════════════════════"
if [ "$success_count" -eq "$total_checks" ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED ($success_count/$total_checks)${NC}"
    echo "   Ultra-aggressive detection is working perfectly!"
elif [ "$success_count" -ge 3 ]; then
    echo -e "${YELLOW}⚠️  MOST TESTS PASSED ($success_count/$total_checks)${NC}"
    echo "   System is working but may need minor adjustments"
else
    echo -e "${RED}❌ TESTS FAILED ($success_count/$total_checks)${NC}"
    echo "   Further troubleshooting needed"
fi
echo "══════════════════════════════════════════════════════════════════════"
echo ""

# Show attack output
echo "Attack Tool Output:"
cat /tmp/attack_output.txt
echo ""

