# WorldWide E-Commerce Platform

A modern, full-featured Django e-commerce platform with integrated payment systems for Rwanda (MTN MoMo, Airtel Money), international payments (Stripe), and secure authentication via Supabase.

## Quick Start

### Local Development

```bash
# 1. Clone and setup
git clone <repo-url>
cd worldwide/worldwide
python -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings (keep DEBUG=True for local dev)

# 4. Setup database and run
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Visit http://localhost:8000
```

### Production on Render

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete setup guide.

**Quick Summary:**
1. Push to GitHub
2. Connect repository to Render
3. Set environment variables
4. Deploy (Render auto-runs migrations)
5. Configure webhook endpoints in payment providers

## Features

- **Multi-Payment System**: MTN MoMo, Airtel Money, Stripe, Cash on Delivery
- **User Authentication**: Email/password + Supabase OAuth (Google/GitHub)
- **Product Management**: Categories, inventory, pricing
- **Order Processing**: Cart, checkout, order tracking
- **Admin Dashboard**: Full control over products, orders, payments
- **Responsive Design**: Mobile-optimized with TailwindCSS
- **Security**: HMAC webhook verification, SSL/TLS, CSRF protection

## Project Structure

```
worldwide/
├── manage.py
├── requirements.txt
├── Procfile              # For Render deployment
├── build.sh             # Build script
├── render.yaml          # Render configuration
├── .env.example         # Example environment variables
├── DEPLOYMENT.md        # Production deployment guide
├── accounts/            # User authentication
├── cart/                # Shopping cart
├── core/                # Core site settings
├── orders/              # Order management
├── payments/            # Payment processing
├── products/            # Product catalog
├── reviews/             # Product reviews
├── shipping/            # Shipping management
├── wishlist/            # User wishlists
├── search/              # Product search
├── static/              # Static files (CSS, JS, images)
├── templates/           # HTML templates
└── worldwide/           # Django settings
```

## Environment Variables

See `.env.example` for complete list. Key variables:

```bash
# Development
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Production
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (Supabase PostgreSQL)
DATABASE_URL=postgresql://user:pass@host:5432/db

# Payments
STRIPE_PUBLISHABLE_KEY=pk_xxx
STRIPE_SECRET_KEY=sk_xxx
PAYPACK_CLIENT_ID=xxx
PAYPACK_CLIENT_SECRET=xxx

# Security
SECURE_SSL_REDIRECT=True
CSRF_COOKIE_SECURE=True
```

## Payment Integration

### Paypack (Rwanda - MTN MoMo & Airtel Money)
- **Mobile popup**: Auto-polls status every 3 seconds
- **Webhook verification**: HMAC-SHA256 signature
- **Status API**: `/payments/api/check-status/<order_number>/`

### Stripe (International)
- **Payment Intent**: Secure client-side tokenization
- **Webhook**: Validates `payment_intent.succeeded` events

### Cash on Delivery
- No payment required upfront
- Mark as paid on delivery

## Security Features

✅ **Webhook Verification**
- HMAC-SHA256 signature validation
- Prevents replay attacks
- Logs all webhook attempts

✅ **HTTPS/SSL**
- Enforced in production
- HSTS headers enabled
- Secure cookies (CSRF, Session)

✅ **Database Security**
- Uses Supabase PostgreSQL
- Connection pooling support
- Encrypted credentials

✅ **API Security**
- CSRF protection
- X-Frame-Options: DENY
- Content Security Policy headers
- User authentication required for sensitive endpoints

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for:
- Step-by-step Render setup
- GitHub integration
- Supabase database configuration
- Webhook endpoint setup
- Production environment variables
- Troubleshooting guide

## Testing

```bash
# Run tests
pytest

# Generate coverage report
pytest --cov

# Check code quality
black --check .
ruff check .
```

## Logging

- **Console**: INFO level logs printed to terminal
- **File**: WARNING+ logs saved to `logs/django.log`
- **Payments**: All payment events logged separately

Access logs in Render:
```
Dashboard > Logs > scroll to find entries
```

## Static & Media Files

- **Static Files**: Served via WhiteNoise (no external storage needed)
- **Media Files**: Stored in `media/` directory
- **Images**: Product images in `media/products/`
- **To use S3**: Install `django-storages` and configure

## Common Tasks

### Create admin user
```bash
python manage.py createsuperuser
```

### Run migrations
```bash
python manage.py migrate
```

### Collect static files
```bash
python manage.py collectstatic --noinput
```

### Create seed data
```bash
python manage.py seed_data
```

### Check for issues
```bash
python manage.py check --deploy
```

## Support & Documentation

- Django: https://docs.djangoproject.com
- Render: https://render.com/docs
- Supabase: https://supabase.com/docs
- Stripe: https://stripe.com/docs
- Paypack: https://developers.paypack.rw

## License

Proprietary - All rights reserved

---

**Ready to deploy?** Follow [DEPLOYMENT.md](DEPLOYMENT.md) for production setup!
