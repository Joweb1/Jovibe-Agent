#!/bin/bash

# Jovibe Agent Termux Installer
echo "Starting Jovibe Agent installation for Termux..."

# 1. Update and install system dependencies
echo "Updating packages..."
pkg update -y && pkg upgrade -y
echo "Installing dependencies (python, termux-api, etc.)..."
pkg install python python-pip termux-api -y

# 2. Setup JOVIBE_HOME
JOVIBE_HOME="$HOME/.jovibe"
mkdir -p "$JOVIBE_HOME"
echo "Created Jovibe data directory at $JOVIBE_HOME"

# 3. Install the package
echo "Installing Jovibe Agent..."
pip install .

# 4. Check for .env and prompt for API keys
ENV_FILE="$JOVIBE_HOME/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "Creating default .env at $ENV_FILE"
    echo "GEMINI_API_KEY=" > "$ENV_FILE"
    echo "TELEGRAM_TOKEN=" >> "$ENV_FILE"
    echo "GEMINI_MODEL=gemini-2.0-flash" >> "$ENV_FILE"
    echo "Please edit $ENV_FILE to add your API keys."
fi

echo "------------------------------------------------"
echo "Installation Complete!"
echo "To start the agent, simply type: jovibe"
echo "------------------------------------------------"
