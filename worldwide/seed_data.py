#!/usr/bin/env python
"""
Seed script for Worldwide e-shopping LTD demo database.
Creates categories, products (local + import), site settings, and demo data.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'worldwide.settings')
os.chdir('/home/geek/allwithhermes/worldwide')
sys.path.insert(0, '/home/geek/allwithhermes/worldwide')
django.setup()

from products.models import Category, Brand, Product
from accounts.models import User
from core.models import SiteSettings, Banner
from decimal import Decimal


def seed_site_settings():
    """Create or update site settings."""
    ss, created = SiteSettings.objects.get_or_create(
        pk=1,
        defaults={
            "site_name": "Worldwide e-shopping LTD",
            "tagline": "We help you buy products on Alibaba, Amazon, eBay, and many more...",
            "footer_text": "&copy; 2026 Worldwide e-shopping LTD. Kigali, Rwanda. All rights reserved.",
            "facebook_url": "https://web.facebook.com/epurchaseworldwide/",
            "contact_email": "info@worldwideshopping.rw",
            "contact_phone": "+250 788 123 456",
            "contact_address": "Kigali, Rwanda",
            "currency": "RWF",
            "currency_symbol": "RWF",
            "default_shipping_cost_per_kg": Decimal("12.00"),
            "default_service_fee_percent": Decimal("10.00"),
            "default_usd_to_rwf_rate": Decimal("1350.00"),
            "mtn_momo_enabled": True,
            "airtel_money_enabled": True,
            "stripe_enabled": False,
            "cod_enabled": True,
        }
    )
    if not created:
        ss.site_name = "Worldwide e-shopping LTD"
        ss.tagline = "We help you buy products on Alibaba, Amazon, eBay, and many more..."
        ss.facebook_url = "https://web.facebook.com/epurchaseworldwide/"
        ss.save()
    print(f"SiteSettings: {'created' if created else 'updated'} - {ss.site_name}")
    return ss


def seed_categories():
    """Create product categories with icons."""
    cats = [
        {"name": "Electronics & Gadgets", "icon": "laptop", "featured": True, "order": 1},
        {"name": "Fashion & Clothing", "icon": "shirt", "featured": True, "order": 2},
        {"name": "Home & Living", "icon": "home", "featured": True, "order": 3},
        {"name": "Sports & Fitness", "icon": "dumbbell", "featured": True, "order": 4},
        {"name": "Beauty & Health", "icon": "sparkles", "featured": True, "order": 5},
        {"name": "Automotive Parts", "icon": "car", "featured": True, "order": 6},
        {"name": "Tools & Hardware", "icon": "wrench", "featured": True, "order": 7},
        {"name": "Kids & Toys", "icon": "baby", "featured": True, "order": 8},
        {"name": "Office & School", "icon": "briefcase-business", "featured": True, "order": 9},
        {"name": "Phones & Accessories", "icon": "smartphone", "featured": True, "order": 10},
    ]
    created_cats = []
    for c in cats:
        cat, created = Category.objects.get_or_create(
            name=c["name"],
            defaults={"icon": c["icon"], "featured": c["featured"], "is_active": True, "order": c["order"]}
        )
        if not created:
            cat.icon = c["icon"]
            cat.featured = c["featured"]
            cat.is_active = True
            cat.order = c["order"]
            cat.save(update_fields=["icon", "featured", "is_active", "order", "updated_at"])
        created_cats.append(cat)
        print(f"Category: {'created' if created else 'exists'} - {cat.name}")
    return created_cats


def seed_brands():
    """Create some brands."""
    brand_names = [
        "Samsung", "Apple", "Nike", "Adidas", "Xiaomi", "Huawei", "Sony", "LG",
        "Lenovo", "Anker", "Baseus", "Logitech", "Oraimo", "JBL", "HP", "Generic",
    ]
    brands = []
    for name in brand_names:
        b, created = Brand.objects.get_or_create(name=name, defaults={"is_active": True})
        brands.append(b)
        print(f"Brand: {'created' if created else 'exists'} - {b.name}")
    return brands


def seed_import_products(categories):
    """Create import on-demand products from Alibaba/Amazon with auto-pricing."""
    import_products = [
        {
            "name": "Wireless Bluetooth Earbuds Pro",
            "category": "Electronics & Gadgets",
            "origin_platform": "alibaba",
            "source_url": "https://www.alibaba.com/product-detail/Wireless-Bluetooth-Earbuds-Pro_1600234567890.html",
            "original_price_usd": Decimal("8.50"),
            "weight": Decimal("0.3"),
            "description": "High-quality wireless Bluetooth 5.3 earbuds with active noise cancellation, 30-hour battery life, IPX5 waterproof. Perfect for sports and daily use.",
            "short_description": "Bluetooth 5.3 earbuds with ANC, 30hr battery",
            "is_featured": True,
            "estimated_delivery_days": "10-14 days",
        },
        {
            "name": "Smart Watch Fitness Tracker",
            "category": "Electronics & Gadgets",
            "origin_platform": "alibaba",
            "source_url": "https://www.alibaba.com/product-detail/Smart-Watch-Fitness-Tracker_1600345678901.html",
            "original_price_usd": Decimal("15.00"),
            "weight": Decimal("0.5"),
            "description": "Advanced smartwatch with heart rate monitor, SpO2 tracking, GPS, sleep monitoring, and 7-day battery life. Compatible with Android and iOS.",
            "short_description": "Smartwatch with HR, SpO2, GPS, 7-day battery",
            "is_featured": True,
            "estimated_delivery_days": "10-14 days",
        },
        {
            "name": "Portable Power Bank 20000mAh",
            "category": "Electronics & Gadgets",
            "origin_platform": "alibaba",
            "source_url": "https://www.alibaba.com/product-detail/Power-Bank-20000mAh_1600456789012.html",
            "original_price_usd": Decimal("12.00"),
            "weight": Decimal("0.8"),
            "description": "Fast-charging 20000mAh power bank with USB-C PD 65W, dual USB-A ports, LED display. Charges laptop, phone, and tablet simultaneously.",
            "short_description": "20000mAh PD 65W power bank with LED display",
            "is_featured": False,
            "estimated_delivery_days": "10-14 days",
        },
        {
            "name": "Men's Casual Sneakers - Trendy 2026",
            "category": "Fashion & Clothing",
            "origin_platform": "trendyol",
            "source_url": "https://www.trendyol.com/mens-casual-sneakers-p-123456789",
            "original_price_usd": Decimal("22.00"),
            "weight": Decimal("1.2"),
            "description": "Comfortable men's casual sneakers with breathable mesh upper, memory foam insole, and durable rubber outsole. Available in sizes 40-45.",
            "short_description": "Comfortable casual sneakers, sizes 40-45",
            "is_featured": True,
            "estimated_delivery_days": "14-21 days",
        },
        {
            "name": "Women's Crossbody Bag - Leather",
            "category": "Fashion & Clothing",
            "origin_platform": "alibaba",
            "source_url": "https://www.alibaba.com/product-detail/Womens-Leather-Crossbody-Bag_1600567890123.html",
            "original_price_usd": Decimal("18.00"),
            "weight": Decimal("0.6"),
            "description": "Genuine leather women's crossbody bag with adjustable strap, multiple compartments, and gold-tone hardware. Elegant design for everyday use.",
            "short_description": "Genuine leather crossbody bag, elegant design",
            "is_featured": True,
            "estimated_delivery_days": "10-14 days",
        },
        {
            "name": "LED Desk Lamp with USB Charging",
            "category": "Home & Living",
            "origin_platform": "alibaba",
            "source_url": "https://www.alibaba.com/product-detail/LED-Desk-Lamp-USB_1600678901234.html",
            "original_price_usd": Decimal("9.50"),
            "weight": Decimal("1.5"),
            "description": "Adjustable LED desk lamp with 5 brightness levels, 3 color temperatures, USB charging port, and touch control. Eye-care technology for reduced strain.",
            "short_description": "LED desk lamp with USB port, 5 brightness levels",
            "is_featured": False,
            "estimated_delivery_days": "10-14 days",
        },
        {
            "name": "Yoga Mat Non-Slip 6mm",
            "category": "Sports & Fitness",
            "origin_platform": "amazon",
            "source_url": "https://www.amazon.com/dp/B09XYZ123456",
            "original_price_usd": Decimal("14.00"),
            "weight": Decimal("1.0"),
            "description": "Premium non-slip yoga mat, 6mm thick, eco-friendly TPE material. Includes carrying strap. Perfect for yoga, pilates, and floor exercises.",
            "short_description": "6mm non-slip yoga mat, eco-friendly TPE",
            "is_featured": True,
            "estimated_delivery_days": "14-21 days",
        },
        {
            "name": "Resistance Bands Set (5pcs)",
            "category": "Sports & Fitness",
            "origin_platform": "amazon",
            "source_url": "https://www.amazon.com/dp/B09ABC789012",
            "original_price_usd": Decimal("7.50"),
            "weight": Decimal("0.5"),
            "description": "Set of 5 resistance bands with different resistance levels. Includes door anchor, ankle straps, and carry bag. Full-body workout at home.",
            "short_description": "5pc resistance bands set with accessories",
            "is_featured": False,
            "estimated_delivery_days": "14-21 days",
        },
        {
            "name": "Vitamin C Serum for Face",
            "category": "Beauty & Health",
            "origin_platform": "alibaba",
            "source_url": "https://www.alibaba.com/product-detail/Vitamin-C-Serum-Face_1600789012345.html",
            "original_price_usd": Decimal("4.50"),
            "weight": Decimal("0.2"),
            "description": "20% Vitamin C serum with hyaluronic acid and vitamin E. Brightens skin, reduces dark spots, and anti-aging. 30ml bottle.",
            "short_description": "20% Vitamin C serum, brightening & anti-aging",
            "is_featured": True,
            "estimated_delivery_days": "10-14 days",
        },
        {
            "name": "Car Phone Mount - Magnetic",
            "category": "Automotive Parts",
            "origin_platform": "alibaba",
            "source_url": "https://www.alibaba.com/product-detail/Car-Phone-Mount-Magnetic_1600890123456.html",
            "original_price_usd": Decimal("6.00"),
            "weight": Decimal("0.3"),
            "description": "Strong magnetic car phone mount for air vent. Compatible with all smartphones. 360-degree rotation, one-hand operation.",
            "short_description": "Magnetic car phone mount, 360 rotation",
            "is_featured": False,
            "estimated_delivery_days": "10-14 days",
        },
        {
            "name": "Kids Educational Tablet",
            "category": "Kids & Toys",
            "origin_platform": "alibaba",
            "source_url": "https://www.alibaba.com/product-detail/Kids-Educational-Tablet_1600901234567.html",
            "original_price_usd": Decimal("35.00"),
            "weight": Decimal("0.8"),
            "description": "7-inch kids educational tablet with parental control, pre-loaded learning apps, shockproof case, and 64GB storage. Ages 3-12.",
            "short_description": "7-inch kids tablet with parental control, 64GB",
            "is_featured": True,
            "estimated_delivery_days": "10-14 days",
        },
        {
            "name": "Wireless Mouse Ergonomic",
            "category": "Electronics & Gadgets",
            "origin_platform": "aliexpress",
            "source_url": "https://www.aliexpress.com/item/1005001234567890.html",
            "original_price_usd": Decimal("5.50"),
            "weight": Decimal("0.2"),
            "description": "Ergonomic wireless mouse with 2.4GHz connectivity, 1600 DPI, silent clicks. Comfortable for long work sessions.",
            "short_description": "Ergonomic wireless mouse, silent clicks",
            "is_featured": False,
            "estimated_delivery_days": "14-21 days",
        },
        {
            "name": "USB-C Fast Charger 65W GaN",
            "category": "Phones & Accessories",
            "origin_platform": "aliexpress",
            "source_url": "https://www.aliexpress.com/item/1005006543210001.html",
            "original_price_usd": Decimal("11.80"),
            "weight": Decimal("0.25"),
            "description": "Compact 65W GaN charger for phones, tablets, and USB-C laptops with smart heat protection.",
            "short_description": "65W GaN USB-C charger",
            "is_featured": True,
            "estimated_delivery_days": "14-21 days",
        },
        {
            "name": "Laptop Backpack Anti-Theft USB",
            "category": "Office & School",
            "origin_platform": "alibaba",
            "source_url": "https://www.alibaba.com/product-detail/Laptop-Backpack-Anti-Theft_1600111222333.html",
            "original_price_usd": Decimal("16.40"),
            "weight": Decimal("0.9"),
            "description": "Water-resistant laptop backpack with lockable zippers, padded 15.6-inch compartment, and USB cable pass-through.",
            "short_description": "Anti-theft laptop backpack",
            "is_featured": True,
            "estimated_delivery_days": "10-14 days",
        },
        {
            "name": "Electric Drill Set 21V Cordless",
            "category": "Tools & Hardware",
            "origin_platform": "alibaba",
            "source_url": "https://www.alibaba.com/product-detail/Cordless-Drill-Set-21V_1600222333444.html",
            "original_price_usd": Decimal("29.50"),
            "weight": Decimal("2.4"),
            "description": "Cordless drill kit with battery, charger, bit set, torque control, and carry case for home repairs.",
            "short_description": "21V cordless drill kit",
            "is_featured": True,
            "estimated_delivery_days": "10-14 days",
        },
        {
            "name": "Robot Vacuum Cleaner Smart Mapping",
            "category": "Home & Living",
            "origin_platform": "amazon",
            "source_url": "https://www.amazon.com/dp/B0SMARTVAC001",
            "original_price_usd": Decimal("89.00"),
            "weight": Decimal("3.8"),
            "description": "Smart robot vacuum with app control, scheduling, anti-drop sensors, and strong suction for tiles and carpets.",
            "short_description": "Smart robot vacuum cleaner",
            "is_featured": True,
            "estimated_delivery_days": "14-21 days",
        },
        {
            "name": "Baby Stroller Foldable Travel",
            "category": "Kids & Toys",
            "origin_platform": "alibaba",
            "source_url": "https://www.alibaba.com/product-detail/Foldable-Baby-Stroller_1600333444555.html",
            "original_price_usd": Decimal("52.00"),
            "weight": Decimal("6.0"),
            "description": "Lightweight foldable baby stroller with sun canopy, storage basket, safety belt, and smooth wheels.",
            "short_description": "Foldable baby stroller",
            "is_featured": True,
            "estimated_delivery_days": "10-21 days",
        },
        {
            "name": "Makeup Brush Set 12 Pieces",
            "category": "Beauty & Health",
            "origin_platform": "alibaba",
            "source_url": "https://www.alibaba.com/product-detail/Makeup-Brush-Set_1600444555666.html",
            "original_price_usd": Decimal("6.25"),
            "weight": Decimal("0.35"),
            "description": "Soft synthetic makeup brush set for foundation, powder, contour, eyeshadow, and travel use.",
            "short_description": "12pc makeup brush set",
            "is_featured": True,
            "estimated_delivery_days": "10-14 days",
        },
        {
            "name": "Dash Camera 1080p Night Vision",
            "category": "Automotive Parts",
            "origin_platform": "aliexpress",
            "source_url": "https://www.aliexpress.com/item/1005009876500011.html",
            "original_price_usd": Decimal("24.00"),
            "weight": Decimal("0.45"),
            "description": "Compact 1080p dash camera with wide-angle lens, loop recording, G-sensor, and night vision.",
            "short_description": "1080p car dash camera",
            "is_featured": True,
            "estimated_delivery_days": "14-21 days",
        },
        {
            "name": "Air Fryer 5L Digital",
            "category": "Home & Living",
            "origin_platform": "alibaba",
            "source_url": "https://www.alibaba.com/product-detail/Digital-Air-Fryer-5L_1600555666777.html",
            "original_price_usd": Decimal("38.00"),
            "weight": Decimal("4.0"),
            "description": "Digital 5L air fryer with non-stick basket, timer, temperature control, and family-size capacity.",
            "short_description": "5L digital air fryer",
            "is_featured": True,
            "estimated_delivery_days": "10-21 days",
        },
    ]

    created_products = []
    for p in import_products:
        cat_name = p.pop("category")
        cat = Category.objects.filter(name=cat_name).first()
        if not cat:
            print(f"WARNING: Category '{cat_name}' not found, skipping {p['name']}")
            continue

        product, created = Product.objects.get_or_create(
            name=p["name"],
            defaults={
                **p,
                "category": cat,
                "product_type": "import",
                "in_stock": True,
                "stock_quantity": 999,
                "is_active": True,
                "is_new": True,
                "service_fee_percent": Decimal("10.00"),
                "shipping_cost_per_kg": Decimal("12.00"),
                "usd_to_rwf_rate": Decimal("1350.00"),
            }
        )
        created_products.append(product)
        price_rwf = product.calculated_price_rwf
        print(f"Import Product: {'created' if created else 'exists'} - {product.name} | {price_rwf:,.0f} RWF" if price_rwf else f"Import Product: {'created' if created else 'exists'} - {product.name}")
    return created_products


def seed_local_products(categories):
    """Create local stock products (already in Kigali)."""
    local_products = [
        {
            "name": "Samsung Galaxy A15 - 128GB",
            "category": "Electronics & Gadgets",
            "price": Decimal("185000.00"),
            "description": "Samsung Galaxy A15 with 128GB storage, 6.5\" display, 50MP camera. Available for immediate pickup in Kigali.",
            "short_description": "Samsung A15 128GB - Ready in Kigali",
            "stock_quantity": 25,
            "is_featured": True,
        },
        {
            "name": "T-Shirt Cotton - Black",
            "category": "Fashion & Clothing",
            "price": Decimal("8500.00"),
            "description": "100% cotton black t-shirt, premium quality. Available in S, M, L, XL. Pickup today in Kigali.",
            "short_description": "Premium cotton black t-shirt",
            "stock_quantity": 100,
            "is_featured": False,
        },
        {
            "name": "Bluetooth Speaker JBL Style",
            "category": "Electronics & Gadgets",
            "price": Decimal("35000.00"),
            "description": "Portable Bluetooth speaker with deep bass, 12-hour battery, waterproof. Same-day delivery in Kigali.",
            "short_description": "Portable BT speaker, 12hr battery, waterproof",
            "stock_quantity": 50,
            "is_featured": True,
        },
        {
            "name": "Running Shoes - Unisex",
            "category": "Sports & Fitness",
            "price": Decimal("45000.00"),
            "description": "Lightweight running shoes with cushioned sole. Sizes 38-44. Available for immediate pickup.",
            "short_description": "Lightweight running shoes, sizes 38-44",
            "stock_quantity": 30,
            "is_featured": True,
        },
        {
            "name": "Oraimo 10000mAh Power Bank",
            "category": "Phones & Accessories",
            "price": Decimal("22000.00"),
            "description": "Original Oraimo 10000mAh power bank with dual USB output, available for same-day delivery in Kigali.",
            "short_description": "Oraimo power bank ready in Kigali",
            "stock_quantity": 40,
            "is_featured": True,
        },
        {
            "name": "HP EliteBook Core i5 Refurbished",
            "category": "Office & School",
            "price": Decimal("285000.00"),
            "description": "Clean refurbished HP EliteBook Core i5 laptop with SSD storage, charger, and local warranty.",
            "short_description": "Refurbished HP EliteBook Core i5",
            "stock_quantity": 12,
            "is_featured": True,
        },
        {
            "name": "Logitech K120 USB Keyboard",
            "category": "Electronics & Gadgets",
            "price": Decimal("14500.00"),
            "description": "Durable wired USB keyboard with comfortable keys, ready for office and school setups.",
            "short_description": "Logitech wired USB keyboard",
            "stock_quantity": 60,
            "is_featured": True,
        },
        {
            "name": "School Backpack Waterproof",
            "category": "Office & School",
            "price": Decimal("18000.00"),
            "description": "Water-resistant backpack for school, work, and daily travel with padded straps and laptop space.",
            "short_description": "Waterproof school backpack",
            "stock_quantity": 35,
            "is_featured": True,
        },
        {
            "name": "Electric Kettle 1.8L",
            "category": "Home & Living",
            "price": Decimal("16500.00"),
            "description": "Fast-boil 1.8L electric kettle with auto shut-off and stainless steel heating plate.",
            "short_description": "1.8L electric kettle",
            "stock_quantity": 28,
            "is_featured": True,
        },
        {
            "name": "Car Jump Starter Portable",
            "category": "Automotive Parts",
            "price": Decimal("68000.00"),
            "description": "Portable car jump starter with USB output, flashlight, and safety clamps for emergency use.",
            "short_description": "Portable car jump starter",
            "stock_quantity": 10,
            "is_featured": True,
        },
        {
            "name": "Kids Building Blocks 500pcs",
            "category": "Kids & Toys",
            "price": Decimal("24000.00"),
            "description": "Creative building blocks set with 500 pieces for learning, imagination, and family play.",
            "short_description": "500pc building blocks set",
            "stock_quantity": 22,
            "is_featured": True,
        },
        {
            "name": "Digital Bathroom Scale",
            "category": "Beauty & Health",
            "price": Decimal("19000.00"),
            "description": "Accurate digital bathroom scale with clear LCD display and slim glass design.",
            "short_description": "Digital bathroom scale",
            "stock_quantity": 30,
            "is_featured": True,
        },
        {
            "name": "Tool Box 19 Inch",
            "category": "Tools & Hardware",
            "price": Decimal("27500.00"),
            "description": "Strong 19-inch tool box with removable tray and secure latches for home and workshop tools.",
            "short_description": "19-inch tool box",
            "stock_quantity": 18,
            "is_featured": True,
        },
        {
            "name": "Women's Summer Dress",
            "category": "Fashion & Clothing",
            "price": Decimal("28000.00"),
            "description": "Lightweight women's summer dress with comfortable fit, available for immediate pickup.",
            "short_description": "Women's casual summer dress",
            "stock_quantity": 20,
            "is_featured": True,
        },
    ]

    created_products = []
    for p in local_products:
        cat_name = p.pop("category")
        cat = Category.objects.filter(name=cat_name).first()
        if not cat:
            continue

        product, created = Product.objects.get_or_create(
            name=p["name"],
            defaults={
                **p,
                "category": cat,
                "product_type": "local",
                "in_stock": True,
                "is_active": True,
                "is_new": True,
                "weight": Decimal("0.5"),
            }
        )
        created_products.append(product)
        print(f"Local Product: {'created' if created else 'exists'} - {product.name} | {product.price:,.0f} RWF")
    return created_products


def seed_admin_user():
    """Create a default staff account for local setup."""
    user, created = User.objects.get_or_create(
        email="admin@worldwide.com",
        defaults={
            "username": "admin",
            "is_staff": True,
            "is_superuser": True,
            "is_active": True,
        },
    )
    if created:
        user.set_password("admin123")
        user.save()
    else:
        changed = False
        if not user.is_staff or not user.is_superuser:
            user.is_staff = True
            user.is_superuser = True
            changed = True
        if not user.username:
            user.username = "admin"
            changed = True
        if changed:
            user.save()
    print(f"Admin user: {'created' if created else 'ready'} - admin@worldwide.com / admin123")
    return user


if __name__ == "__main__":
    print("=" * 60)
    print("SEEDING Worldwide e-shopping LTD Database")
    print("=" * 60)

    seed_site_settings()
    seed_admin_user()
    print()
    categories = seed_categories()
    print()
    seed_brands()
    print()
    print("--- Import Products (Auto-Priced from USD to RWF) ---")
    import_products = seed_import_products(categories)
    print()
    print("--- Local Stock Products ---")
    local_products = seed_local_products(categories)
    print()
    print("=" * 60)
    print(f"DONE: {len(import_products)} import + {len(local_products)} local products created")
    print("=" * 60)
