#!/bin/bash

# Jovibe Agent Termux Installer
echo "Starting Jovibe Agent installation for Termux..."

# 0. Check for Termux environment
if [ -z "$TERMUX_VERSION" ]; then
    echo "Warning: This script is optimized for Termux. Proceeding anyway..."
fi

# 1. Update and install system dependencies
echo "Updating packages..."
pkg update -y && pkg upgrade -y
echo "Installing essential build tools and libraries..."
pkg install python python-pip termux-api clang make python-dev libffi libffi-dev openssl openssl-dev rust binutils -y

# Optional but RECOMMENDED: Install TUR repo for pre-compiled binaries
# This avoids hours of compilation for things like grpcio and psutil
echo "Checking for Termux User Repository (TUR)..."
pkg install tur-repo -y

# Try to install complex dependencies via pkg if available (faster and more reliable)
echo "Installing complex dependencies via pkg..."
pkg install python-grpcio python-psutil python-cryptography -y || echo "Package-level dependencies not found, will attempt pip installation."

# 2. Setup JOVIBE_HOME
JOVIBE_HOME="$HOME/.jovibe"
mkdir -p "$JOVIBE_HOME"
echo "Created Jovibe data directory at $JOVIBE_HOME"

# 3. Install the package
echo "Installing Jovibe Agent..."
pip install . --no-cache-dir

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
