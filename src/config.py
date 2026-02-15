#!/usr/bin/env python3
"""
Configuration management for Captive Portal Auto-Login
Handles credentials and settings from .env file or environment variables
"""

import os
from pathlib import Path
from typing import Tuple, Optional

class ConfigManager:
    """Manage configuration from .env file or environment variables"""
    
    # Environment variable names
    USERNAME_VAR = "CAPTIVE_PORTAL_USERNAME"
    PASSWORD_VAR = "CAPTIVE_PORTAL_PASSWORD"
    LOGIN_URL_VAR = "CAPTIVE_PORTAL_URL"
    
    # Default values
    DEFAULT_LOGIN_URL = "http://172.16.1.3:8002/index.php?zone=lan"
    DEFAULT_TIMEOUT = 900  # 15 minutes
    DEFAULT_REDIRECT_URL = "https://www.mnit.ac.in"
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize ConfigManager
        
        Args:
            project_root: Path to project root. If None, uses parent of src directory
        """
        if project_root is None:
            # Assume this file is in src/ directory
            project_root = Path(__file__).parent.parent
        
        self.project_root = project_root
        self.env_file = project_root / ".env"
        self._env_vars = {}
        self._load_env_file()
    
    def _load_env_file(self):
        """Load variables from .env file"""
        if not self.env_file.exists():
            return
        
        try:
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip("'\"")
                        self._env_vars[key] = value
        except Exception as e:
            print(f"⚠️ Warning: Could not read .env file: {e}")
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a configuration value from environment variables or .env file
        
        Args:
            key: Variable name
            default: Default value if not found
        
        Returns:
            Configuration value or default
        """
        # Check environment variables first
        if key in os.environ:
            return os.environ[key]
        
        # Check .env file
        if key in self._env_vars:
            return self._env_vars[key]
        
        return default
    
    def get_credentials(self) -> Tuple[str, str]:
        """
        Get username and password
        
        Returns:
            Tuple of (username, password)
        
        Raises:
            ValueError: If credentials are not configured
        """
        username = self.get(self.USERNAME_VAR)
        password = self.get(self.PASSWORD_VAR)
        
        if not username or not password:
            raise ValueError(
                f"Credentials not configured!\n"
                f"Please set {self.USERNAME_VAR} and {self.PASSWORD_VAR}\n"
                f"Run: python3 install/install.py"
            )
        
        return username, password
    
    def get_login_url(self) -> str:
        """Get captive portal login URL"""
        return self.get(self.LOGIN_URL_VAR, self.DEFAULT_LOGIN_URL)
    
    def get_timeout(self) -> int:
        """Get login attempt timeout in seconds"""
        timeout_str = self.get("CAPTIVE_PORTAL_TIMEOUT")
        if timeout_str:
            try:
                return int(timeout_str)
            except ValueError:
                pass
        return self.DEFAULT_TIMEOUT
    
    def get_redirect_url(self) -> str:
        """Get redirect URL after login"""
        return self.get("CAPTIVE_PORTAL_REDIRECT_URL", self.DEFAULT_REDIRECT_URL)
    
    def set_credentials(self, username: str, password: str):
        """
        Update credentials in memory and .env file
        
        Args:
            username: New username
            password: New password
        """
        self._env_vars[self.USERNAME_VAR] = username
        self._env_vars[self.PASSWORD_VAR] = password
        self._save_env_file()
    
    def _save_env_file(self):
        """Save configuration to .env file"""
        try:
            content = "# Captive Portal Credentials\n"
            content += "# DO NOT COMMIT THIS FILE TO VERSION CONTROL\n\n"
            
            for key, value in self._env_vars.items():
                content += f'{key}="{value}"\n'
            
            self.env_file.write_text(content)
            
            # Restrict permissions on Unix
            import platform
            if platform.system() != "Windows":
                os.chmod(self.env_file, 0o600)
        except Exception as e:
            print(f"❌ Error saving .env file: {e}")
            raise


def load_config(project_root: Optional[Path] = None) -> ConfigManager:
    """
    Create and return a ConfigManager instance
    
    Args:
        project_root: Optional path to project root
    
    Returns:
        Initialized ConfigManager instance
    """
    return ConfigManager(project_root)


if __name__ == "__main__":
    # Test the config manager
    config = load_config()
    try:
        username, password = config.get_credentials()
        print(f"✅ Credentials loaded:")
        print(f"   Username: {username}")
        print(f"   Password: {'*' * len(password)}")
        print(f"   Login URL: {config.get_login_url()}")
        print(f"   Timeout: {config.get_timeout()}s")
    except ValueError as e:
        print(f"❌ {e}")
