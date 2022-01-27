#!/bin/sh

set -e

/usr/sbin/mosquitto -c /mosquitto/config/mosquitto.conf &

echo "Starting dispatcher"
python3 -u /opt/broker/broker.py