import google.generativeai as genai
from src.auth import AuthManager
from src.config.settings import GEMINI_MODEL, GEMINI_API_KEY
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

    async def generate_response(self, prompt, system_instruction=None):
        """Generate a response, handling any tool calls along the way."""
        if not self.model:
            self.initialize()
        
        chat = self.model.start_chat(enable_automatic_function_calling=True)
        
        # We include the system instruction as a message if provided, 
        # as gemini-2.0-flash-exp and others handle it well this way or via system_instruction param.
        # For simplicity in this implementation, we prepend it to the prompt.
        full_prompt = prompt
        if system_instruction:
            full_prompt = f"{system_instruction}\n\nUSER INPUT: {prompt}"

        response = await chat.send_message_async(full_prompt)
        return response.text
