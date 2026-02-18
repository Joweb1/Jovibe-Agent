import os
import subprocess
import aiohttp
from datetime import datetime
from src.skills.registry import SkillRegistry
from src.config.settings import BASE_DIR
from src.memory.db import Session, Interaction

import re
import glob
from pathlib import Path

@SkillRegistry.register("glob_files")
def glob_files(pattern: str):
    """Finds files matching a glob pattern (e.g., 'src/**/*.py')."""
    try:
        files = glob.glob(str(BASE_DIR / pattern), recursive=True)
        # Return paths relative to BASE_DIR
        relative_files = [os.path.relpath(f, BASE_DIR) for f in files]
        return "\n".join(relative_files) if relative_files else "No files matched the pattern."
    except Exception as e:
        return f"Error globbing files: {str(e)}"

@SkillRegistry.register("grep_search")
def grep_search(pattern: str, file_pattern: str = "**/*.*"):
    """Searches for a regex pattern within files matching the file_pattern."""
    results = []
    try:
        files = glob.glob(str(BASE_DIR / file_pattern), recursive=True)
        regex = re.compile(pattern)
        
        for file_path in files:
            if os.path.isdir(file_path): continue
            try:
                with open(file_path, "r", errors="ignore") as f:
                    for i, line in enumerate(f):
                        if regex.search(line):
                            rel_path = os.path.relpath(file_path, BASE_DIR)
                            results.append(f"{rel_path}:{i+1}: {line.strip()}")
            except Exception:
                continue
        
        return "\n".join(results[:50]) if results else "No matches found."
    except Exception as e:
        return f"Error during grep: {str(e)}"

@SkillRegistry.register("edit_file_replace")
def edit_file_replace(file_path: str, old_text: str, new_text: str):
    """Replaces exact 'old_text' with 'new_text' in the specified file."""
    full_path = BASE_DIR / file_path
    if not os.path.exists(full_path):
        return f"Error: File '{file_path}' not found."
    
    try:
        with open(full_path, "r") as f:
            content = f.read()
        
        if old_text not in content:
            return f"Error: The exact text to replace was not found in '{file_path}'."
        
        new_content = content.replace(old_text, new_text)
        with open(full_path, "w") as f:
            f.write(new_content)
        
        return f"Successfully updated '{file_path}'."
    except Exception as e:
        return f"Error editing file: {str(e)}"

@SkillRegistry.register("google_search")
async def google_search(query: str):
    """Performs a web search and returns snippets of results."""
    # Since we don't have a dedicated API key here, we'll use a public search endpoint or mock
    # For a real implementation, you'd use Serper or Google Search API.
    # Here we'll use a simple DuckDuckGo-style fetch for demonstration.
    url = f"https://html.duckduckgo.com/html/?q={query}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html, "html.parser")
                    results = []
                    for res in soup.find_all('a', class_='result__a', limit=5):
                        results.append(f"{res.get_text()} - {res.get('href')}")
                    return "\n".join(results) if results else "No results found."
                return f"Search failed with status {response.status}"
    except Exception as e:
        return f"Search error: {str(e)}"

@SkillRegistry.register("enter_plan_mode")
def enter_plan_mode(goal: str):
    """Signals that the agent is entering a structured planning phase for a complex goal."""
    return f"PLANNING MODE ACTIVATED for: {goal}. Please outline the steps you will take."

@SkillRegistry.register("ask_user")
def ask_user(question: str):
    """Pauses execution to ask the user a clarifying question. Use this when unsure how to proceed."""
    return f"STOP_AND_ASK: {question}"

@SkillRegistry.register("termux_take_photo")
def termux_take_photo(camera_id: int = 0, filename: str = "photo.jpg"):
    """Takes a photo using the device camera (Termux only)."""
    save_path = STORAGE_DIR / filename
    command = f"termux-camera-photo -c {camera_id} {save_path}"
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return f"Photo saved to {save_path}"
        else:
            return f"Error taking photo: {result.stderr or 'Ensure termux-api is installed.'}"
    except Exception as e:
        return f"Error: {str(e)}"

@SkillRegistry.register("termux_send_notification")
def termux_send_notification(title: str, message: str):
    """Sends a system notification on the device (Termux only)."""
    command = f'termux-notification --title "{title}" --content "{message}"'
    try:
        subprocess.run(command, shell=True)
        return "Notification sent."
    except Exception as e:
        return f"Error sending notification: {str(e)}"

@SkillRegistry.register("save_memory_fact")
def save_memory_fact(fact: str):
    """Saves a specific fact about the user or project to user.md for long-term memory."""
    try:
        with open(USER_FILE, "a") as f:
            f.write(f"\n- {fact} (Logged on {datetime.now().strftime('%Y-%m-%d')})")
        return f"Fact saved to memory: {fact}"
    except Exception as e:
        return f"Error saving fact: {str(e)}"

@SkillRegistry.register("manage_todos")
def manage_todos(action: str, task: str = ""):
    """Manages the TODO.md file. Actions: 'list', 'add', 'remove'."""
    todo_file = BASE_DIR / "TODO.md"
    try:
        if action == "list":
            if not os.path.exists(todo_file): return "No TODOs found."
            with open(todo_file, "r") as f: return f.read()
        
        elif action == "add":
            with open(todo_file, "a") as f:
                f.write(f"\n- [ ] {task}")
            return f"Task added: {task}"
        
        elif action == "remove":
            if not os.path.exists(todo_file): return "No TODOs found."
            with open(todo_file, "r") as f:
                lines = f.readlines()
            new_lines = [l for l in lines if task.lower() not in l.lower()]
            with os.open(todo_file, "w") as f:
                f.writelines(new_lines)
            return f"Removed tasks matching: {task}"
            
        return "Invalid action. Use 'list', 'add', or 'remove'."
    except Exception as e:
        return f"Error managing TODOs: {str(e)}"

@SkillRegistry.register("write_project_file")
def write_project_file(file_path: str, content: str):
    """Writes or overwrites a file within the project directory."""
    full_path = BASE_DIR / file_path
    try:
        # Ensure the directory exists
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)
        return f"Successfully wrote to '{file_path}'."
    except Exception as e:
        return f"Error writing file: {str(e)}"

@SkillRegistry.register("get_system_info")
def get_system_info():
    """Returns basic information about the system (OS, CPU, etc.)."""
    try:
        import platform
        import psutil
        info = {
            "os": platform.system(),
            "os_release": platform.release(),
            "cpu": platform.processor(),
            "memory_total": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
            "memory_available": f"{psutil.virtual_memory().available / (1024**3):.2f} GB",
            "battery": f"{psutil.sensors_battery().percent}%" if psutil.sensors_battery() else "N/A"
        }
        return str(info)
    except ImportError:
        # Fallback if psutil is not installed
        return f"OS: {os.name}, Platform: {subprocess.getoutput('uname -a')}"

@SkillRegistry.register("append_to_heartbeat")
def append_to_heartbeat(task_description: str):
    """Adds a new task to the HEARTBEAT.md file."""
    from src.config.settings import HEARTBEAT_FILE
    try:
        with open(HEARTBEAT_FILE, "a") as f:
            f.write(f"\n- [ ] {task_description} (Added on {datetime.now().strftime('%Y-%m-%d %H:%M')})")
        return f"Task added to heartbeat: {task_description}"
    except Exception as e:
        return f"Error appending task: {str(e)}"

@SkillRegistry.register("fetch_web_page")
async def fetch_web_page(url: str):
    """Fetches the text content of a web page given its URL."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    text = await response.text()
                    # Return first 5000 characters to avoid token limits
                    return text[:5000]
                else:
                    return f"Error: Received status code {response.status}"
    except Exception as e:
        return f"Error fetching URL: {str(e)}"

@SkillRegistry.register("get_current_time")
def get_current_time():
    """Returns the current date and time in ISO format."""
    return datetime.now().isoformat()

@SkillRegistry.register("read_project_file")
def read_project_file(file_path: str):
    """Reads the content of a file within the project directory."""
    full_path = BASE_DIR / file_path
    if not os.path.exists(full_path):
        return f"Error: File '{file_path}' not found."
    
    try:
        with open(full_path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

@SkillRegistry.register("list_project_files")
def list_project_files(directory: str = "."):
    """Lists all files and folders in a specific project directory."""
    full_path = BASE_DIR / directory
    if not os.path.exists(full_path) or not os.path.isdir(full_path):
        return f"Error: Directory '{directory}' not found."
    
    try:
        items = os.listdir(full_path)
        return "
".join(items)
    except Exception as e:
        return f"Error listing directory: {str(e)}"

@SkillRegistry.register("search_memory")
def search_memory(query: str, limit: int = 5):
    """Searches through the agent's interaction history for a keyword."""
    session = Session()
    try:
        results = session.query(Interaction).filter(
            (Interaction.prompt.like(f"%{query}%")) | 
            (Interaction.response.like(f"%{query}%"))
        ).order_by(Interaction.timestamp.desc()).limit(limit).all()
        
        if not results:
            return "No matching interactions found in memory."
            
        formatted = []
        for r in results:
            formatted.append(f"[{r.timestamp}] {r.channel} - User: {r.prompt} | AI: {r.response[:100]}...")
        return "
".join(formatted)
    finally:
        session.close()

@SkillRegistry.register("execute_shell_command")
def execute_shell_command(command: str):
    """Executes a shell command on the local system. (USE WITH CAUTION)"""
    # Safety: In a real agent, we would ask for confirmation.
    # For now, we'll log it and execute it.
    print(f"CRITICAL: Executing shell command: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout if result.returncode == 0 else result.stderr
        return f"Exit Code: {result.returncode}
Output: {output}"
    except Exception as e:
        return f"Error executing command: {str(e)}"
