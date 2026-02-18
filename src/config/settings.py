import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Project Paths
BASE_DIR = Path(__file__).parent.parent.parent
SRC_DIR = BASE_DIR / "src"
CONFIG_DIR = SRC_DIR / "config"
STORAGE_DIR = BASE_DIR / "storage"
STORAGE_DIR.mkdir(exist_ok=True)

# OAuth Constants (Ported from Gemini CLI)
OAUTH_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
OAUTH_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
OAUTH_SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

# File Paths
CREDENTIALS_FILE = STORAGE_DIR / "credentials.json"
TOKEN_FILE = STORAGE_DIR / "token.json"
SOUL_FILE = BASE_DIR / "soul.md"
USER_FILE = BASE_DIR / "user.md"
HEARTBEAT_FILE = BASE_DIR / "HEARTBEAT.md"
DB_FILE = STORAGE_DIR / "jovibe.sqlite"

# Gemini Config
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Channel Config
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
