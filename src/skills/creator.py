import os
import importlib
import inspect
from src.skills.registry import SkillRegistry
from src.config.settings import BASE_DIR

@SkillRegistry.register("create_new_skill")
def create_new_skill(filename: str, code: str):
    """
    Creates a new Python skill file in the `src/skills/` directory and registers it immediately.
    
    Args:
        filename: The name of the file (e.g., 'web_scraper.py'). MUST end in .py.
        code: The full Python code for the skill. MUST include imports and the @SkillRegistry.register decorator.
              Example:
              ```python
              from src.skills.registry import SkillRegistry
              
              @SkillRegistry.register("my_new_skill")
              def my_new_skill(arg1: str):
                  '''Description of the skill.'''
                  return f"Hello {arg1}"
              ```
    """
    if not filename.endswith(".py"):
        return "Error: Filename must end with .py"
    
    if "SkillRegistry" not in code:
        return "Error: The code must import SkillRegistry and use the @SkillRegistry.register decorator."

    skills_dir = BASE_DIR / "src" / "skills"
    file_path = skills_dir / filename
    
    if file_path.exists():
        return f"Error: Skill file '{filename}' already exists. Use 'edit_file_replace' to modify it."

    try:
        # 1. Write the file
        with open(file_path, "w") as f:
            f.write(code)
        
        # 2. Import the module dynamically to register the skill immediately
        module_name = filename[:-3]
        importlib.import_module(f"src.skills.{module_name}")
        
        return f"Successfully created and registered skill in '{filename}'. You can use it immediately."
    except Exception as e:
        # If import fails, try to clean up the file? Or leave it for debugging?
        # Let's leave it but return the error.
        return f"File written to '{filename}', but failed to load module: {str(e)}"
