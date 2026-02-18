# Jovibe Agent

A modular AI agent built with Python and Gemini, designed for both reactive (Telegram/Discord) and proactive (Heartbeat) tasks.

## Installation (Termux)

1. Clone this repository.
2. Run the installer:
   ```bash
   chmod +x install_termux.sh
   ./install_termux.sh
   ```
3. Edit your settings in `~/.jovibe/.env`:
   ```bash
   nano ~/.jovibe/.env
   ```

## Usage

Once installed, you can start the agent from any terminal window by running:

```bash
jovibe
```

## Features
- **Telegram Adapter**: Interact with your agent via Telegram.
- **Heartbeat Manager**: Proactive task execution based on `HEARTBEAT.md`.
- **Tool-Augmented**: The agent can search the web, manage files, and execute shell commands.
- **Persistent Memory**: Saves user preferences and interaction history in a local SQLite database.

## Data Locations
- **Config & Soul**: `~/.jovibe/`
- **Database**: `~/.jovibe/storage/jovibe.sqlite`
