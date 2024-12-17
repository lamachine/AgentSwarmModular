"""
Google API Credentials Handler

Centralized credential management for all Google API services.
Uses OAuth2 flow and token caching for efficient authentication.
"""

import os
import json
import pickle
from typing import List
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from functools import lru_cache
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Temporary scopes until we create service-specific files
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/tasks'
]

def get_credentials_path() -> str:
    """Get path to credentials file from environment."""
    creds_file = os.getenv('GOOGLE_CLIENT_SECRET_FILE')
    if not creds_file:
        raise ValueError("GOOGLE_CLIENT_SECRET_FILE not set in environment variables")
    if not os.path.exists(creds_file):
        raise FileNotFoundError(f"Credentials file not found at: {creds_file}")
    return creds_file

@lru_cache(maxsize=1)
def get_credentials() -> Credentials:
    """Get and cache Google API credentials."""
    token_path = 'token.pickle'
    creds = None
    
    # Load existing token if present
    if os.path.exists(token_path):
        try:
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        except Exception as e:
            print(f"Error loading token: {str(e)}")
    
    # Refresh or create new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing credentials: {str(e)}")
                creds = None
        
        if not creds:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    get_credentials_path(),
                    SCOPES
                )
                creds = flow.run_local_server(port=0)
            except Exception as e:
                raise RuntimeError(f"Failed to create new credentials: {str(e)}")
        
        # Save credentials
        try:
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        except Exception as e:
            print(f"Warning: Failed to save token: {str(e)}")
    
    return creds

# Direct testing
if __name__ == "__main__":
    print("\nTesting Google API Credentials:")
    try:
        # Test credentials loading
        print("1. Testing credential initialization...")
        creds = get_credentials()
        print("✓ Credentials initialized successfully")
        
        # Test token validity
        print("\n2. Testing token validity...")
        if creds.valid:
            print("✓ Token is valid")
        else:
            print("✗ Token is invalid")
        
        # Test scopes
        print("\n3. Testing scopes...")
        if hasattr(creds, 'scopes'):
            print("Authorized scopes:")
            for scope in creds.scopes:
                print(f"  - {scope}")
        else:
            print("✗ No scopes found")
        
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        print(f"\nTest failed: {str(e)}")
        import traceback
        print("\nFull traceback:")
        print(traceback.format_exc())