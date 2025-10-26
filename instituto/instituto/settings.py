from pathlib import Path
import os
import importlib.util

# ==========================
# Cargar variables desde .env (si existe)
# ==========================
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ.setdefault(key, value)

# ==========================
# Configuración base
# ==========================
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "REEMPLAZAME_EN_DESARROLLO")

def env_bool(name, default=False):
    val = os.environ.get(name)
    if val is None:
        return default
    return str(val).lower() in {"1", "true", "yes", "on"}

DEBUG = env_bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")
CSRF_TRUSTED_ORIGINS = [o for o in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if o]

# ==========================
# Seguridad
# ==========================
if not DEBUG:  # Solo en producción
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    REFERRER_POLICY = "strict-origin-when-cross-origin"
else:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False

# ==========================
# Aplicaciones
# ==========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'apps.blog',
    'apps.comentarios',
    'apps.usuarios',
    'whitenoise.runserver_nostatic',
]

# Detectar CKEditor instalado
_ckeditor_apps = []
if importlib.util.find_spec('ckeditor') is not None:
    _ckeditor_apps.append('ckeditor')
if importlib.util.find_spec('ckeditor_uploader') is not None:
    _ckeditor_apps.append('ckeditor_uploader')
if importlib.util.find_spec('django_ckeditor_5') is not None:
    _ckeditor_apps.append('django_ckeditor_5')
INSTALLED_APPS += _ckeditor_apps

# ==========================
# Middleware
# ==========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'instituto.urls'

# ==========================
# Templates
# ==========================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.parent / 'templates'],
        'APP_DIRS': True,  # ✅ volvemos a True para evitar el error de loaders
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'instituto.wsgi.application'

# ==========================
# Base de datos
# ==========================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ==========================
# Caché
# ==========================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'app-cache',
    }
}

# ==========================
# Archivos estáticos y media
# ==========================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR.parent / 'static']  # 👈 sube un nivel
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.parent / 'media'  # 👈 también sube un nivel

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==========================
# Usuario personalizado
# ==========================
AUTH_USER_MODEL = 'usuarios.Usuario'

# ==========================
# Configuración CKEditor Clásico
# ==========================
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_ALLOW_NONIMAGE_FILES = False
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Full',
        'height': 300,
        'width': '100%',
        'extraPlugins': ','.join(['uploadimage', 'image2']),
        'removePlugins': 'stylesheetparser',
    }
}

# ==========================
# Configuración CKEditor 5
# ==========================
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|',
            'bold', 'italic', 'underline', 'strikethrough', 'link', 'blockQuote',
            '|',
            'bulletedList', 'numberedList', 'insertTable', 'imageUpload',
            '|',
            'undo', 'redo'
        ],
        'image': {
            # Mantener solo herramientas que suelen venir en el build por defecto
            'toolbar': [
                'imageTextAlternative',
                'toggleImageCaption',
                'imageStyle:inline',
                'imageStyle:block',
                'imageStyle:side'
            ],
            'styles': ['inline', 'block', 'side'],
        },
        'simpleUpload': {
            'uploadUrl': '/ckeditor5/upload/',
        },
        'table': {
            'contentToolbar': [
                'tableColumn', 'tableRow', 'mergeTableCells', 'tableProperties', 'tableCellProperties'
            ],
        },
    }
}


