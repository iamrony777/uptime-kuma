#!/bin/bash

# Check if connected to Protonvpn

exec python3 /app/protonvpn_ip_check.py


# Then start server

exec node /app/server/server.js