import asyncio
import sys
from pathlib import Path

# Ensure the project root is in sys.path to prioritize local 'src' imports
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.llm import GeminiBrain  # noqa: E402
from src.memory.manager import SoulManager  # noqa: E402
from src.heartbeat import HeartbeatManager  # noqa: E402
from src.adapters.telegram_adapter import TelegramAdapter  # noqa: E402

async def main():
    print("Starting Jovibe Agent...")
    
    # Initialize components
    brain = GeminiBrain()
    brain.initialize()
    
    soul = SoulManager()
    
    heartbeat = HeartbeatManager(brain, soul)
    telegram = TelegramAdapter(brain, soul)
    
    # Run all components concurrently
    print("Launching core services...")
    await asyncio.gather(
        heartbeat.start(),
        telegram.run(),
        # discord.run(),
    )

def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nJovibe Agent shutting down.")

if __name__ == "__main__":
    run()
