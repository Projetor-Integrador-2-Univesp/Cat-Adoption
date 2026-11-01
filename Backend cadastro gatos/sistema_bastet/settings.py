"""Configurações do Django para o Lar Bastet."""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env_list(nome):
    return [valor.strip() for valor in os.getenv(nome, "").split(",") if valor.strip()]


def env_bool(nome, padrao=False):
    valor = os.getenv(nome)
    if valor is None:
        return padrao
    return valor.strip().lower() in {"1", "true", "yes", "on"}


# O ambiente de recuperação usa um banco SQLite separado.
IS_RECUPERACAO = os.getenv("DJANGO_SETTINGS_MODULE", "").endswith(".settings_recuperacao")
DEBUG = env_bool("DJANGO_DEBUG", padrao=IS_RECUPERACAO)

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY") or os.getenv("SECRET_KEY")
if not SECRET_KEY:
    if IS_RECUPERACAO:
        SECRET_KEY = "somente-ambiente-local-de-recuperacao-nao-usar-em-producao"
    else:
        raise ImproperlyConfigured("Configure DJANGO_SECRET_KEY no ambiente.")

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS")
if IS_RECUPERACAO and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured("Configure DJANGO_ALLOWED_HOSTS no ambiente.")

INSTALLED_APPS = [
    "gatos",
    "corsheaders",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "sistema_bastet.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "sistema_bastet.wsgi.application"

# O SQLite sobrescreve esta configuração em settings_recuperacao.py.
if not IS_RECUPERACAO:
    obrigatorias = ["DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT"]
    ausentes = [nome for nome in obrigatorias if not os.getenv(nome)]
    if ausentes:
        raise ImproperlyConfigured(
            "Variáveis do PostgreSQL ausentes: " + ", ".join(ausentes)
        )

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", ""),
        "USER": os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", ""),
        "PORT": os.getenv("DB_PORT", "5432"),
        "OPTIONS": {"sslmode": "require"},
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS")
if IS_RECUPERACAO and not CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS = ["http://127.0.0.1:5500", "http://localhost:5500"]
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")

# O Render encaminha o esquema HTTPS pelo proxy reverso.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env_bool(
    "DJANGO_SECURE_SSL_REDIRECT", padrao=(not DEBUG and not IS_RECUPERACAO)
)
SESSION_COOKIE_SECURE = not DEBUG and not IS_RECUPERACAO
CSRF_COOKIE_SECURE = not DEBUG and not IS_RECUPERACAO
