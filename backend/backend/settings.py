from pathlib import Path
import os
from decouple import config
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# ✅ SECURITY
SECRET_KEY = config('SECRET_KEY', default='your-dev-secret-key')
DEBUG = config('DEBUG', default=False, cast=bool)
# ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='aspirexbackend.onrender.com,127.0.0.1,localhost').split(',')
# ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='aspirexbackend.onrender.com').split(',')
ALLOWED_HOSTS = ['*']
# Allow Render external hostname dynamically
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# ✅ APPLICATIONS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    'storages',
    'chat',
    'mentor',
    'student.apps.StudentConfig',
    'community',
    'unified_auth',

    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'channels',
    'events',
]

# ✅ ASGI / CHANNELS
ASGI_APPLICATION = 'backend.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

# ✅ MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Use only for fallback if needed
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

# ✅ TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'backend.wsgi.application'

# ✅ DATABASE
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'))
    )
}

# ✅ PASSWORD VALIDATORS
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ✅ LANGUAGE / TIMEZONE
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ✅ STATIC FILES - Using Cloudinary
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'cloudinary_storage.storage.StaticHashedCloudinaryStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# ✅ MEDIA FILES - Using Cloudinary
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"DEBUG: {DEBUG}")
logger.info(f"DEFAULT_FILE_STORAGE: {DEFAULT_FILE_STORAGE}")


# ✅ EMAIL CONFIG
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ✅ CORS & CSRF
CORS_ALLOWED_ORIGINS = [
    "https://aspire-x.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://aspire-n8cn506nk-harsh-chauhans-projects-9fc7d68c.vercel.app",
    "http://127.0.0.1",
]

CSRF_TRUSTED_ORIGINS = [
    "https://aspire-x.vercel.app",
    "https://aspirexbackend.onrender.com",
    "http://localhost:5173",
    "https://aspire-n8cn506nk-harsh-chauhans-projects-9fc7d68c.vercel.app",
    "http://127.0.0.1",
    
]

# ✅ SECURITY HEADERS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# ✅ AUTH
AUTH_USER_MODEL = 'student.Student'

AUTHENTICATION_BACKENDS = [
    'backend.backends.MultiUserBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Google OAuth Settings
GOOGLE_OAUTH2_CLIENT_ID = config('GOOGLE_OAUTH2_CLIENT_ID', default='')
GOOGLE_OAUTH2_CLIENT_SECRET = config('GOOGLE_OAUTH2_CLIENT_SECRET', default='')
GOOGLE_OAUTH2_REDIRECT_URI = config('GOOGLE_OAUTH2_REDIRECT_URI', default='http://127.0.0.1:8000/api/auth/google/callback/')

# Google OAuth Scopes
GOOGLE_OAUTH2_SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
]

# ✅ REST FRAMEWORK
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'unified_auth.authentication.StudentOrMentorTokenAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ]
}

USE_SUPABASE = config('USE_SUPABASE', default=False, cast=bool)

if not USE_SUPABASE:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


    # """
    # Django settings for backend project.

    # Generated by 'django-admin startproject' using Django 5.2.

    # For more information on this file, see
    # https://docs.djangoproject.com/en/5.2/topics/settings/

    # For the full list of settings and their values, see
    # https://docs.djangoproject.com/en/5.2/ref/settings/
    # """

    # from pathlib import Path
    # import os
    # from decouple import config

    # # Build paths inside the project like this: BASE_DIR / 'subdir'.
    # BASE_DIR = Path(__file__).resolve().parent.parent


    # # Quick-start development settings - unsuitable for production
    # # See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

    # # SECURITY WARNING: keep the secret key used in production secret!
    # SECRET_KEY = 'django-insecure-sa9co(d(sd!fjr^1=v62p-5-e4o&00af((dbjbz6mbrc98xz=g'

    # # SECURITY WARNING: don't run with debug turned on in production!
    # DEBUG = True

    # ALLOWED_HOSTS = ['localhost', '127.0.0.1']


    # # Application definition

    # INSTALLED_APPS = [
    #     'django.contrib.admin',
    #     'django.contrib.auth',
    #     'django.contrib.contenttypes',
    #     'django.contrib.sessions',
    #     'django.contrib.messages',
    #     'django.contrib.staticfiles',
    #     'chat',
    #     'mentor',
    #     'storages',
    #     'corsheaders',
    #     'rest_framework',
    #     'rest_framework.authtoken',
    #     'student.apps.StudentConfig',
    #     'cloudinary',
    #     'cloudinary_storage',
    # ]


    # INSTALLED_APPS += ['channels']

    # # Set ASGI application
    # ASGI_APPLICATION = 'backend.asgi.application'

    # # Channel Layer config (using Redis)
    # CHANNEL_LAYERS = {
    #     "default": {
    #         "BACKEND": "channels_redis.core.RedisChannelLayer",
    #         "CONFIG": {
    #             "hosts": [("127.0.0.1", 6379)],
    #         },
    #     },
    # }





    # MIDDLEWARE = [
    #     'corsheaders.middleware.CorsMiddleware',
    #     'django.middleware.common.CommonMiddleware',
    #     'django.middleware.security.SecurityMiddleware',
    #     'django.contrib.sessions.middleware.SessionMiddleware',
    #     'django.middleware.csrf.CsrfViewMiddleware',
    #     'django.contrib.auth.middleware.AuthenticationMiddleware',
    #     'django.contrib.messages.middleware.MessageMiddleware',
    #     'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # ]

    # AUTH_USER_MODEL = 'student.Student'

    # CORS_ALLOWED_ORIGINS = [
    #     "http://localhost:5173",  # Vite default port
    # ]
    # CORS_ALLOW_CREDENTIALS = True
    # CORS_ALLOW_ALL_ORIGINS = True  # TEMPORARY for debugging, remove in production

    # AUTHENTICATION_BACKENDS = [
    #     'backend.backends.MultiUserBackend',  # Custom backend for both
    #     'django.contrib.auth.backends.ModelBackend',  # Fallback
    # ]

    # REST_FRAMEWORK = {

    #     'DEFAULT_PERMISSION_CLASSES': [
    #         'rest_framework.permissions.AllowAny',
    #         'rest_framework.authentication.TokenAuthentication',
    #         'rest_framework.authentication.SessionAuthentication'
    #     ]
    # }



    # ROOT_URLCONF = 'backend.urls'

    # TEMPLATES = [
    #     {
    #         'BACKEND': 'django.template.backends.django.DjangoTemplates',
    #         'DIRS': [],
    #         'APP_DIRS': True,
    #         'OPTIONS': {
    #             'context_processors': [
    #                 'django.template.context_processors.request',
    #                 'django.contrib.auth.context_processors.auth',
    #                 'django.contrib.messages.context_processors.messages',
    #             ],
    #         },
    #     },
    # ]

    # WSGI_APPLICATION = 'backend.wsgi.application'


    # # Database
    # # https://docs.djangoproject.com/en/5.2/ref/settings/#databases

    # DATABASES = {
    #     'default': {
    #         'ENGINE': 'django.db.backends.sqlite3',
    #         'NAME': BASE_DIR / 'db.sqlite3',
    #     }
    # }


    # # Password validation
    # # https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

    # AUTH_PASSWORD_VALIDATORS = [
    #     {
    #         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    #     },
    #     {
    #         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    #     },
    #     {
    #         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    #     },
    #     {
    #         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    #     },
    # ]


    # # Internationalization
    # # https://docs.djangoproject.com/en/5.2/topics/i18n/

    # LANGUAGE_CODE = 'en-us'

    # TIME_ZONE = 'UTC'

    # USE_I18N = True

    # USE_TZ = True


    # # Static files (CSS, JavaScript, Images)
    # # https://docs.djangoproject.com/en/5.2/howto/static-files/

    # STATIC_URL = 'static/'

    # # Default primary key field type
    # # https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

    # DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

    # # settings.py
    # MEDIA_URL = '/media/'
    # MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

    # # Email configuration using python-decouple
    # EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    # EMAIL_HOST = 'smtp.gmail.com'
    # EMAIL_PORT = 587
    # EMAIL_USE_TLS = True
    # EMAIL_HOST_USER = config('EMAIL_HOST_USER')
    # EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
    # DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

    # # Razorpay API keys (securely loaded from .env)
    # RAZORPAY_KEY_ID = config('RAZORPAY_KEY_ID')
    # RAZORPAY_KEY_SECRET = config('RAZORPAY_KEY_SECRET')

    # # MEDIA STORAGE CONFIGURATION
    # # Use Cloudinary in production, local storage in development
    # USE_CLOUDINARY = config('USE_CLOUDINARY', default=False, cast=bool)

    # if USE_CLOUDINARY:
    #     DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    #     CLOUDINARY_STORAGE = {
    #         'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME'),
    #         'API_KEY': config('CLOUDINARY_API_KEY'),
    #         'API_SECRET': config('CLOUDINARY_API_SECRET'),
    #     }
    #     MEDIA_URL = f"https://res.cloudinary.com/{config('CLOUDINARY_CLOUD_NAME')}/"
    # else:
    #     MEDIA_URL = '/media/'
    #     MEDIA_ROOT = os.path.join(BASE_DIR, 'media')