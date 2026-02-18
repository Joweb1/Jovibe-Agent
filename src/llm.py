import google.generativeai as genai
import asyncio
from google.api_core import exceptions
from src.auth import AuthManager
from src.config.settings import GEMINI_MODEL, GEMINI_API_KEY, OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET, OAUTH_SCOPES
from src.skills.registry import SkillRegistry
import src.skills.default  # noqa: F401 # Ensure default skills are registered

class GeminiBrain:
    def __init__(self):
        self.auth_manager = AuthManager()
        self.model = None
        self.registry = SkillRegistry()

    def initialize(self):
        """Initialize the Gemini API with API Key or OAuth credentials."""
        if GEMINI_API_KEY:
            print("Initializing Gemini with API Key...")
            genai.configure(api_key=GEMINI_API_KEY)
        else:
            print("Initializing Gemini with OAuth...")
            creds = self.auth_manager.get_credentials()
            genai.configure(credentials=creds)
        
        # Load registered skills as tools
        tools = list(self.registry.get_skills().values())
        self.model = genai.GenerativeModel(GEMINI_MODEL, tools=tools)

    async def generate_response(self, prompt, system_instruction=None, retries=3):
        """Generate a response, handling any tool calls along the way with retry logic."""
        if not self.model:
            self.initialize()
        
        for attempt in range(retries):
            try:
                chat = self.model.start_chat(enable_automatic_function_calling=True)
                
                full_prompt = prompt
                if system_instruction:
                    full_prompt = f"{system_instruction}\n\nUSER INPUT: {prompt}"

                response = await chat.send_message_async(full_prompt)
                return response.text
            except exceptions.ResourceExhausted as e:
                wait_time = (attempt + 1) * 10
                if attempt < retries - 1:
                    print(f"Quota exceeded. Retrying in {wait_time}s... ({e.message})")
                    await asyncio.sleep(wait_time)
                else:
                    return f"Error: Quota exceeded after {retries} attempts. Please try again later."
            except Exception as e:
                return f"An unexpected error occurred: {str(e)}"
        
        return "Error: Failed to generate response."
