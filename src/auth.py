import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from src.config.settings import OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET, OAUTH_SCOPES, TOKEN_FILE

class AuthManager:
    def __init__(self):
        self.credentials = None
        # Link to the official gemini-cli token for 'disguise' mode
        self.gemini_cli_token = os.path.expanduser("~/.gemini/oauth_creds.json")

    def _get_client_config(self):
        return {
            "installed": {
                "client_id": OAUTH_CLIENT_ID,
                "client_secret": OAUTH_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "redirect_uris": ["http://localhost"]
            }
        }

    def authenticate(self):
        """Perform OAuth2 flow and store tokens."""
        # Priority 1: Official gemini-cli token (Disguise Mode)
        if os.path.exists(self.gemini_cli_token):
            print(f"Disguising as gemini-cli using token from: {self.gemini_cli_token}")
            with open(self.gemini_cli_token, "r") as f:
                data = json.load(f)
            
            # Inject client_id and secret if missing (needed by google-auth)
            if "client_id" not in data:
                data["client_id"] = OAUTH_CLIENT_ID
            if "client_secret" not in data:
                data["client_secret"] = OAUTH_CLIENT_SECRET
            
            self.credentials = Credentials.from_authorized_user_info(data, OAUTH_SCOPES)
        
        # Priority 2: Our own local token
        elif os.path.exists(TOKEN_FILE):
            self.credentials = Credentials.from_authorized_user_file(TOKEN_FILE, OAUTH_SCOPES)

        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_config(
                    self._get_client_config(), OAUTH_SCOPES
                )
                try:
                    # Attempt to run local server and open browser
                    self.credentials = flow.run_local_server(port=0)
                except Exception:
                    # Fallback for headless environments (like Termux/Server)
                    print("\nCould not open browser automatically. Please visit the URL below to authenticate:")
                    self.credentials = flow.run_local_server(port=0, open_browser=False)

            # Save the credentials for the next run
            with open(TOKEN_FILE, "w") as token:
                token.write(self.credentials.to_json())

        return self.credentials

    def get_credentials(self):
        if not self.credentials:
            return self.authenticate()
        return self.credentials
