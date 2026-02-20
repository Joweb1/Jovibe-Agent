from src.memory.manager import SoulManager
import os

def test_soul_manager_system_prompt_default(tmp_path, monkeypatch):
    # Mock BASE_DIR to the temporary path
    monkeypatch.setattr("src.config.settings.BASE_DIR", tmp_path)
    
    manager = SoulManager()
    prompt = manager.get_system_prompt()
    
    # Check if the core identity text is in the prompt
    assert "Jovibe Agent" in prompt
    assert "# IDENTITY & PROJECT CONTEXT" in prompt

def test_soul_manager_system_prompt_with_content(tmp_path, monkeypatch):
    # Mock BASE_DIR to the temporary path
    monkeypatch.setattr("src.config.settings.BASE_DIR", tmp_path)
    
    soul_file = tmp_path / "soul.md"
    user_file = tmp_path / "user.md"
    
    soul_file.write_text("Custom Soul Content")
    user_file.write_text("Custom User Context")
    
    manager = SoulManager()
    prompt = manager.get_system_prompt()
    
    assert "Custom Soul Content" in prompt
    assert "Custom User Context" in prompt
    assert "## soul.md" in prompt
    assert "## user.md" in prompt
