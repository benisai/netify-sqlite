#!/bin/bash
cd /app/server && python3 main.py &
cd /app/server && python3 get-dhcp.py &
sleep 7  # Adjust the sleep duration as needed
cd /app/web && node app.js
