import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Project & Data Paths
# If installed as a package, we want data in a persistent user directory.
JOVIBE_HOME = Path(os.getenv("JOVIBE_HOME", Path.home() / ".jovibe"))
JOVIBE_HOME.mkdir(parents=True, exist_ok=True)

# We check if we are running from a source checkout or as an installed package
# If .env or soul.md exists in the current directory, we might be in 'dev mode'
BASE_DIR = Path(__file__).parent.parent.parent

# For simplicity, we prioritize JOVIBE_HOME for persistent data
STORAGE_DIR = JOVIBE_HOME / "storage"
STORAGE_DIR.mkdir(exist_ok=True)

# File Paths (Stored in JOVIBE_HOME for persistence)
SOUL_FILE = JOVIBE_HOME / "soul.md"
USER_FILE = JOVIBE_HOME / "user.md"
HEARTBEAT_FILE = JOVIBE_HOME / "HEARTBEAT.md"
DB_FILE = STORAGE_DIR / "jovibe.sqlite"
TOKEN_FILE = STORAGE_DIR / "token.json"

# Initialize default files if they don't exist in JOVIBE_HOME
def _init_default_file(path, default_content=""):
    if not path.exists():
        # If the file exists in the repo, copy it as a template
        repo_file = BASE_DIR / path.name
        if repo_file.exists():
            with open(repo_file, "r") as f:
                content = f.read()
        else:
            content = default_content
        with open(path, "w") as f:
            f.write(content)

_init_default_file(SOUL_FILE, "Default soul: You are Jovibe Agent.")
_init_default_file(USER_FILE, "No user context yet.")
_init_default_file(HEARTBEAT_FILE, "# HEARTBEAT\n- [ ] Initial task")

# Load environment from JOVIBE_HOME/.env or current directory
load_dotenv(JOVIBE_HOME / ".env")
load_dotenv()

# Gemini Config
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# OAuth Constants (Ported from Gemini CLI)
OAUTH_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "681255809395-oo8ft2oprdrnp9e3aqf6av3hmdib135j.apps.googleusercontent.com")
OAUTH_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "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")
OAUTH_SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

# Channel Config
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
