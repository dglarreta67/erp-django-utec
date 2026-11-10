from .settings import *  # noqa: F401,F403
import os
import dj_database_url

DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'secret-key-prod-placeholder')

_render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')
_extra_hosts = os.environ.get('ALLOWED_HOSTS', '').split(',')

ALLOWED_HOSTS = ['localhost', '127.0.0.1'] + (
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

SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False') == 'True'
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'False') == 'True'
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True

# ── ALMACENAMIENTO (Django 4.2: solo STORAGES, nunca STATICFILES_STORAGE) ──
# Estáticos: WhiteNoise con manifiesto. STRICT=False evita que collectstatic
# falle por referencias a archivos faltantes (p. ej. bootstrap.min.css.map).
WHITENOISE_MANIFEST_STRICT = False

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# ── ARCHIVOS MEDIA EN S3 (solo si AWS_STORAGE_BUCKET_NAME está definida) ──
# Variables a configurar en Render → Environment:
#   AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME,
#   AWS_S3_REGION_NAME, AWS_S3_CUSTOM_DOMAIN (opcional)

_bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME', '')

if _bucket:
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
    AWS_STORAGE_BUCKET_NAME = _bucket
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_DEFAULT_ACL = None            # el bucket controla el acceso
    AWS_S3_FILE_OVERWRITE = False     # no sobreescribir si el nombre ya existe
    AWS_QUERYSTRING_AUTH = False      # URLs públicas (sin firma)

    _custom_domain = os.environ.get('AWS_S3_CUSTOM_DOMAIN', '')
    if _custom_domain:
        AWS_S3_CUSTOM_DOMAIN = _custom_domain
        MEDIA_URL = f'https://{_custom_domain}/'
    else:
        MEDIA_URL = f'https://{_bucket}.s3.amazonaws.com/'

    STORAGES['default'] = {
        'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
    }