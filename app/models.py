from datetime import datetime, timezone
from uuid import uuid4

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class User(UserMixin, TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(40))
    role = db.Column(db.String(40), default="customer", nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    orders = db.relationship(
        "Order",
        foreign_keys="Order.customer_id",
        back_populates="customer",
        lazy="dynamic",
    )
    notifications = db.relationship("Notification", back_populates="user", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, *roles):
        return self.role in roles


class Category(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    slug = db.Column(db.String(140), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    services = db.relationship("Service", back_populates="category", lazy="dynamic")


class Service(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    name = db.Column(db.String(160), nullable=False)
    slug = db.Column(db.String(180), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    category = db.relationship("Category", back_populates="services")
    orders = db.relationship("Order", back_populates="service", lazy="dynamic")


class Order(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(40), unique=True, nullable=False, default=lambda: f"JOA-{uuid4().hex[:10].upper()}")
    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey("service.id"), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    status = db.Column(db.String(40), default="pending", nullable=False, index=True)
    notes = db.Column(db.Text)
    admin_notes = db.Column(db.Text)
    amount = db.Column(db.Integer, nullable=False, default=0)

    customer = db.relationship("User", foreign_keys=[customer_id], back_populates="orders")
    assigned_to = db.relationship("User", foreign_keys=[assigned_to_id])
    service = db.relationship("Service", back_populates="orders")
    payments = db.relationship("Payment", back_populates="order", lazy="dynamic")
    files = db.relationship("FileAsset", back_populates="order", lazy="dynamic", cascade="all, delete-orphan")


class Payment(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"))
    transaction_reference = db.Column(db.String(120), unique=True, nullable=False, default=lambda: uuid4().hex)
    provider = db.Column(db.String(40), default="stripe", nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(8), default="TZS", nullable=False)
    buyer_phone = db.Column(db.String(40))
    buyer_name = db.Column(db.String(120))
    status = db.Column(db.String(40), default="pending", nullable=False, index=True)
    raw_payload = db.Column(db.JSON)

    order = db.relationship("Order", back_populates="payments")


class FileAsset(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)
    purpose = db.Column(db.String(40), default="customer_document", nullable=False)

    order = db.relationship("Order", back_populates="files")
    uploaded_by = db.relationship("User")


class Notification(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(160), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)

    user = db.relationship("User", back_populates="notifications")


class AuditLog(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    action = db.Column(db.String(160), nullable=False)
    entity_type = db.Column(db.String(80))
    entity_id = db.Column(db.Integer)
    meta = db.Column("metadata", db.JSON)

    actor = db.relationship("User")
