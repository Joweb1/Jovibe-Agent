import inspect
import functools
from typing import Any, Callable, Dict, List, Optional

class SkillRegistry:
    _instance = None
    _skills: Dict[str, Callable] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SkillRegistry, cls).__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, name: Optional[str] = None):
        """Decorator to register a function as a skill."""
        def decorator(func: Callable):
            skill_name = name or func.__name__
            cls._skills[skill_name] = func
            return func
        return decorator

    @classmethod
    def get_skills(cls) -> Dict[str, Callable]:
        return cls._skills

    @classmethod
    def get_tool_schemas(cls) -> List[Dict[str, Any]]:
        """Generate Gemini-compatible tool schemas from registered skills."""
        schemas = []
        for name, func in cls._skills.items():
            # Simple schema generation based on docstrings and type hints
            # For a production app, use pydantic or a more robust parser
            doc = inspect.getdoc(func) or "No description provided."
            params = inspect.signature(func).parameters
            
            properties = {}
            required = []
            
            for param_name, param in params.items():
                if param_name == "self": continue
                
                param_type = "string"
                if param.annotation == int: param_type = "integer"
                elif param.annotation == float: param_type = "number"
                elif param.annotation == bool: param_type = "boolean"
                
                properties[param_name] = {
                    "type": param_type,
                    "description": f"Parameter {param_name}"
                }
                if param.default == inspect.Parameter.empty:
                    required.append(param_name)

            schemas.append({
                "function_declarations": [{
                    "name": name,
                    "description": doc,
                    "parameters": {
                        "type": "OBJECT",
                        "properties": properties,
                        "required": required
                    }
                }]
            })
        return schemas

    async def execute(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a skill by name."""
        if name not in self._skills:
            raise ValueError(f"Skill '{name}' not found.")
        
        func = self._skills[name]
        if inspect.iscoroutinefunction(func):
            return await func(**arguments)
        else:
            return func(**arguments)
