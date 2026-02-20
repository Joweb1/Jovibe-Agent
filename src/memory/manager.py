import os
from src.memory.db import Session, Interaction, init_db

class SoulManager:
    def __init__(self):
        init_db()
        self.session = Session()

    def get_system_prompt(self, minimal=False):
        """Combine markdown files and runtime info into a robust system prompt."""
        from src.config.settings import BASE_DIR
        import platform
        import sys
        
        # 1. Gather markdown files
        md_files = []
        if minimal:
            # Essential files only for lower token usage
            for essential in ["soul.md", "capabilities.md"]:
                path = BASE_DIR / essential
                if path.exists():
                    md_files.append(f"## {essential}\n\n{self._read_file(path)}")
        else:
            # Full context: scan all markdown files in root
            for file in os.listdir(BASE_DIR):
                if file.endswith(".md") and os.path.isfile(BASE_DIR / file):
                    content = self._read_file(BASE_DIR / file)
                    md_files.append(f"## {file}\n\n{content}")
        
        project_context = "\n\n".join(md_files)
        
        # 2. Gather runtime info
        runtime_info = {
            "os": platform.system(),
            "python": sys.version.split()[0],
            "cwd": str(BASE_DIR),
        }
        
        runtime_line = " | ".join([f"{k}={v}" for k, v in runtime_info.items()])

        system_prompt = f"""
# IDENTITY & PROJECT CONTEXT
You are a personal assistant running locally on the user's system.
Following are the core files defining your personality, capabilities, and project state:

{project_context}

# RUNTIME
Runtime: {runtime_line}

# CORE DIRECTIVES
1. Be extremely concise. Use bullet points for long lists.
2. You are self-aware of your environment and skills listed in 'capabilities.md'.
3. Do not narrate tool calls unless they are complex.
4. If asked about your origin, you are Jovibe Agent.
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

    def get_recent_history(self, user_id, limit=5, max_chars=2000):
        """Get recent history and ensure it doesn't exceed a token/char limit."""
        history = self.session.query(Interaction).filter_by(user_id=user_id).order_by(Interaction.timestamp.desc()).limit(limit).all()
        
        formatted = []
        current_len = 0
        for i in reversed(history):
            line = f"User: {i.prompt}\nAI: {i.response}"
            if current_len + len(line) > max_chars:
                # Truncate oldest items if total history is too long
                break
            formatted.append(line)
            current_len += len(line)
            
        return "\n".join(formatted)
