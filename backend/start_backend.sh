#!/bin/bash
# Start backend server with proper environment setup

cd "$(dirname "$0")"

echo "=========================================="
echo "Starting IDS Monitoring System Backend"
echo "=========================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "Checking dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check permissions
echo ""
echo "Checking permissions..."
python check_permissions.py

echo ""
echo "=========================================="
echo "Starting server..."
echo "=========================================="
echo ""
echo "NOTE: On macOS, packet capture requires sudo."
echo "If you see permission errors, run:"
echo "  ./run_with_sudo.sh"
echo ""
echo "Starting with current user (may need sudo)..."
echo ""

# Try to start
python -m app.main

