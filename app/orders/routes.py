from flask import Blueprint, abort, current_app, flash, redirect, render_template, send_file, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import FileAsset, Order, Service
from app.utils import save_upload
from .forms import OrderForm

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")


@orders_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    form = OrderForm()
    services = Service.query.filter_by(is_active=True).order_by(Service.name).all()
    form.service_id.choices = [(service.id, f"{service.name} - ${service.price / 100:.2f} USD") for service in services]
    if form.validate_on_submit():
        service = Service.query.get_or_404(form.service_id.data)
        order = Order(customer=current_user, service=service, amount=service.price, notes=form.notes.data)
        db.session.add(order)
        db.session.flush()
        for upload in form.documents.data or []:
            if upload and upload.filename:
                original, stored, path, extension = save_upload(upload, f"orders/{order.order_number}")
                db.session.add(
                    FileAsset(
                        order=order,
                        uploaded_by=current_user,
                        original_filename=original,
                        stored_filename=stored,
                        file_path=path,
                        file_type=extension,
                        purpose="customer_document",
                    )
                )
        db.session.commit()
        flash("Order submitted. You can now pay online.", "success")
        return redirect(url_for("orders.detail", order_number=order.order_number))
    return render_template("orders/create.html", form=form)


@orders_bp.route("/<order_number>")
@login_required
def detail(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    if order.customer_id != current_user.id and not current_user.has_role("super_admin", "admin", "service_officer", "accountant"):
        abort(403)
    return render_template("orders/detail.html", order=order, stripe_public_key=current_app.config["STRIPE_PUBLIC_KEY"])


@orders_bp.route("/files/<int:file_id>/download")
@login_required
def download_file(file_id):
    file_asset = FileAsset.query.get_or_404(file_id)
    order = file_asset.order
    allowed = order.customer_id == current_user.id or current_user.has_role("super_admin", "admin", "service_officer", "accountant")
    if not allowed:
        abort(403)
    return send_file(file_asset.file_path, as_attachment=True, download_name=file_asset.original_filename)
