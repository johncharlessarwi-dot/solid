# JOHN ONLINE SERVICES & APPLICATIONS

A production-minded Flask digital service marketplace where customers request services, upload documents, pay online, track progress, and download completed work.

## Stack

- Python 3.12+
- Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-Login, Flask-WTF
- SQLite for development
- Jinja2 templates
- Tailwind CSS via CDN for fast setup
- Alpine.js
- Stripe checkout and webhook support
- Local secure file storage

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
flask db init
flask db migrate -m "Initial schema"
flask db upgrade
flask seed-data
flask create-admin --name "Super Admin" --email admin@example.com --password "Admin@12345"
flask run
```

Open `http://localhost:5000`.

## Default Roles

- `super_admin`
- `admin`
- `service_officer`
- `accountant`
- `customer`

## Stripe Payment Routes

- `POST /orders/<order_number>/stripe-checkout`
- `POST /stripe/webhook`

Stripe enforces a minimum charge amount. For TZS payments this app blocks checkout below `STRIPE_MIN_TZS`, defaulting to `1500`, and shows a friendly message instead of raising a server error.

## Notes For Production

- Use a strong `SECRET_KEY`.
- Move uploads to private object storage when scaling beyond one server.
- Configure HTTPS and secure cookies at the reverse proxy/application layer.
- Replace Tailwind CDN with a compiled Tailwind build for strict production CSP.
- Keep Stripe webhook signing enabled.
