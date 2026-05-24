import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-secret-key-change-me')
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'corsheaders',
    'gateway',
    'usuarios',
    'vacantes',
    'candidatos',
    'postulaciones',
    'evaluaciones',
    'historial',
    'soa_services',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'config.urls'
TEMPLATES = []
WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'sigetad_db'),
        'USER': os.getenv('POSTGRES_USER', 'sigetad_user'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'sigetad_pass'),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True
from corsheaders.defaults import default_headers, default_methods
CORS_ALLOW_HEADERS = list(default_headers) + ['authorization']
CORS_ALLOW_METHODS = list(default_methods)

BUS_HOST = os.getenv('BUS_HOST', 'localhost')
BUS_PORT = int(os.getenv('BUS_PORT', '5000'))

TOKEN_MAX_AGE_SECONDS = 60 * 60 * 8

# Seguridad de contraseñas
# Django hashea todas las contraseñas usando PBKDF2-SHA256
# con 720.000 iteraciones por defecto (OWASP recomendado)
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]
