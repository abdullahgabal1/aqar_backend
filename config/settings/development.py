from .base import *
from decouple import config

DEBUG = config('DEBUG', default=True, cast=bool)

# Use local memory cache for development so Redis isn't strictly required
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Run Celery tasks synchronously in development
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_STORE_EAGER_RESULT = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Disable password validation in dev for easier testing
AUTH_PASSWORD_VALIDATORS = []

# Email backend for dev
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Celery in dev (e.g. eager mode if needed, but we'll use Redis)
# CELERY_TASK_ALWAYS_EAGER = True

# CORS
CORS_ALLOW_ALL_ORIGINS = True
