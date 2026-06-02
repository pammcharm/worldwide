# WorldWide E-Commerce Platform - Deployment Guide

A modern, secure Django e-commerce platform with support for MTN MoMo, Airtel Money, Stripe payments, and Supabase authentication.

## Features

✅ **Multi-Payment Support**
- MTN MoMo (Paypack Rwanda)
- Airtel Money (Paypack Rwanda)
- Stripe (International)
- Cash on Delivery (COD)

✅ **Authentication**
- Email/Password authentication
- Supabase OAuth (Google, GitHub)
- User profiles and addresses

✅ **E-Commerce**
- Product catalog with categories
- Shopping cart
- Order management
- Shipping integration
- Product reviews and wishlist
- Search functionality

✅ **Security**
- HMAC-SHA256 webhook verification
- SSL/TLS support
- CSRF protection
- Secure headers (HSTS, CSP, X-Frame-Options)
- Rate limiting on payment endpoints
- Secure password hashing

✅ **Image Management**
- Local filesystem storage (Render native)
- Optional S3/Supabase Storage for CDN
- Automatic image fallback
- Responsive image optimization

## Technology Stack

- **Backend**: Django 5.1+
- **Database**: PostgreSQL (Supabase)
- **Authentication**: Django Auth + Supabase
- **Payments**: Stripe, Paypack
- **Storage**: WhiteNoise for static files + Local/S3 media
- **Deployment**: Render.com
- **Frontend**: HTML5, TailwindCSS, Alpine.js

## Local Development

### Prerequisites

- Python 3.12+
- PostgreSQL 14+ (or SQLite for development)
- pip/uv package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/pammcharm/worldwide.git
   cd worldwide/worldwide
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create .env file**
   ```bash
   cp .env.example .env
   # Edit .env with your local settings - keep DEBUG=True for local dev
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

8. **Run development server**
   ```bash
   python manage.py runserver 8000
   ```

   Visit http://localhost:8000

## Production Deployment on Render

### Step 1: Prepare Your Project for Git

```bash
# Ensure .env is in .gitignore (it should already be)
git status  # Verify no .env files are staged

# Commit all project files
git add .
git commit -m "Initial commit: WorldWide e-commerce ready for production"
```

### Step 2: Push to GitHub

```bash
# If not already initialized
git init
git remote add origin https://github.com/pammcharm/worldwide.git
git branch -M main
git push -u origin main
```

### Step 3: Configure Supabase Database

1. Go to [supabase.com](https://supabase.com) and create a project
2. Get your **Connection String** from Settings > Database > URI
   - Format: `postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require`
3. Note the credentials for Render configuration

### Step 4: Deploy to Render

1. Go to [render.com](https://render.com) and sign in with GitHub
2. Click "New +" → "Web Service"
3. Select your GitHub repository
4. Configure basic settings:
   - **Name**: worldwide (or your choice)
   - **Environment**: Python 3.12
   - **Build Command**: `bash build.sh`
   - **Start Command**: `gunicorn worldwide.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --threads 2 --worker-class gthread`
   - **Instance Type**: Standard (512 MB RAM minimum)

### Step 5: Set Environment Variables in Render

In Render dashboard, add these environment variables under "Environment":

#### Core Django Settings
```
SECRET_KEY=<generate-long-random-string>
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com,yourdomain.com
```

#### Database - IMPORTANT: Use Supabase PostgreSQL
```
DATABASE_URL=postgresql://postgres.PROJECT_REF:PASSWORD@aws-0-region.pooler.supabase.com:6543/postgres?sslmode=require
```
⚠️ Replace with your Supabase connection string from Step 3

#### Supabase Auth (Optional)
```
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SECRET_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Payment Gateways
```
STRIPE_PUBLISHABLE_KEY=pk_live_xxx
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

PAYPACK_CLIENT_ID=your-client-id
PAYPACK_CLIENT_SECRET=your-client-secret
PAYPACK_WEBHOOK_SECRET=your-webhook-secret
```

#### Email Configuration
```
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
```

#### Security (Production)
```
SECURE_SSL_REDIRECT=True
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

#### Image Storage (Choose One)

**Option 1: Local Filesystem (Recommended for Render)**
```
USE_S3_STORAGE=False
```
Images stored in `/media/` directory (preserved between deploys if you set up Render disk)

**Option 2: S3/Supabase Storage (For CDN + Distributed)**
```
USE_S3_STORAGE=True
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1
AWS_S3_ACCESS_KEY_ID=your-access-key
AWS_S3_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_CUSTOM_DOMAIN=cdn.yourdomain.com  # Optional
```

### Step 6: (Optional) Configure Persistent Storage for Images

If using local filesystem storage, set up persistent disk on Render:

1. In Render dashboard, go to your service > Disks
2. Click "Add Disk"
   - **Name**: media
   - **Mount Path**: `/var/media`
   - **Size**: 10 GB (or as needed)
3. Update your settings to use persistent disk

Alternative: Use Render's `/var/www/html` persistent directory

### Step 7: Complete First Deployment

1. Click "Deploy" in Render
2. Wait for build to complete (5-10 minutes)
3. Check logs for any errors

```bash
# Monitor logs in real-time
Render Dashboard > Logs > toggle "Show Live Logs"
```

### Step 8: Initialize Database (First Time Only)

Migrations run automatically via the `release` command in Procfile, but create superuser manually:

1. Go to Render Dashboard > your service > Shell
2. Run:
   ```bash
   python manage.py createsuperuser
   ```

3. Access admin at `https://your-app-name.onrender.com/admin/`

## Image Management

### Images in Production

#### Using Local Filesystem (Default)

**Setup:**
```
USE_S3_STORAGE=False
```

**How it works:**
- Images stored in `media/` directory on server
- Served via Django views.static.serve
- Persisted using Render's disk feature

**Upload images:**
1. Admin Dashboard > Products
2. Add product with images via upload form
3. Or use management command:
   ```bash
   python manage.py download_product_images --product-id=123 --source-url=https://example.com/image.jpg
   ```

#### Using S3/Supabase Storage (CDN)

**Setup:**
```
USE_S3_STORAGE=True
AWS_STORAGE_BUCKET_NAME=your-bucket
AWS_S3_ACCESS_KEY_ID=xxx
AWS_S3_SECRET_ACCESS_KEY=xxx
```

**Benefits:**
- Images served from CDN (faster globally)
- Unlimited storage (pay-per-use)
- No server disk space needed
- Easy to scale

### Ensuring Images Display Properly

**Product Template Checks:**
```django
{% if primary_image %}
    <img src="{{ primary_image.image.url }}" alt="{{ product.name }}">
{% else %}
    <!-- Fallback: Unsplash placeholder -->
    <img src="https://source.unsplash.com/400x400/?product" alt="{{ product.name }}">
{% endif %}
```

**Collect Static Files on Deploy:**
```bash
# Automatically runs via build.sh
python manage.py collectstatic --noinput --clear
```

**Test Image Display:**
1. Admin > Upload product image
2. Visit product page
3. Image should display

## Setting Up Webhook Endpoints

### Stripe Webhooks

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/webhooks)
2. Add endpoint:
   - **URL**: `https://your-app-name.onrender.com/checkout/payments/webhook/stripe/`
   - **Events**: `payment_intent.succeeded`, `payment_intent.payment_failed`
3. Copy signing secret → add to Render as `STRIPE_WEBHOOK_SECRET`

### Paypack Webhooks

1. Go to [Paypack Dashboard](https://admin.paypack.rw) > Webhooks
2. Add endpoint:
   - **URL**: `https://your-app-name.onrender.com/checkout/payments/webhook/momo/`
   - **Method**: POST
   - **Events**: Transaction callbacks
3. Copy signing secret → add to Render as `PAYPACK_WEBHOOK_SECRET`

## Database Management

### Migrations

**Create migration:**
```bash
python manage.py makemigrations
```

**Apply migrations:**
```bash
python manage.py migrate
```

**On Render, migrations auto-run** via:
```
Procfile: release: python manage.py migrate --noinput
```

### Backup Data (Supabase)

1. Go to Supabase Dashboard > Project Settings > Database Backups
2. Set backup frequency (daily recommended)
3. Download backups from "Backups" tab

### Access PostgreSQL Console

```bash
# From Render shell
psql $DATABASE_URL
```

## Troubleshooting

### "No such file: media/products/image.jpg"

**Solution:**
```bash
# Ensure images are collected
python manage.py collectstatic --noinput --clear

# Check media directory
ls -la /var/media/

# Re-upload image via admin
```

### "Static files not loading"

**Solution:**
```bash
# In Render shell
python manage.py collectstatic --noinput --clear

# Check whitenoise is enabled in MIDDLEWARE
```

### Database Connection Error

**Solution:**
1. Verify `DATABASE_URL` format is correct
2. Check Supabase IP whitelist (should allow all for Render)
3. Test connection:
   ```bash
   psql $DATABASE_URL
   ```

### Webhook Failures

**Solution:**
1. Verify webhook secret is correct in both dashboard and Render env
2. Check logs: `Render Dashboard > Logs > filter for "webhook"`
3. Ensure endpoint is publicly accessible:
   ```bash
   curl https://your-app.onrender.com/checkout/payments/webhook/stripe/
   ```

### Images Not Displaying

**Solution:**
1. Check browser console for 404 errors
2. Verify `MEDIA_URL` and `MEDIA_ROOT` in settings
3. Check file permissions: `chmod 755 /var/media/`
4. Re-collect static files

## Monitoring

### Logs
- **Render**: Dashboard > Logs (real-time monitoring)
- **Local**: `logs/django.log` (after setup)
- **Payment events**: Logged separately under `payments` logger

### Performance
- **Render Metrics**: Dashboard > Metrics (CPU, Memory, Network)
- **Database**: Supabase Dashboard > Logs

### Health Checks
```bash
# Test API is running
curl https://your-app.onrender.com/
```

## Git Workflow for Production

### Before Pushing Changes

```bash
# 1. Test locally
python manage.py test

# 2. Check for issues
python manage.py check --deploy

# 3. Format code
black .
ruff check .

# 4. Create migration if needed
python manage.py makemigrations

# 5. Stage and commit
git add .
git commit -m "Description of changes"
```

### Pushing to Production

```bash
git push origin main
```

**Render automatically:**
1. Detects push to main branch
2. Runs build script: `bash build.sh`
3. Runs migrations
4. Collects static files
5. Restarts the web service

## Environment Variables Reference

| Variable | Example | Required | Notes |
|---|---|---|---|
| `SECRET_KEY` | `django-insecure-...` | Yes | Generate random string |
| `DEBUG` | `False` | Yes | Always `False` in production |
| `ALLOWED_HOSTS` | `app.onrender.com,yourdomain.com` | Yes | Comma-separated |
| `DATABASE_URL` | `postgresql://...` | Yes | Supabase connection string |
| `SECURE_SSL_REDIRECT` | `True` | No | Enable HTTPS redirect |
| `USE_S3_STORAGE` | `False` | No | Use S3 for images (optional) |
| `STRIPE_SECRET_KEY` | `sk_live_...` | Yes | From Stripe dashboard |
| `PAYPACK_CLIENT_ID` | `xxx` | No | Optional if not using MoMo |

## Security Checklist

- [ ] `SECRET_KEY` is unique and strong
- [ ] `DEBUG=False` in production
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] HTTPS enforced (`SECURE_SSL_REDIRECT=True`)
- [ ] Database backed up (Supabase automatic backups enabled)
- [ ] Webhook secrets configured
- [ ] Sensitive environment variables NOT in git
- [ ] `.env` in `.gitignore`
- [ ] Admin password strong (created via `createsuperuser`)
- [ ] Supabase IP whitelist configured

## Support & Documentation

- Django: https://docs.djangoproject.com
- Render: https://render.com/docs
- Supabase: https://supabase.com/docs
- Stripe: https://stripe.com/docs
- Paypack: https://developers.paypack.rw

## Next Steps

1. ✅ Deploy to Render
2. ✅ Configure webhooks
3. Upload first product with images
4. Test payment flow (use Stripe test mode)
5. Set up custom domain (Render > Custom Domain)
6. Enable HTTPS certificate (automatic)
7. Monitor logs and metrics

---

**You're all set!** Your WorldWide e-commerce platform is now live on Render with Supabase database and full image support.
