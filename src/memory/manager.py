import os
import json
from src.config.settings import SOUL_FILE, USER_FILE
from src.memory.db import Session, Interaction, init_db

class SoulManager:
    def __init__(self):
        init_db()
        self.session = Session()

    def get_system_prompt(self):
        """Combine soul.md and user.md into a system prompt."""
        soul_content = self._read_file(SOUL_FILE, "Default soul: You are Jovibe Agent, a helpful AI assistant.")
        user_context = self._read_file(USER_FILE, "No specific user context provided.")
        
        system_prompt = f"""
# IDENTITY (SOUL.MD)
{soul_content}

# USER CONTEXT (USER.MD)
{user_context}

# CORE DIRECTIVES
1. Be concise and professional.
2. Use your memory of past interactions to provide personalized help.
3. If asked about your origin, you are Jovibe Agent, built in Python using Gemini.
"""
        return system_prompt

    def _read_file(self, path, default=""):
        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read()
        return default

    def log_interaction(self, channel, user_id, prompt, response):
        interaction = Interaction(
            channel=channel,
            user_id=user_id,
            prompt=prompt,
            response=response
        )
        self.session.add(interaction)
        self.session.commit()

    def get_recent_history(self, user_id, limit=5):
        history = self.session.query(Interaction).filter_by(user_id=user_id).order_by(Interaction.timestamp.desc()).limit(limit).all()
        return "
".join([f"User: {i.prompt}
AI: {i.response}" for i in reversed(history)])
