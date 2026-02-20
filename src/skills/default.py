import os
import subprocess
import aiohttp
from datetime import datetime
from src.skills.registry import SkillRegistry
from src.config.settings import BASE_DIR, STORAGE_DIR, USER_FILE
from src.memory.db import Session, Interaction

import re
import glob

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
            if os.path.isdir(file_path):
                continue
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
            if not os.path.exists(todo_file):
                return "No TODOs found."
            with open(todo_file, "r") as f:
                return f.read()
        
        elif action == "add":
            with open(todo_file, "a") as f:
                f.write(f"\n- [ ] {task}")
            return f"Task added: {task}"
        
        elif action == "remove":
            if not os.path.exists(todo_file):
                return "No TODOs found."
            with open(todo_file, "r") as f:
                lines = f.readlines()
            new_lines = [line for line in lines if task.lower() not in line.lower()]
            with open(todo_file, "w") as f:
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
        
        # Try to get battery, handle permission errors gracefully
        try:
            battery = psutil.sensors_battery()
            battery_str = f"{battery.percent}%" if battery else "N/A"
        except Exception:
            battery_str = "Permission Denied/Unavailable"

        info = {
            "os": platform.system(),
            "os_release": platform.release(),
            "cpu": platform.processor(),
            "memory_total": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
            "memory_available": f"{psutil.virtual_memory().available / (1024**3):.2f} GB",
            "battery": battery_str
        }
        return str(info)
    except Exception as e:
        # Fallback if psutil fails or is missing
        return f"OS: {os.name}, Error: {str(e)}"

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
    """Fetches and cleans the text content of a web page given its URL."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=15) as response:
                if response.status == 200:
                    html = await response.text()
                    
                    # Use BeautifulSoup to clean the HTML
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html, "html.parser")
                    
                    # Remove script and style elements
                    for script_or_style in soup(["script", "style", "header", "footer", "nav"]):
                        script_or_style.decompose()
                    
                    # Get text and clean up whitespace
                    text = soup.get_text(separator=" ")
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    clean_text = "\n".join(chunk for chunk in chunks if chunk)
                    
                    # Return first 6000 characters (slightly increased limit)
                    return clean_text[:6000]
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
        return "\n".join(items)
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
        return "\n".join(formatted)
    finally:
        session.close()

@SkillRegistry.register("git_ops")
def git_ops(action: str, repo_url: str = "", message: str = "", branch: str = "main"):
    """Performs git operations: 'clone', 'pull', 'push', 'commit_all', 'status'."""
    try:
        if action == "status":
            cmd = "git status"
        elif action == "clone":
            cmd = f"git clone {repo_url}"
        elif action == "pull":
            cmd = f"git pull origin {branch}"
        elif action == "commit_all":
            cmd = f'git add . && git commit -m "{message}"'
        elif action == "push":
            cmd = f"git push origin {branch}"
        else:
            return "Invalid action. Use 'clone', 'pull', 'push', 'commit_all', or 'status'."
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=BASE_DIR)
        output = result.stdout if result.returncode == 0 else result.stderr
        return f"Git {action} result:\n{output}"
    except Exception as e:
        return f"Error during git {action}: {str(e)}"

@SkillRegistry.register("investigate_codebase")
def investigate_codebase(directory: str = "."):
    """Provides a high-level architectural overview of a codebase."""
    full_path = BASE_DIR / directory
    if not full_path.exists():
        return f"Error: Directory '{directory}' not found."
    
    try:
        # 1. List files
        files = subprocess.getoutput(f"find {full_path} -maxdepth 2 -not -path '*/.*'")
        
        # 2. Check for key files (README, package.json, requirements.txt)
        key_files = []
        for k in ["README.md", "package.json", "requirements.txt", "pyproject.toml", "main.py", "index.js"]:
            if (full_path / k).exists():
                key_files.append(k)
        
        # 3. Summarize structure
        summary = f"Codebase Investigation of '{directory}':\n\n"
        summary += f"Files found:\n{files}\n\n"
        summary += f"Key entry points/configs: {', '.join(key_files)}\n"
        
        return summary
    except Exception as e:
        return f"Error investigating codebase: {str(e)}"

@SkillRegistry.register("switch_model")
def switch_model(model_name: str):
    """Changes the current Gemini model (e.g., 'gemini-2.0-flash', 'gemini-1.5-pro')."""
    try:
        # We'll set an environment variable that GeminiBrain will respect
        os.environ["GEMINI_MODEL"] = model_name
        return f"Successfully switched model to: {model_name}. I will use this for future responses."
    except Exception as e:
        return f"Error switching model: {str(e)}"

@SkillRegistry.register("execute_shell_command")
def execute_shell_command(command: str):
    """Executes a shell command on the local system. (USE WITH CAUTION)"""
    # Safety: In a real agent, we would ask for confirmation.
    # For now, we'll log it and execute it.
    print(f"CRITICAL: Executing shell command: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout if result.returncode == 0 else result.stderr
        return f"Exit Code: {result.returncode}\nOutput: {output}"
    except Exception as e:
        return f"Error executing command: {str(e)}"
