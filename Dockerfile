# Use a slim image for faster builds and deployments
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies for PostgreSQL and building tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the entire project
COPY . .

# Prepare static and media directories
RUN mkdir -p /app/staticfiles /app/media /app/logs
RUN touch /app/logs/django.log

# Run collectstatic during build to prepare whitenoise files
RUN python manage.py collectstatic --noinput

# Dynamic Port Binding: Important for Render and other cloud providers
CMD gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 4 --timeout 120 khoutwa_backend.wsgi:application