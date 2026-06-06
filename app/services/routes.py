from flask import Blueprint, render_template

from app.models import Category, Service

services_bp = Blueprint("services", __name__, url_prefix="/services")


@services_bp.route("/")
def index():
    categories = Category.query.order_by(Category.name).all()
    return render_template("services/index.html", categories=categories)


@services_bp.route("/<slug>")
def detail(slug):
    service = Service.query.filter_by(slug=slug, is_active=True).first_or_404()
    return render_template("services/detail.html", service=service)
