import pytest
import google.generativeai as genai
from unittest.mock import MagicMock, AsyncMock
from src.llm import GeminiBrain

@pytest.mark.asyncio
async def test_brain_generate_response(mocker):
    # Mocking genai.configure and GenerativeModel
    mocker.patch("google.generativeai.configure")
    mock_model = mocker.patch("google.generativeai.GenerativeModel")
    
    # Mock the chat and response
    mock_chat = AsyncMock()
    mock_response = MagicMock()
    mock_response.text = "Hello, I am Jovibe Agent!"
    mock_chat.send_message_async.return_value = mock_response
    
    # Setup the GenerativeModel to return our mock_chat
    mock_model_instance = mock_model.return_value
    mock_model_instance.start_chat.return_value = mock_chat
    
    # Initialize the brain (with dummy API key or mocked auth)
    mocker.patch("src.config.settings.GEMINI_API_KEY", "dummy_key")
    brain = GeminiBrain()
    brain.initialize()
    
    response = await brain.generate_response("Hi!")
    
    assert response == "Hello, I am Jovibe Agent!"
    mock_model_instance.start_chat.assert_called_once()
    mock_chat.send_message_async.assert_called_once()
