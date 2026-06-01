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
    'documentos',
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
MEDIA_ROOT = BASE_DIR / os.getenv('MEDIA_ROOT', 'uploads')
DOCUMENTOS_STORAGE_DIR = os.getenv('DOCUMENTOS_STORAGE_DIR', 'documentos')
DOCUMENTOS_MAX_UPLOAD_BYTES = int(os.getenv('DOCUMENTOS_MAX_UPLOAD_BYTES', str(10 * 1024 * 1024)))
DOCUMENTOS_DOWNLOAD_TOKEN_SECONDS = int(os.getenv('DOCUMENTOS_DOWNLOAD_TOKEN_SECONDS', str(10 * 60)))
CANDIDATE_FILE_TOKEN_SECONDS = int(os.getenv('CANDIDATE_FILE_TOKEN_SECONDS', str(5 * 60)))
LOGIN_MAX_FAILED_ATTEMPTS = int(os.getenv('LOGIN_MAX_FAILED_ATTEMPTS', '5'))
LOGIN_LOCKOUT_SECONDS = int(os.getenv('LOGIN_LOCKOUT_SECONDS', str(15 * 60)))
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
