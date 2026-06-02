#!/bin/bash
# Build script for Render deployment
set -e

echo "Installing Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Copy branding images to static folder
mkdir -p static/images
cp icon.png static/images/icon.png 2>/dev/null || true
cp worldwide.jpg static/images/worldwide.jpg 2>/dev/null || true

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Build completed successfully!"
