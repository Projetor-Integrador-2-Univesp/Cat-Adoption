"""Configuração de desenvolvimento com banco SQLite isolado.

Uso: python manage.py runserver --settings=sistema_bastet.settings_recuperacao
"""

from .settings import *  # noqa: F401,F403

# Sobrescreve a conexão do projeto para usar somente o SQLite local.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db_recuperacao.sqlite3",
    }
}

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]
