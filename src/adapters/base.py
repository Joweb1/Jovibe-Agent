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
        try:
            system_prompt = self.soul.get_system_prompt()
            # Retrieve structured turns for native multi-turn support
            history_turns = self.soul.get_recent_history_turns(user_id, limit=5)
            
            # Construct the final message list
            messages = history_turns + [{"role": "user", "parts": [{"text": text}]}]
            
            response = await self.brain.generate_response(messages, system_instruction=system_prompt)
            
            if not response:
                print(f"Warning: Received empty response for user {user_id}")
                return

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
        except Exception as e:
            error_msg = f"Sorry, I encountered an internal error: {str(e)}"
            print(f"Error handling message from {user_id}: {e}")
            try:
                await self.send_message(user_id, error_msg)
            except Exception:
                pass # Already logged or network is dead
