from flask import Blueprint, render_template

from app.models import Category, Service

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    categories = Category.query.order_by(Category.name).all()
    featured_services = Service.query.filter_by(is_active=True).limit(8).all()
    return render_template("main/home.html", categories=categories, featured_services=featured_services)


@main_bp.route("/about")
def about():
    return render_template("main/static_page.html", title="About", page="about")


@main_bp.route("/pricing")
def pricing():
    services = Service.query.filter_by(is_active=True).order_by(Service.price).all()
    return render_template("main/pricing.html", services=services)


@main_bp.route("/contact")
def contact():
    return render_template("main/static_page.html", title="Contact", page="contact")


@main_bp.route("/blog")
def blog():
    return render_template("main/static_page.html", title="Blog", page="blog")


@main_bp.route("/faq")
def faq():
    return render_template("main/static_page.html", title="FAQ", page="faq")


@main_bp.route("/terms")
def terms():
    return render_template("main/static_page.html", title="Terms", page="terms")


@main_bp.route("/privacy-policy")
def privacy():
    return render_template("main/static_page.html", title="Privacy Policy", page="privacy")
