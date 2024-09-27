"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 5.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os
# import dj_database_url

from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECURITY WARNING: don't run with debug turned on in production!
SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = os.getenv('DEBUG', 'False') == 'True'
# ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS").split(",")

ALLOWED_HOSTS = ['localhost', '127.0.0.1','localhost:8000']

# INTERNAL_IPS = [
#     '127.0.0.1',
# ]

# django default development phase
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
# EMAIL_USE_SSL = True
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# only for development
CORS_ALLOW_ALL_ORIGINS = True

# For development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
]

# Allow CORS for localhost:3000 (Next.js)
CORS_ALLOW_CREDENTIALS = True  # To allow cookies to be sent in cross-origin requests
CORS_ORIGIN_WHITELIST = [
    'http://localhost:3000',  # Next.js frontend
]

# Allow all headers (optional, you can be more restrictive)
CORS_ALLOW_HEADERS = ['*']
ALLOWED_HOSTS  = ['*']

# SESSION_COOKIE_DOMAIN = 'http://localhost:3000'
# CSRF_COOKIE_DOMAIN = 'http://localhost:3000'
SESSION_COOKIE_SAMESITE = 'Lax'  # Allow cross-site cookies
# SESSION_COOKIE_SECURE = True      # Requires HTTPS for cookies
# CSRF_COOKIE_SAMESITE = 'None'
# CSRF_COOKIE_SECURE = True

# custom Auth user model
AUTH_USER_MODEL = 'api.custUser'

DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100MB in bytes
FILE_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100MB in bytes

# Application definition

INSTALLED_APPS = [
    # channels
    'channels',

    # corsheaders
    'corsheaders',

    # daphne
    'daphne',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # sites to interface or differiate between sites
    'django.contrib.sites',

    # restframework
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'rest_framework_simplejwt',

    # install app api
    'api',

    # django-allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    # tailwind modules
    # 'tailwind',
    # 'new_theme', 

    # storages 
    'storages',
]

TAILWIND_APP_NAME = 'theme'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ),
}

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    # 'allauth.account.auth_backends.AuthenticationBackend',
]

MIDDLEWARE = [
    # cors headers
    'corsheaders.middleware.CorsMiddleware',

    # whitenoise
    'whitenoise.middleware.WhiteNoiseMiddleware',

    # django-request-logging
    'request_logging.middleware.LoggingMiddleware',

    # my logger middleware
    'core.middleware.RequestLoggingMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Add the account middleware:
    "allauth.account.middleware.AccountMiddleware",

    # my redirect middleware
    # 'api.middleware.CustomRedirectMiddleware',
    # 'api.middleware.DeleteMessagesCookieMiddleware',
]

CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        # os.path.join(BASE_DIR, 'templates')
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
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

WSGI_APPLICATION = 'core.wsgi.application'

ASGI_APPLICATION = "core.asgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'

AZURE_ACCOUNT_NAME=os.getenv("AZURE_ACCOUNT_NAME")
AZURE_ACCOUNT_KEY=os.getenv("AZURE_ACCOUNT_KEY")
AZURE_CONTAINER=os.getenv("AZURE_CONTAINER")
# AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")

# DATABASES = {
#     'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv("DB_NAME"),
        'USER': os.getenv("DB_USER"),
        'PASSWORD': os.getenv("DB_PASSWORD"),
        'HOST': os.getenv("DB_HOST"),  # This should match the service name in docker-compose.yml
        'PORT': os.getenv("DB_PORT"),
    }
}

CELERY_IMPORTS = ('api.tasks',)
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_BROKER", "redis://redis:6379/0")
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [os.environ.get('REDIS_URL', 'redis://redis:6379/1')],
        },
    },
}

# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels.layers.InMemoryChannelLayer"
#     }
# }

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': "redis://0.0.0.0:6379/",  # Update with your Redis server details if necessary
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


# Google configuration
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv("GOOGLE_KEY")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv("GOOGLE_SECRET")

SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
]

# Define SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE to get extra permissions from Google.
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
    }
}

ACCOUNT_ADAPTER = 'api.account_adapter.MyAccountAdapter'
# LOGIN_REDIRECT_URL = 'http://localhost:3000'
SOCIALACCOUNT_ADAPTER = 'api.social_adapter.MySocialAccountAdapter'

SITE_ID = 8


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Check if the media folder exists, if not, create it
if not os.path.exists(MEDIA_ROOT):
    os.makedirs(MEDIA_ROOT)

if not os.path.exists(f'{MEDIA_ROOT}/compressed_videos'):
    os.makedirs(f'{MEDIA_ROOT}/compressed_videos')

if not os.path.exists(f'{MEDIA_ROOT}/attachments'):
    os.makedirs(f'{MEDIA_ROOT}/attachments')

if not os.path.exists(f'{MEDIA_ROOT}/hls_videos'):
    os.makedirs(f'{MEDIA_ROOT}/hls_videos')


# logging settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'celery.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',  
            'propagate': False,
        },
        'api': { 
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'celery': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

