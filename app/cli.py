import click
from werkzeug.utils import secure_filename

from .extensions import db
from .models import Category, Service, User


SEED_DATA = {
    "Student Services": [
        ("TCU Applications", 30000),
        ("HESLB Applications", 25000),
        ("Scholarship Applications", 35000),
        ("CV Writing", 20000),
        ("Research Proposal Writing", 80000),
        ("Career Guidance", 15000),
    ],
    "Business Services": [
        ("TRA Services", 40000),
        ("BRELA Services", 50000),
        ("Business Registration", 100000),
        ("Tax Assistance", 60000),
        ("Business Plans", 150000),
    ],
    "IT Services": [
        ("Website Development", 500000),
        ("Mobile Apps", 1200000),
        ("Graphic Design", 70000),
        ("Logo Design", 50000),
        ("Cyber Security", 250000),
        ("Hosting Setup", 80000),
    ],
    "Tourism Services": [
        ("Kilimanjaro Booking", 200000),
        ("Safari Booking", 250000),
        ("Hotel Reservations", 40000),
        ("Visa Assistance", 120000),
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
            for service_name, price in services:
                if not Service.query.filter_by(name=service_name).first():
                    db.session.add(
                        Service(
                            category=category,
                            name=service_name,
                            slug=slugify(service_name),
                            description=f"Request expert help for {service_name.lower()} with secure document handling.",
                            price=price,
                        )
                    )
        db.session.commit()
        click.echo("Seeded categories and services.")

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
