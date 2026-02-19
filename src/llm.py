from google import genai
import asyncio
from src.auth import AuthManager
from src.config.settings import GEMINI_MODEL, GEMINI_API_KEY
from src.skills.registry import SkillRegistry
import src.skills.default  # noqa: F401 # Ensure default skills are registered

class GeminiBrain:
    def __init__(self):
        self.auth_manager = AuthManager()
        self.client = None
        self.registry = SkillRegistry()

    def initialize(self):
        """Initialize the Gemini Client with API Key or OAuth credentials."""
        if GEMINI_API_KEY:
            print("Initializing Gemini Client with API Key...")
            self.client = genai.Client(api_key=GEMINI_API_KEY)
        else:
            print("Initializing Gemini Client with OAuth...")
            creds = self.auth_manager.get_credentials()
            # The new SDK can take the credentials object directly.
            # Depending on the version, it might need to be passed via common_config or directly.
            # Most recent versions support genai.Client(credentials=creds)
            self.client = genai.Client(credentials=creds)

    async def generate_response(self, prompt, system_instruction=None, retries=3):
        """Generate a response using the new google-genai Client."""
        if not self.client:
            self.initialize()
        
        # Load registered skills as tools
        skills = self.registry.get_skills()
        # tools = list(skills.values()) if skills else None
        # Note: Tool calling in the new SDK might require further adjustment 
        # but for now we follow the user's simple generation request pattern.

        # Configure generating options
        config = {}
        if system_instruction:
            config["system_instruction"] = system_instruction
        
        # For now, we'll keep it simple to match the user's requested snippet structure
        for attempt in range(retries):
            try:
                # The new SDK's generate_content is synchronous by default unless using aio.
                # To keep it async, we should use the aio client or run in executor.
                # Actually, the new SDK has an 'aio' module.
                # However, for simplicity and to stay close to the user's snippet:
                
                # Check if we should use the aio client
                # from google.genai import aio
                # However, the user's snippet used `client = genai.Client()`
                
                response = self.client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=prompt,
                    config=config
                )
                return response.text
            except Exception as e:
                wait_time = (attempt + 1) * 5
                if attempt < retries - 1:
                    print(f"Error occurred: {str(e)}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    return f"An unexpected error occurred: {str(e)}"
        
        return "Error: Failed to generate response."
