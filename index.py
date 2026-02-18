import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Get the path to the 'backend' folder
    project_root = os.path.dirname(os.path.abspath(__file__))
    backend_path = os.path.join(project_root, 'backend')
    
    logger.info(f"Project root: {project_root}")
    logger.info(f"Backend path: {backend_path}")

    if backend_path not in sys.path:
        sys.path.append(backend_path)

    # Set the Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lumina_backend.settings')

    from lumina_backend.wsgi import application
    
    # Vercel looks for 'app'
    app = application
    logger.info("Django application loaded successfully")

except Exception as e:
    logger.error(f"Failed to load Django application: {e}")
    raise e
