#!/bin/bash
# Integration test for MintWatcher start/stop functionality

echo "MintWatcher Start/Stop Integration Test"
echo "========================================"
echo ""

# Change to script directory
cd "$(dirname "$0")"

echo "1. Checking initial status..."
python3 mintwatcher.py --status
echo ""

echo "2. Stopping any existing instances..."
python3 mintwatcher.py --stop
echo ""

echo "3. Starting MintWatcher in background..."
python3 mintwatcher.py --start &
MINTWATCHER_PID=$!
echo "Started with PID: $MINTWATCHER_PID"
sleep 3
echo ""

echo "4. Checking status (should be running)..."
python3 mintwatcher.py --status
echo ""

echo "5. Testing --stop command..."
python3 mintwatcher.py --stop
echo ""

echo "6. Verifying it stopped..."
sleep 1
python3 mintwatcher.py --status
echo ""

echo "Test complete!"
