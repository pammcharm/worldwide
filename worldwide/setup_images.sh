#!/bin/bash
# Copy branding images to static folder for deployment

echo "📁 Setting up static images..."

# Create static images directory
mkdir -p /home/geek/allwithhermes/worldwide/static/images

# Copy images from root to static
cp /home/geek/allwithhermes/worldwide/icon.png /home/geek/allwithhermes/worldwide/static/images/icon.png 2>/dev/null || echo "ℹ️  icon.png not in root"
cp /home/geek/allwithhermes/worldwide/worldwide.jpg /home/geek/allwithhermes/worldwide/static/images/worldwide.jpg 2>/dev/null || echo "ℹ️  worldwide.jpg not in root"

# Also create placeholder.png in media for fallback
convert -size 400x400 xc:linear-gradient:from-#ede9fe:to-#fce7f3 /home/geek/allwithhermes/worldwide/media/placeholder.png 2>/dev/null || echo "ℹ️  ImageMagick not available"

echo "✅ Static images setup complete"
