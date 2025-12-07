#!/bin/bash
# Run backend with sudo while preserving virtual environment

cd "$(dirname "$0")"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    PYTHON_PATH=$(which python)
    echo "Using Python from venv: $PYTHON_PATH"
else
    PYTHON_PATH=$(which python3)
    echo "Using system Python: $PYTHON_PATH"
fi

# Run with sudo, preserving the Python path
sudo -E env PATH="$PATH" "$PYTHON_PATH" -m app.main

