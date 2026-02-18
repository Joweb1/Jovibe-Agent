import json
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from src.config.settings import OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET, OAUTH_SCOPES, TOKEN_FILE

class AuthManager:
    def __init__(self):
        self.credentials = None

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
        if os.path.exists(TOKEN_FILE):
            self.credentials = Credentials.from_authorized_user_file(TOKEN_FILE, OAUTH_SCOPES)

        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_config(
                    self._get_client_config(), OAUTH_SCOPES
                )
                self.credentials = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(TOKEN_FILE, "w") as token:
                token.write(self.credentials.to_json())

        return self.credentials

    def get_credentials(self):
        if not self.credentials:
            return self.authenticate()
        return self.credentials
