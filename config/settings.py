
"""
Django settings for config project.

Electronics Store Inventory Management System.
Conforms to Software Architecture and Design Specification (SAD) Sections 3.1, 3.4-3.9, 4.1.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file if present
env_file = BASE_DIR / '.env'
if env_file.exists():
    load_dotenv(dotenv_path=env_file, override=True)
else:
    load_dotenv(override=True)

# Security: Read secrets from environment variables
debug_val = os.getenv('DEBUG', 'False')
DEBUG = str(debug_val).lower() in ('true', '1', 'yes')

SECRET_KEY = os.environ.get('SECRET_KEY')

if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set.")

raw_allowed_hosts = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [h.strip() for h in raw_allowed_hosts.split(',') if h.strip()]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Project modules per SAD Section 4.1
    'accounts.apps.AccountsConfig',
    'inventory.apps.InventoryConfig',
    'dashboard.apps.DashboardConfig',
    'reports.apps.ReportsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Custom User Model configuration
AUTH_USER_MODEL = 'accounts.User'

# Database Configuration: MySQL through Django ORM
# Credentials and connection parameters are loaded from .env.
# Automated tests use an isolated SQLite database unless TEST_WITH_MYSQL is set.
is_testing = 'test' in sys.argv

if is_testing and not os.environ.get('TEST_WITH_MYSQL'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
else:
    DB_ENGINE = os.environ.get('DB_ENGINE', 'django.db.backends.mysql')
    if 'sqlite3' in DB_ENGINE:
        DATABASES = {
            'default': {
                'ENGINE': DB_ENGINE,
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': DB_ENGINE,
                'NAME': os.environ.get('DB_NAME', 'electronics_inventory'),
                'USER': os.environ.get('DB_USER', 'root'),
                'PASSWORD': os.environ.get('DB_PASSWORD', ''),
                'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
                'PORT': os.environ.get('DB_PORT', '3306'),
                'OPTIONS': {
                    'charset': 'utf8mb4',
                },
            }
        }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Authentication URLs & Flow
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'inventory:landing'
LOGOUT_REDIRECT_URL = 'login'

# Session and Cookie Security
# 30-minute session expiration on inactivity
SESSION_COOKIE_AGE = 1800
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

# Cache Configuration for login rate-limiting
# Local memory for tests, Redis in production when configured.
CACHE_URL = os.getenv('CACHE_URL')

if is_testing:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'electronics-auth-test-cache',
        }
    }

elif CACHE_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': CACHE_URL,
        }
    }

else:
    if not DEBUG:
        raise ValueError(
            "CACHE_URL must be set in production (DEBUG=False) for shared cache."
        )

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'electronics-auth-cache',
        }
    }

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
