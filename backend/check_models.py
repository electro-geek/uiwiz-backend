import google.generativeai as genai
import os
import sys

# Add backend to path to import config_reader
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from lumina_backend.config_reader import get_config

try:
    config = get_config()
    api_key = config.get('gemini.api_key')
    if not api_key:
        print("API Key not found")
        sys.exit(1)
        
    genai.configure(api_key=api_key)
    print("Listing models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Model: {m.name}")
except Exception as e:
    print(f"Error: {e}")
