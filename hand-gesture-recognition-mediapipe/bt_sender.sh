#!/bin/bash
# Continuous Bluetooth sender
DEVICE="B8:27:EB:AA:BB:29"
PORT=1
PIPE="/tmp/gesture_pipe"

# Create named pipe if it doesn't exist
if [[ ! -p $PIPE ]]; then
    mkfifo $PIPE
fi

echo "Bluetooth sender ready. Connecting to $DEVICE..."

# Keep sending data from the pipe
while true; do
    if [[ -p $PIPE ]]; then
        while IFS= read -r line; do
            echo "$line" | sudo rfcomm connect /dev/rfcomm0 $DEVICE $PORT &
            sleep 0.5
            sudo pkill -f "rfcomm connect"
        done < $PIPE
    fi
    sleep 1
done
