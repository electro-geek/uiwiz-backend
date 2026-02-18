import os
from pathlib import Path


class Config:
    def __init__(self, data):
        self.data = data

    def get(self, key, default=None):
        # Try Environment Variable first (dot replaced with underscore, uppercase)
        # e.g. django.secret_key -> DJANGO_SECRET_KEY
        env_key = key.replace('.', '_').upper()
        val = os.getenv(env_key)
        if val is not None:
            return val
        
        # Fallback to the properties file data
        return self.data.get(key, default)


def read_config(config_path=None):
    """Read config.properties and return a dict of settings."""
    if config_path is None:
        config_path = Path(__file__).resolve().parent.parent / 'config.properties'

    config = {}
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    
    # Even if file doesn't exist, we return empty dict which Config object will use
    return config


# Global config instance
_config = None


def get_config():
    """Get global config instance (lazy-loaded singleton wrapper)."""
    global _config
    if _config is None:
        config_data = read_config()
        _config = Config(config_data)
    return _config
