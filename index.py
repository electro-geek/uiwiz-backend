import os
import sys

# Get the path to the 'backend' folder
# Since index.py is now in the root, it's just 'backend' in the same directory
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')

if backend_path not in sys.path:
    sys.path.append(backend_path)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lumina_backend.settings')

from lumina_backend.wsgi import application

# Vercel looks for 'app'
app = application
