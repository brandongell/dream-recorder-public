#!/bin/bash

echo "GPIO Button Test Sequence"
echo "========================="
echo
echo "We will do EXACTLY 3 button presses in this order:"
echo "1. ONE single tap (quick press and release)"
echo "2. ONE long tap (hold for 3+ seconds)"
echo "3. ONE double tap (two quick presses)"
echo
echo "IMPORTANT: Wait for each instruction before pressing!"
echo
echo "Press ENTER to start the test..."
read

# Clear the logs
sudo journalctl --rotate
sudo journalctl --vacuum-time=1s > /dev/null 2>&1

echo
echo "Starting log monitoring..."
echo

# Start monitoring in background
sudo journalctl -u dream-recorder-gpio.service -f --no-pager > gpio_test_log.txt &
JOURNAL_PID=$!

sleep 2

echo "========================================="
echo "TEST 1: SINGLE TAP"
echo "Please do ONE quick tap NOW"
echo "========================================="
sleep 5

echo
echo "========================================="
echo "TEST 2: LONG TAP" 
echo "Please HOLD the button for 3+ seconds NOW"
echo "========================================="
sleep 8

echo
echo "========================================="
echo "TEST 3: DOUBLE TAP"
echo "Please do TWO quick taps NOW"
echo "========================================="
sleep 5

echo
echo "Test complete! Stopping log monitoring..."
kill $JOURNAL_PID 2>/dev/null

echo
echo "Analyzing results..."
echo

echo "=== PRESS/RELEASE Events ==="
grep -E "PRESS detected|RELEASE detected" gpio_test_log.txt

echo
echo "=== TAP Detection Results ==="
grep -E "SINGLE TAP|DOUBLE TAP|LONG TAP" gpio_test_log.txt | grep -v "Starting tuned tap"

echo
echo "Full log saved to gpio_test_log.txt"
