#!/bin/bash
# Generate continuous traffic to the VM for testing

VM_IP="192.168.64.3"

echo "======================================"
echo "Generating traffic to VM: $VM_IP"
echo "======================================"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Continuous ping
while true; do
    echo "[$(date +%H:%M:%S)] Pinging $VM_IP..."
    ping -c 1 -W 1 $VM_IP > /dev/null 2>&1
    sleep 1
    
    # Try HTTP request if available
    if command -v curl &> /dev/null; then
        curl -s --max-time 1 http://$VM_IP > /dev/null 2>&1
    fi
    
    sleep 1
done

