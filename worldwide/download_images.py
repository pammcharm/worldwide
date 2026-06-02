#!/usr/bin/env python
"""
Update existing products with real online images from Unsplash/Pexels.
Run from Django project root with venv activated.
"""
import os, sys, subprocess, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'worldwide.settings')
os.chdir('/home/geek/allwithhermes/worldwide')
sys.path.insert(0, '/home/geek/allwithhermes/worldwide')
django.setup()

from products.models import Product, Category
from core.models import SiteSettings
from decimal import Decimal
import urllib.request
import uuid

MEDIA_DIR = '/home/geek/allwithhermes/worldwide/media/products'
os.makedirs(MEDIA_DIR, exist_ok=True)

# Map products to real free stock images (Unsplash source)
PRODUCT_IMAGES = {
    "Wireless Bluetooth Earbuds Pro": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400&h=400&fit=crop",
    "Smart Watch Fitness Tracker": "https://images.unsplash.com/photo-1546868871-af0de0ae72be?w=400&h=400&fit=crop",
    "Portable Power Bank 20000mAh": "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=400&h=400&fit=crop",
    "Men's Casual Sneakers - Trendy 2026": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop",
    "Women's Crossbody Bag - Leather": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=400&h=400&fit=crop",
    "LED Desk Lamp with USB Charging": "https://images.unsplash.com/photo-1507473885765-e6ed057ab6fe?w=400&h=400&fit=crop",
    "Yoga Mat Non-Slip 6mm": "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=400&h=400&fit=crop",
    "Resistance Bands Set (5pcs)": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=400&fit=crop",
    "Vitamin C Serum for Face": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=400&h=400&fit=crop",
    "Car Phone Mount - Magnetic": "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=400&h=400&fit=crop",
    "Kids Educational Tablet": "https://images.unsplash.com/photo-1544396821-4dd40b938aeb?w=400&h=400&fit=crop",
    "Wireless Mouse Ergonomic": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400&h=400&fit=crop",
    "Samsung Galaxy A15 - 128GB": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=400&h=400&fit=crop",
    "T-Shirt Cotton - Black": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=400&fit=crop",
    "Bluetooth Speaker JBL Style": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400&h=400&fit=crop",
    "Running Shoes - Unisex": "https://images.unsplash.com/photo-1460353581641-37baddab0fa2?w=400&h=400&fit=crop",
    "USB-C Fast Charger 65W GaN": "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=400&h=400&fit=crop",
    "Laptop Backpack Anti-Theft USB": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400&h=400&fit=crop",
    "Electric Drill Set 21V Cordless": "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=400&h=400&fit=crop",
    "Robot Vacuum Cleaner Smart Mapping": "https://images.unsplash.com/photo-1603618090561-412154b4bd1b?w=400&h=400&fit=crop",
    "Baby Stroller Foldable Travel": "https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?w=400&h=400&fit=crop",
    "Makeup Brush Set 12 Pieces": "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=400&h=400&fit=crop",
    "Dash Camera 1080p Night Vision": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=400&h=400&fit=crop",
    "Air Fryer 5L Digital": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=400&fit=crop",
    "Oraimo 10000mAh Power Bank": "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=400&h=400&fit=crop",
    "HP EliteBook Core i5 Refurbished": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=400&fit=crop",
    "Logitech K120 USB Keyboard": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=400&h=400&fit=crop",
    "School Backpack Waterproof": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400&h=400&fit=crop",
    "Electric Kettle 1.8L": "https://commons.wikimedia.org/wiki/Special:FilePath/General_electric_-_electric_water_kettle.jpg?width=400",
    "Car Jump Starter Portable": "https://images.unsplash.com/photo-1606577924006-27d39b132ae2?w=400&h=400&fit=crop",
    "Kids Building Blocks 500pcs": "https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=400&h=400&fit=crop",
    "Digital Bathroom Scale": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=400&fit=crop",
    "Tool Box 19 Inch": "https://images.unsplash.com/photo-1530124566582-a618bc2615dc?w=400&h=400&fit=crop",
    "Women's Summer Dress": "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=400&h=400&fit=crop",
}

CATEGORY_IMAGES = {
    "Electronics & Gadgets": "https://images.unsplash.com/photo-1468495244123-6c6c332eeece?w=200&h=200&fit=crop",
    "Fashion & Clothing": "https://images.unsplash.com/photo-1445205170230-053b83016050?w=200&h=200&fit=crop",
    "Home & Living": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=200&h=200&fit=crop",
    "Sports & Fitness": "https://commons.wikimedia.org/wiki/Special:FilePath/EFTA00001133_-_Well-lit_fitness_room_featuring_exercise_equipment_including_a_treadmill_stationary_bike_weight_machines_and_a_pull-up_bar_on_a_wooden_floor_against_a_textured_wall.jpg?width=300",
    "Beauty & Health": "https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=200&h=200&fit=crop",
    "Automotive Parts": "https://images.unsplash.com/photo-1486262715619-67b85e0b08d3?w=200&h=200&fit=crop",
    "Tools & Hardware": "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=200&h=200&fit=crop",
    "Kids & Toys": "https://images.unsplash.com/photo-1558060370-d644479cb6f7?w=200&h=200&fit=crop",
    "Office & School": "https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=200&h=200&fit=crop",
    "Phones & Accessories": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=200&h=200&fit=crop",
}

def download_image(url, save_path):
    """Download image from URL."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            with open(save_path, 'wb') as f:
                f.write(resp.read())
        return True
    except Exception as e:
        print(f"  DOWNLOAD FAILED: {e}")
        return False


def update_product_images():
    """Download and assign images to products."""
    from products.models import ProductImage

    for product_name, url in PRODUCT_IMAGES.items():
        product = Product.objects.filter(name=product_name).first()
        if not product:
            print(f"  NOT FOUND: {product_name}")
            continue

        # Skip if already has images
        if product.images.exists():
            print(f"  SKIP (has images): {product_name}")
            continue

        ext = 'jpg'
        filename = f"{product.slug}-{uuid.uuid4().hex[:6]}.{ext}"
        save_path = os.path.join(MEDIA_DIR, filename)

        print(f"  Downloading: {product_name}...", end=" ")
        if download_image(url, save_path):
            relative_path = f"products/{filename}"
            ProductImage.objects.create(
                product=product,
                image=relative_path,
                is_primary=True,
                alt_text=product.name,
            )
            print(f"OK -> {relative_path}")
        else:
            print("FAILED")


def update_category_images():
    """Download and assign images to categories."""
    for cat_name, url in CATEGORY_IMAGES.items():
        cat = Category.objects.filter(name=cat_name).first()
        if not cat:
            continue
        if cat.image:
            print(f"  SKIP (has image): {cat.name}")
            continue

        ext = 'jpg'
        filename = f"{cat.slug}-{uuid.uuid4().hex[:6]}.{ext}"
        save_path = os.path.join('/home/geek/allwithhermes/worldwide/media/categories', filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        print(f"  Downloading: {cat.name}...", end=" ")
        if download_image(url, save_path):
            cat.image = f"categories/{filename}"
            cat.save()
            print(f"OK")
        else:
            print("FAILED")


if __name__ == "__main__":
    print("=" * 60)
    print("DOWNLOADING PRODUCT IMAGES")
    print("=" * 60)
    update_product_images()
    print()
    print("=" * 60)
    print("DOWNLOADING CATEGORY IMAGES")
    print("=" * 60)
    update_category_images()
    print()
    print("DONE")
