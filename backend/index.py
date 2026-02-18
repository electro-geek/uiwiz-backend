import os
import sys

# Add the directory containing index.py to the search path
# so that lumina_backend can be imported correctly by Vercel
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lumina_backend.settings')

from lumina_backend.wsgi import application

# Vercel looks for 'app' or 'handler'
app = application
