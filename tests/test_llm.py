import pytest
from unittest.mock import MagicMock, AsyncMock
from src.llm import GeminiBrain

@pytest.mark.asyncio
async def test_brain_generate_response(mocker):
    # Mocking google.genai.Client
    mock_client_class = mocker.patch("src.llm.genai.Client")
    mock_client = mock_client_class.return_value
    
    # Mock the response structure
    mock_part = MagicMock()
    mock_part.text = "Hello, I am Jovibe Agent!"
    mock_part.function_call = None
    
    mock_content = MagicMock()
    mock_content.parts = [mock_part]
    
    mock_candidate = MagicMock()
    mock_candidate.content = mock_content
    
    mock_response = MagicMock()
    mock_response.candidates = [mock_candidate]
    
    # client.aio.models.generate_content is an async call
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)
    
    # Initialize the brain with a forced API key
    mocker.patch.dict("os.environ", {"GEMINI_API_KEY": "dummy_key"})
    brain = GeminiBrain()
    brain.initialize()
    
    response = await brain.generate_response("Hi!")
    
    assert response == "Hello, I am Jovibe Agent!"
    mock_client.aio.models.generate_content.assert_called_once()
