import asyncio
import os
import time
from datetime import datetime
from src.config.settings import HEARTBEAT_FILE
from src.llm import GeminiBrain
from src.memory.manager import SoulManager

class HeartbeatManager:
    def __init__(self, brain: GeminiBrain, soul: SoulManager):
        self.brain = brain
        self.soul = soul
        self.interval = 60 * 60 # 60 minutes (Reduced frequency to save quota)

    async def start(self):
        """Main heartbeat loop."""
        # Wait a bit on startup to let Telegram initialize first
        await asyncio.sleep(10)
        while True:
            await self.pulse()
            await asyncio.sleep(self.interval)

    async def pulse(self):
        """Perform a single heartbeat check with optimized payload."""
        # QUOTA PROTECTION: Check if models are currently cooling down
        active_model = self.brain._current_model
        if active_model in self.brain._cooldowns:
            if time.time() < self.brain._cooldowns[active_model]:
                print(f"Heartbeat: Model {active_model} is cooling down. Skipping pulse to save quota.")
                return

        print(f"[{datetime.now()}] Pulse initiated...")
        
        heartbeat_content = self._read_heartbeat_tasks()
        if not heartbeat_content:
            print("HEARTBEAT.md is empty. Skipping pulse.")
            return

        # Use minimal system prompt and disable tools for heartbeat to save quota
        system_prompt = self.soul.get_system_prompt(minimal=True)
        
        # Limit the heartbeat content we send
        limited_content = heartbeat_content[:1500] 
        
        prompt = f"""
{system_prompt}

# HEARTBEAT TASK CHECK (RESTRICTED)
The following is your internal task list from HEARTBEAT.md:
---
{limited_content}
---

Your goal is to decide if any of these specific tasks require immediate proactive action.
- **CRITICAL**: Do NOT investigate your own system, quota, or environment during this pulse.
- If no task listed above requires action RIGHT NOW, reply ONLY with 'HEARTBEAT_OK'.
- Do not perform "general maintenance" or "status checks" unless specifically tasked.
"""
        # PASSING tools=[] to strictly forbid tool-calling during heartbeat
        response = await self.brain.generate_response(prompt, tools=[])
        
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
