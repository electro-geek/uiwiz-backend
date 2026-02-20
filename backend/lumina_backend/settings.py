"""
Django settings for lumina_backend project.
Configuration is loaded from config.properties.
"""
import os
from pathlib import Path
from .config_reader import get_config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load configuration from config.properties
config = get_config()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.get('django.secret_key', 'django-insecure-change-me')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config.get('django.debug', 'True').lower() == 'true'

ALLOWED_HOSTS = [
    h.strip()
    for h in config.get('django.allowed_hosts', 'localhost,127.0.0.1').split(',')
]
# Vercel: allow *.vercel.app (Vercel sets VERCEL=1 in production)
if os.environ.get('VERCEL'):
    ALLOWED_HOSTS.append('.vercel.app')


# Application definition

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'api',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS - allow frontend origins from config
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in config.get(
        'cors.allowed_origins',
        'http://localhost:5173'
    ).split(',')
]
CORS_ALLOW_ALL_ORIGINS = DEBUG

ROOT_URLCONF = 'lumina_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'lumina_backend.wsgi.application'


# Database
# Configuration is read from config.properties; env vars override when set.
DATABASES = {
    'default': {
        'ENGINE': config.get('db.engine', 'django.db.backends.postgresql'),
        'NAME': config.get('db.name', 'uiwiz'),
        'USER': config.get('db.user', 'myuser'),
        'PASSWORD': config.get('db.password', 'example'),
        'HOST': config.get('db.host', 'localhost'),
        'PORT': config.get('db.port', '5432'),
        'OPTIONS': {
            'sslmode': config.get('db.sslmode', 'require' if not DEBUG else 'prefer'),
        }
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
}

# Gemini API config (from config.properties)
GEMINI_API_KEY = config.get('gemini.api_key', '')
GEMINI_MODEL = config.get('gemini.model', 'gemini-2.0-flash')

# Firebase config
FIREBASE_SERVICE_ACCOUNT_PATH = config.get('firebase.service_account_path', '')

# Encryption
ENCRYPTION_KEY = config.get('encryption.key', '')
