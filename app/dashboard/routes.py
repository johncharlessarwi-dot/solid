from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app.models import FileAsset, Notification, Order, Payment

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
@login_required
def index():
    if current_user.has_role("super_admin", "admin", "service_officer", "accountant"):
        return render_template("dashboard/staff.html")
    orders = Order.query.filter_by(customer_id=current_user.id).order_by(Order.created_at.desc()).all()
    payments = Payment.query.join(Order).filter(Order.customer_id == current_user.id).order_by(Payment.created_at.desc()).all()
    files = FileAsset.query.join(Order).filter(Order.customer_id == current_user.id).order_by(FileAsset.created_at.desc()).all()
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(10).all()
    return render_template("dashboard/customer.html", orders=orders, payments=payments, files=files, notifications=notifications)
