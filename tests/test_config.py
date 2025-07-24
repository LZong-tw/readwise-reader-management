import pytest
import os
from unittest.mock import patch, mock_open
from config import Config


class TestConfig:
    """Test cases for Config class"""
    
    def test_init_with_env_token(self):
        """Test config initialization with environment variable token"""
        with patch.dict(os.environ, {'READWISE_TOKEN': 'test_token_from_env'}):
            config = Config()
            assert config.api_token == 'test_token_from_env'
            assert config.base_url == "https://readwise.io/api/v3"
            assert config.auth_url == "https://readwise.io/api/v2/auth/"
    
    def test_init_with_file_token(self):
        """Test config initialization with token from file"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('builtins.open', mock_open(read_data='test_token_from_file')):
                config = Config()
                assert config.api_token == 'test_token_from_file'
    
    def test_init_no_token_raises_error(self):
        """Test config initialization raises error when no token is found"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('builtins.open', side_effect=FileNotFoundError):
                with pytest.raises(ValueError, match="Readwise API token not found"):
                    Config()
    
    def test_save_token(self, tmp_path):
        """Test saving token to file"""
        with patch.dict(os.environ, {'READWISE_TOKEN': 'old_token'}):
            config = Config()
            
            # Mock the file writing
            with patch('builtins.open', mock_open()) as mock_file:
                config.save_token('new_token')
                
                # Check that file was written
                mock_file.assert_called_once_with('.readwise_token', 'w')
                mock_file().write.assert_called_once_with('new_token')
                
                # Check that the token was updated
                assert config.api_token == 'new_token'
    
    def test_get_headers(self):
        """Test getting API headers"""
        with patch.dict(os.environ, {'READWISE_TOKEN': 'test_token'}):
            config = Config()
            headers = config.get_headers()
            
            assert headers == {
                "Authorization": "Token test_token",
                "Content-Type": "application/json"
            }
    
    def test_token_priority_env_over_file(self):
        """Test that environment variable takes priority over file"""
        with patch.dict(os.environ, {'READWISE_TOKEN': 'env_token'}):
            with patch('builtins.open', mock_open(read_data='file_token')):
                config = Config()
                assert config.api_token == 'env_token'