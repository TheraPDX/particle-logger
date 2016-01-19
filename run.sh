#!/bin/sh

INTERVAL=10

# Do test
python3 logger.py || exit 1

# Do loop
while true; do
    python3 logger.py
    sleep $INTERVAL
done
