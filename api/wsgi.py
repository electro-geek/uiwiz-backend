"""
Vercel serverless entry point for Django.
Adds backend to path and exposes the WSGI app as `app` (required by Vercel Python runtime).
"""
import os
import sys
from pathlib import Path

# Project root (uiwiz-backend)
ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lumina_backend.settings")

from lumina_backend.wsgi import application

# Vercel Python runtime looks for a variable named `app` (WSGI or ASGI)
app = application
