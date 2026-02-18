from src.skills.registry import SkillRegistry

def test_skill_registration():
    registry = SkillRegistry()
    
    @registry.register("test_skill")
    def my_skill(arg1: str, arg2: int = 10):
        """A test skill description."""
        return f"{arg1}-{arg2}"
    
    skills = registry.get_skills()
    assert "test_skill" in skills
    assert skills["test_skill"] == my_skill

def test_tool_schema_generation():
    registry = SkillRegistry()
    
    @registry.register("schema_skill")
    def schema_skill(name: str, age: int):
        """Skill for schema test."""
        pass
    
    schemas = registry.get_tool_schemas()
    # Filter for our specific skill
    skill_schema = next(s for s in schemas if s["function_declarations"][0]["name"] == "schema_skill")
    
    func = skill_schema["function_declarations"][0]
    assert func["description"] == "Skill for schema test."
    assert "name" in func["parameters"]["properties"]
    assert "age" in func["parameters"]["properties"]
    assert func["parameters"]["properties"]["age"]["type"] == "integer"
    assert "name" in func["parameters"]["required"]
    assert "age" in func["parameters"]["required"]
