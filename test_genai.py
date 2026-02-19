import asyncio
from src.llm import GeminiBrain
import os

async def test_genai_client():
    """Test the new google-genai client integration."""
    print("Testing Jovibe GeminiBrain with new 'google-genai' SDK...")
    
    # Check if we have an API key or if we should attempt OAuth
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print(f"API Key found: {api_key[:5]}...{api_key[-5:]}")
    else:
        print("No API Key found. Will attempt OAuth if credentials exist.")

    brain = GeminiBrain()
    
    # We'll use a simple prompt to match the user's request
    prompt = "Explain how AI works in a few words"
    
    print(f"Sending prompt: {prompt}")
    try:
        response_text = await brain.generate_response(prompt, system_instruction="You are a helpful AI assistant.")
        print("
--- Response ---")
        print(response_text)
        print("----------------")
    except Exception as e:
        print(f"Error during test: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_genai_client())
