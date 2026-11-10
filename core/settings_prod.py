from .settings import *
import os
import dj_database_url

DEBUG = False
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

SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False') == 'True'
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'False') == 'True'
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# core/settings_prod.py — agregar al final, después de los SECURE_* headers:

# ── ALMACENAMIENTO DE ARCHIVOS MEDIA (producción) ─────────────────────────
# Usar django-storages con S3 para persistir archivos entre deploys.
# Configurar estas variables en el dashboard de Render:
#   AWS_ACCESS_KEY_ID       → Access Key del bucket
#   AWS_SECRET_ACCESS_KEY   → Secret Key del bucket
#   AWS_STORAGE_BUCKET_NAME → Nombre del bucket
#   AWS_S3_REGION_NAME      → Región (ej. us-east-1)
#   AWS_S3_CUSTOM_DOMAIN    → Dominio CDN opcional

_bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME', '')

if _bucket:
    # Solo activa S3 si la variable de entorno está configurada
    DEFAULT_FILE_STORAGE  = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID     = os.environ.get('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
    AWS_STORAGE_BUCKET_NAME = _bucket
    AWS_S3_REGION_NAME    = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_DEFAULT_ACL       = None        # el bucket controla el acceso
    AWS_S3_FILE_OVERWRITE = False       # no sobreescribir si el nombre ya existe
    AWS_QUERYSTRING_AUTH  = False       # URLs públicas (sin firma)
    MEDIA_URL             = f'https://{_bucket}.s3.amazonaws.com/'
