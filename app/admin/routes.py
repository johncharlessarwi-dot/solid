from sqlalchemy import func
from werkzeug.utils import secure_filename

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user

from app.decorators import roles_required
from app.extensions import db
from app.models import Category, FileAsset, Order, Payment, Service, User
from app.utils import save_upload
from .forms import CategoryForm, OrderStatusForm, ServiceForm, UserRoleForm

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def slugify(value):
    return secure_filename(value.lower().replace(" ", "-")).replace("_", "-")


@admin_bp.route("/")
@roles_required("super_admin", "admin", "service_officer", "accountant")
def index():
    stats = {
        "total_users": User.query.count(),
        "total_orders": Order.query.count(),
        "total_revenue": db.session.query(func.coalesce(func.sum(Payment.amount), 0)).filter(Payment.status.in_(["paid", "success", "completed"])).scalar(),
        "pending_orders": Order.query.filter_by(status="pending").count(),
        "completed_orders": Order.query.filter_by(status="completed").count(),
    }
    latest_orders = Order.query.order_by(Order.created_at.desc()).limit(8).all()
    return render_template("admin/index.html", stats=stats, latest_orders=latest_orders)


@admin_bp.route("/users")
@roles_required("super_admin", "admin")
def users():
    return render_template("admin/users.html", users=User.query.order_by(User.created_at.desc()).all())


@admin_bp.route("/users/<int:user_id>", methods=["GET", "POST"])
@roles_required("super_admin", "admin")
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserRoleForm(obj=user)
    if form.validate_on_submit():
        user.role = form.role.data
        user.is_active = form.is_active.data
        db.session.commit()
        flash("User updated.", "success")
        return redirect(url_for("admin.users"))
    return render_template("admin/edit_user.html", form=form, user=user)


@admin_bp.route("/categories/new", methods=["GET", "POST"])
@roles_required("super_admin", "admin")
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        db.session.add(Category(name=form.name.data, slug=slugify(form.name.data), description=form.description.data))
        db.session.commit()
        flash("Category created.", "success")
        return redirect(url_for("admin.services"))
    return render_template("admin/category_form.html", form=form)


@admin_bp.route("/services")
@roles_required("super_admin", "admin", "service_officer")
def services():
    return render_template("admin/services.html", categories=Category.query.order_by(Category.name).all(), services=Service.query.order_by(Service.name).all())


@admin_bp.route("/services/new", methods=["GET", "POST"])
@roles_required("super_admin", "admin")
def new_service():
    form = ServiceForm()
    form.category_id.choices = [(category.id, category.name) for category in Category.query.order_by(Category.name).all()]
    form.is_active.data = True if form.is_active.data is None else form.is_active.data
    if form.validate_on_submit():
        db.session.add(
            Service(
                category_id=form.category_id.data,
                name=form.name.data,
                slug=slugify(form.name.data),
                description=form.description.data,
                price=form.price.data,
                is_active=form.is_active.data,
            )
        )
        db.session.commit()
        flash("Service created.", "success")
        return redirect(url_for("admin.services"))
    return render_template("admin/service_form.html", form=form)


@admin_bp.route("/orders")
@roles_required("super_admin", "admin", "service_officer", "accountant")
def orders():
    return render_template("admin/orders.html", orders=Order.query.order_by(Order.created_at.desc()).all())


@admin_bp.route("/orders/<order_number>", methods=["GET", "POST"])
@roles_required("super_admin", "admin", "service_officer")
def edit_order(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    form = OrderStatusForm(obj=order)
    if form.validate_on_submit():
        order.status = form.status.data
        order.admin_notes = form.admin_notes.data
        upload = form.result_file.data
        if upload and upload.filename:
            original, stored, path, extension = save_upload(upload, f"orders/{order.order_number}/results")
            db.session.add(
                FileAsset(
                    order=order,
                    uploaded_by=current_user,
                    original_filename=original,
                    stored_filename=stored,
                    file_path=path,
                    file_type=extension,
                    purpose="completed_work",
                )
            )
        db.session.commit()
        flash("Order updated.", "success")
        return redirect(url_for("admin.orders"))
    return render_template("admin/edit_order.html", order=order, form=form)


@admin_bp.route("/payments")
@roles_required("super_admin", "admin", "accountant")
def payments():
    payments = Payment.query.order_by(Payment.created_at.desc()).all()
    daily_income = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).filter(Payment.status.in_(["paid", "success", "completed"])).scalar()
    return render_template("admin/payments.html", payments=payments, daily_income=daily_income)


@admin_bp.route("/files")
@roles_required("super_admin", "admin", "service_officer")
def files():
    return render_template("admin/files.html", files=FileAsset.query.order_by(FileAsset.created_at.desc()).all())
