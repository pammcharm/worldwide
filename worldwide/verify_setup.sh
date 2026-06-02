#!/bin/bash
# Verify images are set up correctly

echo "🔍 Verifying WorldWide E-Commerce Setup..."
echo "=========================================="

# Check for images in root
echo ""
echo "📁 Checking root directory images..."
ls -lh icon.png worldwide.jpg 2>/dev/null || echo "⚠️  Images not in root (will be copied during build)"

# Check media directory
echo ""
echo "📁 Checking media directory..."
if [ -d "media" ]; then
    echo "✅ media/ exists"
    ls -lh media/ 2>/dev/null | head -10
else
    echo "⚠️  media/ directory not found"
fi

# Check static directory
echo ""
echo "📁 Checking static directory..."
if [ -d "static" ]; then
    echo "✅ static/ exists"
    [ -f "static/images/icon.png" ] && echo "✅ static/images/icon.png exists" || echo "⚠️  icon.png not in static (will be copied during build)"
else
    echo "⚠️  static/ directory not found"
fi

# Check database
echo ""
echo "🗄️  Checking database..."
if [ -f "db.sqlite3" ]; then
    echo "✅ db.sqlite3 exists"
    sqlite3 db.sqlite3 "SELECT COUNT(*) as product_count FROM products_product;" 2>/dev/null || echo "⚠️  Cannot query database"
else
    echo "ℹ️  db.sqlite3 not found (will be created on first run)"
fi

# Check key configuration files
echo ""
echo "📋 Checking configuration files..."
[ -f ".env.example" ] && echo "✅ .env.example exists" || echo "⚠️  .env.example missing"
[ -f "requirements.txt" ] && echo "✅ requirements.txt exists" || echo "⚠️  requirements.txt missing"
[ -f "Procfile" ] && echo "✅ Procfile exists" || echo "⚠️  Procfile missing"
[ -f "build.sh" ] && echo "✅ build.sh exists" || echo "⚠️  build.sh missing"

# Check templates
echo ""
echo "📄 Checking templates..."
[ -f "templates/layouts/base.html" ] && echo "✅ base.html exists" || echo "⚠️  base.html missing"
[ -f "templates/products/list.html" ] && echo "✅ product list template exists" || echo "⚠️  product list template missing"

echo ""
echo "✅ Setup verification complete!"
echo ""
echo "Next steps:"
echo "1. python manage.py collectstatic --noinput"
echo "2. python manage.py migrate"
echo "3. python manage.py createsuperuser"
echo "4. python manage.py runserver"
