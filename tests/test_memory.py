import os
import pytest
from src.memory.manager import SoulManager
from src.config.settings import SOUL_FILE, USER_FILE

def test_soul_manager_system_prompt_default(tmp_path):
    # Mocking files
    soul_file = tmp_path / "soul.md"
    user_file = tmp_path / "user.md"
    
    # We need to monkeypatch the settings or just let it use defaults if files don't exist
    manager = SoulManager()
    prompt = manager.get_system_prompt()
    
    assert "Jovibe Agent" in prompt
    assert "IDENTITY (SOUL.MD)" in prompt

def test_soul_manager_system_prompt_with_content(tmp_path, monkeypatch):
    soul_file = tmp_path / "soul.md"
    user_file = tmp_path / "user.md"
    
    soul_file.write_text("Custom Soul Content")
    user_file.write_text("Custom User Context")
    
    monkeypatch.setattr("src.memory.manager.SOUL_FILE", soul_file)
    monkeypatch.setattr("src.memory.manager.USER_FILE", user_file)
    
    manager = SoulManager()
    prompt = manager.get_system_prompt()
    
    assert "Custom Soul Content" in prompt
    assert "Custom User Context" in prompt
