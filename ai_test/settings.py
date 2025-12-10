import os
import dj_database_url

# -------------------------------
# DEBUG & ALLOWED_HOSTS
# -------------------------------

# Use environment variable DEBUG, default False for safety
DEBUG = os.environ.get("DEBUG", "False") == "True"

# Allowed hosts for Render deployment
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")
# Example: ALLOWED_HOSTS="recruter-drive-ai.onrender.com,localhost"

# -------------------------------
# DATABASE CONFIGURATION
# -------------------------------

DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get(
            "DATABASE_URL",
            "postgresql://postgres:12345@localhost:5432/Recruitment"
        ),
        conn_max_age=600,
        ssl_require=True  # Render PostgreSQL needs SSL
    )
}

# -------------------------------
# STATIC & MEDIA (Render ready)
# -------------------------------

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Enable WhiteNoise storage for compression & caching
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
