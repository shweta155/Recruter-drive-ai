"""
Django settings for ai_test project.
"""

from pathlib import Path
import os
import environ
import dj_database_url # Database connection ke liye

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Env variables read karne ke liye setup
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# Quick-start development settings - unsuitable for production
# SECURITY WARNING: keep the secret key used in production secret!
# Production me SECRET_KEY environment variable se ayega, warna default use hoga
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-rf^i_@h*%*-6bz7n5djy8d2r26z+e!y-s4=h2g83pv=uptw)gk")

# SECURITY WARNING: don't run with debug turned on in production!
# Render par DEBUG False hona chahiye
DEBUG = 'RENDER' not in os.environ

ALLOWED_HOSTS = [
    '127.0.0.1', 
    'localhost', 
    '.onrender.com' # Render domain allow karein
]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "app",
    "user_tests",
    "widget_tweaks",
    'recruitment',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware", # <-- ADDED: Static files serve karne ke liye
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ai_test.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "ai_test.wsgi.application"

# --- EMAIL SETTINGS ---
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "shweta.ladne.averybit@gmail.com"
EMAIL_HOST_PASSWORD = "qwgh jagp euzh qcwi"

# ----------------------------------------------------------------------
#                         DATABASE CONFIGURATION
# ----------------------------------------------------------------------

# Render par PostgreSQL aur Local par default (PostgreSQL/SQLite)
DATABASES = {
    'default': dj_database_url.config(
        # Render automatic DATABASE_URL set karta hai, hum use yahan fetch kar rahe hain
        default='postgresql://postgres:12345@localhost:5432/Recruitment',
        conn_max_age=600
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    { "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator" },
    { "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator" },
    { "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator" },
    { "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator" },
]

# API Keys
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", env("GEMINI_API_KEY", default=""))
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", env("OPENAI_API_KEY", default=""))

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ----------------------------------------------------------------------
#                         STATIC & MEDIA FILES
# ----------------------------------------------------------------------

STATIC_URL = "/static/"

# Production me static files yahan collect honge
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Enable WhiteNoise storage for compression and caching
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"