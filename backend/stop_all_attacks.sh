#!/bin/bash
# Stop all running attack processes

echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║                    Stopping All Attack Processes                         ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo ""

# Find and kill Python attack scripts
echo "1. Stopping Python attack scripts..."
PYTHON_ATTACKS=$(ps aux | grep -E "(attack_hulk|attack_http_flood|attack_.*\.py)" | grep -v grep | awk '{print $2}')

if [ -z "$PYTHON_ATTACKS" ]; then
    echo "   No Python attack processes found"
else
    echo "   Found Python attack processes:"
    ps aux | grep -E "(attack_hulk|attack_http_flood|attack_.*\.py)" | grep -v grep
    echo ""
    echo "   Killing processes..."
    for pid in $PYTHON_ATTACKS; do
        kill -9 $pid 2>/dev/null && echo "   ✓ Killed PID $pid"
    done
fi

echo ""

# Find and kill Bash attack scripts
echo "2. Stopping Bash attack scripts..."
BASH_ATTACKS=$(ps aux | grep -E "attack_.*\.sh" | grep -v grep | grep -v "stop_all" | awk '{print $2}')

if [ -z "$BASH_ATTACKS" ]; then
    echo "   No Bash attack processes found"
else
    echo "   Found Bash attack processes:"
    ps aux | grep -E "attack_.*\.sh" | grep -v grep | grep -v "stop_all"
    echo ""
    echo "   Killing processes..."
    for pid in $BASH_ATTACKS; do
        kill -9 $pid 2>/dev/null && echo "   ✓ Killed PID $pid"
    done
fi

echo ""

# Find and kill curl/attack subprocesses
echo "3. Stopping curl/HTTP attack subprocesses..."
CURL_ATTACKS=$(ps aux | grep -E "curl.*192\.168\.64\." | grep -v grep | awk '{print $2}')

if [ -z "$CURL_ATTACKS" ]; then
    echo "   No curl attack processes found"
else
    echo "   Found $(echo "$CURL_ATTACKS" | wc -l | tr -d ' ') curl processes"
    echo "   Killing processes..."
    for pid in $CURL_ATTACKS; do
        kill -9 $pid 2>/dev/null
    done
    echo "   ✓ Killed all curl processes"
fi

echo ""

# Stop via API (real attack launcher)
echo "4. Stopping attacks via API..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/attack-launcher/stop-all)
if echo "$RESPONSE" | grep -q "success"; then
    echo "   ✓ API stop successful"
else
    echo "   ⚠ API stop failed or no attacks to stop"
fi

echo ""

# Verify all stopped
echo "5. Verifying all processes stopped..."
REMAINING=$(ps aux | grep -E "(attack_|curl.*192\.168)" | grep -v grep | grep -v "stop_all" | wc -l | tr -d ' ')

if [ "$REMAINING" -eq "0" ]; then
    echo "   ✓ All attack processes stopped successfully"
else
    echo "   ⚠ $REMAINING processes still running:"
    ps aux | grep -E "(attack_|curl.*192\.168)" | grep -v grep | grep -v "stop_all"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║                    Attack Stop Complete                                 ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"

