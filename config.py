import os
from typing import Optional

class Config:
    """Readwise API configuration management"""
    
    def __init__(self):
        self.api_token = self._get_api_token()
        self.base_url = "https://readwise.io/api/v3"
        self.auth_url = "https://readwise.io/api/v2/auth/"
        
    def _get_api_token(self) -> str:
        """Get API token from environment variable or file"""
        # First try to get from environment variable
        token = os.getenv('READWISE_TOKEN')
        
        if not token:
            # Try to read from file
            try:
                with open('.readwise_token', 'r') as f:
                    token = f.read().strip()
            except FileNotFoundError:
                pass
        
        if not token:
            print("Please set your Readwise API token:")
            print("1. Set environment variable: export READWISE_TOKEN=your_token")
            print("2. Or create .readwise_token file and write your token")
            print("3. Get your token from: https://readwise.io/access_token")
            raise ValueError("Readwise API token not found")
            
        return token
    
    def save_token(self, token: str) -> None:
        """Save API token to file"""
        with open('.readwise_token', 'w') as f:
            f.write(token)
        self.api_token = token
        print("API token saved")
    
    def get_headers(self) -> dict:
        """Get API request headers"""
        return {
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "application/json"
        } 