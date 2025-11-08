#!/bin/bash
# Simple script to run the LAN Messaging Notifier

# Load environment variables if .env exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Run the application
python -m src.app
