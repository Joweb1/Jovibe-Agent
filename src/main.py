import asyncio
from src.llm import GeminiBrain
from src.memory.manager import SoulManager
from src.heartbeat import HeartbeatManager
from src.adapters.telegram_adapter import TelegramAdapter

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
