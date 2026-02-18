#!/bin/bash

# Jovibe Agent Linux (Ubuntu/Debian) Installer
echo "Starting Jovibe Agent installation for Linux..."

# 1. Update and install system dependencies
echo "Updating packages..."
sudo apt update -y
echo "Installing Python and build essentials..."
sudo apt install -y python3 python3-pip python3-venv build-essential libffi-dev libssl-dev

# 2. Setup JOVIBE_HOME
JOVIBE_HOME="$HOME/.jovibe"
mkdir -p "$JOVIBE_HOME"
echo "Created Jovibe data directory at $JOVIBE_HOME"

# 3. Install the package
echo "Installing Jovibe Agent..."
# Using --user to avoid needing sudo for pip install
python3 -m pip install . --user

# 4. Setup environment file
ENV_FILE="$JOVIBE_HOME/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "Creating default .env at $ENV_FILE"
    echo "GEMINI_API_KEY=" > "$ENV_FILE"
    echo "TELEGRAM_TOKEN=" >> "$ENV_FILE"
    echo "GEMINI_MODEL=gemini-2.0-flash" >> "$ENV_FILE"
    echo "Please edit $ENV_FILE to add your API keys."
fi

# 5. Add to PATH if not already there (for local bin)
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo "Adding ~/.local/bin to your PATH..."
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
    echo "Please restart your terminal or run: source ~/.bashrc"
fi

echo "------------------------------------------------"
echo "Installation Complete!"
echo "To start the agent, simply type: jovibe"
echo "------------------------------------------------"
