import asyncio
import os
from datetime import datetime
from src.config.settings import HEARTBEAT_FILE
from src.llm import GeminiBrain
from src.memory.manager import SoulManager

class HeartbeatManager:
    def __init__(self, brain: GeminiBrain, soul: SoulManager):
        self.brain = brain
        self.soul = soul
        self.interval = 30 * 60 # 30 minutes

    async def start(self):
        """Main heartbeat loop."""
        while True:
            await self.pulse()
            await asyncio.sleep(self.interval)

    async def pulse(self):
        """Perform a single heartbeat check."""
        print(f"[{datetime.now()}] Pulse initiated...")
        
        heartbeat_content = self._read_heartbeat_tasks()
        if not heartbeat_content:
            print("HEARTBEAT.md is empty. Skipping pulse.")
            return

        system_prompt = self.soul.get_system_prompt()
        prompt = f"""
{system_prompt}

# HEARTBEAT TASK CHECK
The following are the current tasks in HEARTBEAT.md:
{heartbeat_content}

Your goal is to decide if any of these tasks require immediate proactive action (e.g., a reminder, a status check, or a notification).

If action is required, describe exactly what you want to do and what message should be sent to which channel.
If nothing needs attention right now, reply ONLY with 'HEARTBEAT_OK'.
"""
        response = await self.brain.generate_response(prompt)
        
        if response.startswith("Error:"):
            print(f"Heartbeat pulse failed: {response}")
            return

        if "HEARTBEAT_OK" in response:
            print("Heartbeat: Everything is fine.")
        else:
            print(f"Heartbeat action required: {response}")
            # Here we would parse the response and dispatch messages to adapters.
            # For now, we'll log it.
            self.soul.log_interaction("heartbeat", "system", "TASK_CHECK", response)

    def _read_heartbeat_tasks(self):
        if os.path.exists(HEARTBEAT_FILE):
            with open(HEARTBEAT_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    return content
        return None
