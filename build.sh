#!/usr/bin/env bash
# exit on error
set -o errexit

# Dependencies install karein
pip install -r requirements.txt

# Static files ko STATIC_ROOT (staticfiles folder) mein collect karein
python manage.py collectstatic --no-input

# Database migrations run karein
python manage.py migrate