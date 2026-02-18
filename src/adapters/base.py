from abc import ABC, abstractmethod
from src.llm import GeminiBrain
from src.memory.manager import SoulManager

class BaseAdapter(ABC):
    def __init__(self, brain: GeminiBrain, soul: SoulManager):
        self.brain = brain
        self.soul = soul

    @abstractmethod
    async def run(self):
        """Start the adapter loop (blocking)."""
        pass

    @abstractmethod
    async def send_message(self, user_id, text):
        """Send a message to a specific user on this platform."""
        pass

    async def handle_message(self, channel, user_id, text):
        """Common logic for handling messages from any channel."""
        system_prompt = self.soul.get_system_prompt()
        history = self.soul.get_recent_history(user_id)
        
        prompt = f"""
{system_prompt}

# RECENT CONTEXT
{history}

# INCOMING MESSAGE ({channel})
User: {text}
"""
        response = await self.brain.generate_response(prompt)
        
        # Check if the agent wants to ask a question (STOP_AND_ASK pattern)
        if "STOP_AND_ASK:" in response:
            clean_question = response.split("STOP_AND_ASK:")[1].strip()
            # Log the question as the response
            self.soul.log_interaction(channel, user_id, text, f"[ASKED USER]: {clean_question}")
            await self.send_message(user_id, clean_question)
            return

        # Log interaction
        self.soul.log_interaction(channel, user_id, text, response)
        
        # Send response back to the platform
        await self.send_message(user_id, response)
