import click
from werkzeug.utils import secure_filename

from .extensions import db
from .models import Category, Service, User


# All prices are in USD cents (e.g. 1200 = $12.00) for Stripe compatibility.
# Converted from original TZS prices at ~2600 TZS/USD, rounded to clean amounts.
SEED_DATA = {
    "Student Services": [
        ("TCU Applications",          1200),   # $12.00
        ("HESLB Applications",        1000),   # $10.00
        ("Scholarship Applications",  1400),   # $14.00
        ("CV Writing",                 800),   #  $8.00
        ("Research Proposal Writing", 3000),   # $30.00
        ("Career Guidance",            600),   #  $6.00
    ],
    "Business Services": [
        ("TRA Services",              1500),   # $15.00
        ("BRELA Services",            2000),   # $20.00
        ("Business Registration",     3900),   # $39.00
        ("Tax Assistance",            2300),   # $23.00
        ("Business Plans",            5800),   # $58.00
    ],
    "IT Services": [
        ("Website Development",      19200),   # $192.00
        ("Mobile Apps",              46100),   # $461.00
        ("Graphic Design",            2700),   # $27.00
        ("Logo Design",               1900),   # $19.00
        ("Cyber Security",            9600),   # $96.00
        ("Hosting Setup",             3100),   # $31.00
    ],
    "Tourism Services": [
        ("Kilimanjaro Booking",       7700),   # $77.00
        ("Safari Booking",            9600),   # $96.00
        ("Hotel Reservations",        1500),   # $15.00
        ("Visa Assistance",           4600),   # $46.00
    ],
}


def slugify(value):
    return secure_filename(value.lower().replace(" ", "-")).replace("_", "-")


def register_cli(app):
    @app.cli.command("seed-data")
    def seed_data():
        for category_name, services in SEED_DATA.items():
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                category = Category(
                    name=category_name,
                    slug=slugify(category_name),
                    description=f"Professional {category_name.lower()} for customers across Tanzania.",
                )
                db.session.add(category)
                db.session.flush()
            for service_name, price_cents in services:
                existing = Service.query.filter_by(name=service_name).first()
                if not existing:
                    db.session.add(
                        Service(
                            category=category,
                            name=service_name,
                            slug=slugify(service_name),
                            description=f"Request expert help for {service_name.lower()} with secure document handling.",
                            price=price_cents,
                        )
                    )
                else:
                    # Update existing prices to USD cents on re-seed
                    existing.price = price_cents
        db.session.commit()
        click.echo("Seeded categories and services (prices in USD cents).")

    @app.cli.command("migrate-prices-to-usd")
    def migrate_prices_to_usd():
        """One-time migration: convert existing TZS prices to USD cents."""
        TZS_TO_USD = 2600.0  # exchange rate used for conversion
        services = Service.query.all()
        if not services:
            click.echo("No services found.")
            return
        for service in services:
            usd_dollars = service.price / TZS_TO_USD
            # Round to nearest $0.50 increment, stored as cents
            service.price = round(usd_dollars * 2) * 50  # nearest 50 cents
        db.session.commit()
        click.echo(f"Migrated {len(services)} service prices from TZS to USD cents.")

    @app.cli.command("create-admin")
    @click.option("--name", required=True)
    @click.option("--email", required=True)
    @click.option("--password", required=True)
    def create_admin(name, email, password):
        user = User.query.filter_by(email=email.lower()).first()
        if not user:
            user = User(name=name, email=email.lower(), role="super_admin")
            db.session.add(user)
        user.name = name
        user.role = "super_admin"
        user.set_password(password)
        db.session.commit()
        click.echo(f"Super admin ready: {email}")
