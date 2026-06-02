# WorldWide E-Commerce Platform

**GitHub Repository**: https://github.com/pammcharm/worldwide

A modern, full-featured Django e-commerce platform with integrated payment systems for Rwanda (MTN MoMo, Airtel Money), international payments (Stripe), and Supabase authentication.

## 🚀 Quick Start

### Local Development (5 minutes)

```bash
# 1. Clone repository
git clone https://github.com/pammcharm/worldwide.git
cd worldwide/worldwide

# 2. Run setup script
chmod +x setup.sh
./setup.sh

# 3. Start server
python manage.py runserver

# Visit http://localhost:8000
```

### Production on Render (Step-by-step in DEPLOYMENT.md)

```bash
git push origin main
# Render auto-deploys from main branch
```

## ✨ Features

- **Multi-Payment**: MTN MoMo, Airtel Money, Stripe, Cash on Delivery
- **Authentication**: Email/Password + Supabase OAuth
- **E-Commerce**: Products, Cart, Orders, Shipping, Reviews, Wishlist
- **Images**: Local or S3 storage with fallback placeholders
- **Security**: HMAC webhook verification, HTTPS, CSRF protection
- **Mobile**: Responsive TailwindCSS design, auto-polling payment status

## 📋 Technology Stack

- Django 5.1+ | PostgreSQL (Supabase) | Stripe & Paypack API
- TailwindCSS | Alpine.js | WhiteNoise
- Deploy: Render.com | Storage: Local or S3

## 📚 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide for Render + Supabase
- **[README.md](README.md)** - Project overview and API endpoints

## 🔧 Setup & Configuration

### Local Development
```bash
cp .env.example .env
# Edit .env with local settings (DEBUG=True)
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Production (Render)

1. **Push to GitHub**
   ```bash
   git push origin main
   ```

2. **Connect Render** (render.com)
   - New Web Service
   - Select GitHub repository
   - Build: `bash build.sh`
   - Start: `gunicorn worldwide.wsgi:application`

3. **Set Environment Variables** (See DEPLOYMENT.md)
   - Database: Supabase PostgreSQL connection string
   - Secrets: Stripe, Paypack, EMAIL credentials
   - Security: HTTPS redirect, secure cookies

4. **Configure Webhooks**
   - Stripe: `https://app.onrender.com/checkout/payments/webhook/stripe/`
   - Paypack: `https://app.onrender.com/checkout/payments/webhook/momo/`

## 🖼️ Image Management

### Development
Images automatically served from `/media/` directory

### Production

**Option 1: Local Filesystem** (Default - Recommended for Render)
```
USE_S3_STORAGE=False
Images: /media/products/, /media/categories/, /media/avatars/
```

**Option 2: S3/Supabase Storage** (CDN - Recommended for Global)
```
USE_S3_STORAGE=True
AWS_STORAGE_BUCKET_NAME=your-bucket
AWS_S3_ACCESS_KEY_ID=xxx
AWS_S3_SECRET_ACCESS_KEY=xxx
```

**Upload Images**
```bash
# Admin interface
# Or via management command:
python manage.py download_product_images --product-id=123 --source-url=https://example.com/image.jpg
```

## 🔐 Security Checklist

- ✅ HMAC-SHA256 webhook verification
- ✅ HTTPS + HSTS headers
- ✅ CSRF + Secure cookies
- ✅ Environment variables for secrets
- ✅ `.env` in `.gitignore`
- ✅ No hardcoded credentials

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Images not showing | Run `python manage.py collectstatic` |
| Database connection error | Verify `DATABASE_URL` in `.env` |
| Webhook failures | Check webhook secret matches payment provider |
| Static files 404 | Collect static: `python manage.py collectstatic --noinput --clear` |

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed troubleshooting.

## 📞 Support

- Django Docs: https://docs.djangoproject.com
- Render: https://render.com/docs
- Supabase: https://supabase.com/docs
- Stripe: https://stripe.com/docs
- Paypack: https://developers.paypack.rw

## 📝 Project Structure

```
worldwide/
├── manage.py
├── requirements.txt
├── Procfile                    # Render config
├── build.sh                    # Build script
├── setup.sh                    # Local setup
├── DEPLOYMENT.md               # Production guide
├── README.md                   # Overview
├── .env.example                # Config template
├── accounts/                   # Authentication
├── products/                   # E-commerce
├── orders/                     # Order processing
├── payments/                   # Payment handling
├── cart/ reviews/ wishlist/    # Features
└── templates/static/media/     # Frontend
```

## 🚀 Deployment Steps Summary

1. **Clone**: `git clone` this repo
2. **Setup**: Run `./setup.sh` locally to test
3. **Push**: `git push origin main`
4. **Deploy**: Connect to Render from GitHub
5. **Configure**: Add environment variables
6. **Launch**: Render auto-deploys on push

## 💡 Key Features Implemented

✅ Paypack webhook with HMAC signature verification
✅ Mobile popup status polling every 3 seconds
✅ Local + S3 image storage options
✅ Supabase PostgreSQL database integration
✅ Secure payment endpoints
✅ Admin dashboard
✅ Product management
✅ Order tracking
✅ User authentication

## 📄 License

Proprietary - All rights reserved

---

**Ready to deploy?** Follow the step-by-step guide in [DEPLOYMENT.md](DEPLOYMENT.md)!
