import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

def _bool(name, default=False):
    return os.environ.get(name, str(default)).lower() in {"1", "true", "yes", "on"}

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-insecure-change-me")
DEBUG = _bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

CORS_ALLOWED_ORIGINS = [
    o.strip() for o in os.environ.get(
        "DJANGO_CORS_ORIGINS", 'http://localhost:5173'
    ).split(",") if o.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "comercio",
    "pagos",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "comercio"),
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}

GESTION_VERIFY_TOKEN_URL = os.environ.get(
    "GESTION_VERIFY_TOKEN_URL", "http://127.0.0.1:8001/api/usuarios/verificar-token/"
)
CATALOGO_API_BASE_URL = os.environ.get("CATALOGO_API_BASE_URL", "http://127.0.0.1:8002/api")

# Transbank Webpay Plus sandbox (Integration).
# Las credenciales se cargan desde .env
TBK_COMMERCE_CODE = os.environ.get("TBK_COMMERCE_CODE", "")
TBK_API_KEY = os.environ.get("TBK_API_KEY", "")
TBK_ENVIRONMENT = os.environ.get("TBK_ENVIRONMENT", "TEST")
TBK_RETURN_URL = os.environ.get("TBK_RETURN_URL", "http://localhost:5173/pago/retorno")
TBK_ALLOWED_RETURN_URLS = [
    u.strip() for u in os.environ.get(
        "TBK_ALLOWED_RETURN_URLS", TBK_RETURN_URL
    ).split(",") if u.strip()
]
TBK_BACKEND_RETURN_URL = os.environ.get(
    "TBK_BACKEND_RETURN_URL", "http://127.0.0.1:8000/api/payments/return/"
)

TEST_RUNNER = "pagos.tests.MensajeEspanolRunner"