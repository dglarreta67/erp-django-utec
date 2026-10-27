import os
import dj_database_url
from .settings import *

# Eliminar variable legacy heredada de settings.py para evitar conflicto en Django 4.2+
if 'STATICFILES_STORAGE' in globals():
    del STATICFILES_STORAGE

# DEBUG se controla desde Render (Environment -> DEBUG). Por defecto False.
# Solo ponlo en True un momento para ver errores, y luego borra la variable.
DEBUG = os.environ.get('DEBUG', 'False').strip().lower() in ('1', 'true', 'yes')

SECRET_KEY = os.environ.get('SECRET_KEY', 'secret-key-prod-placeholder')

_render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')
_extra_hosts = os.environ.get('ALLOWED_HOSTS', '').split(',')

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*'] + (
    [_render_host] if _render_host else []
) + [h for h in _extra_hosts if h]

DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}

CSRF_TRUSTED_ORIGINS = []
if _render_host:
    CSRF_TRUSTED_ORIGINS.append(f'https://{_render_host}')

# Render termina el HTTPS en su proxy; sin esto el login del admin puede fallar
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False') == 'True'
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'False') == 'True'
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True

WHITENOISE_MANIFEST_STRICT = False

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# Con DEBUG=False Django no imprime los errores 500 por defecto.
# Esto los manda a la consola para que aparezcan en Render -> Logs.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {'handlers': ['console'], 'level': 'INFO'},
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}