from uuid import uuid4

import stripe
from flask import Blueprint, abort, current_app, jsonify, request, url_for
from flask_login import current_user, login_required

from app.extensions import csrf, db
from app.models import Notification, Order, Payment
from app.utils import verify_hmac_signature

payments_bp = Blueprint("payments", __name__)


def require_api_key():
    expected = current_app.config["PETERPAY_API_KEY"]
    if not expected or request.headers.get("X-API-KEY") != expected:
        abort(401)


@payments_bp.route("/orders/<order_number>/stripe-checkout", methods=["POST"])
@login_required
def stripe_checkout(order_number):
    order = Order.query.filter_by(order_number=order_number, customer_id=current_user.id).first_or_404()
    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]
    if not stripe.api_key:
        abort(503, "Stripe is not configured.")
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": "tzs",
                    "unit_amount": order.amount,
                    "product_data": {"name": order.service.name},
                },
                "quantity": 1,
            }
        ],
        metadata={"order_id": order.id, "order_number": order.order_number},
        success_url=current_app.config["BASE_URL"] + url_for("orders.detail", order_number=order.order_number),
        cancel_url=current_app.config["BASE_URL"] + url_for("orders.detail", order_number=order.order_number),
    )
    payment = Payment(order=order, provider="stripe", amount=order.amount, transaction_reference=session.id, status="pending")
    db.session.add(payment)
    db.session.commit()
    return jsonify({"checkout_url": session.url})


@payments_bp.route("/payments/create", methods=["POST"])
@csrf.exempt
def create_payment():
    require_api_key()
    payload = request.get_json(silent=True) or {}
    amount = int(payload.get("amount") or 0)
    if amount <= 0:
        abort(400, "Amount must be greater than zero.")
    payment = Payment(
        amount=amount,
        buyer_phone=payload.get("buyer_phone"),
        buyer_name=payload.get("buyer_name"),
        provider="peterpay",
        transaction_reference=f"PP-{uuid4().hex[:14].upper()}",
        raw_payload=payload,
    )
    db.session.add(payment)
    db.session.commit()
    return jsonify({"transaction_reference": payment.transaction_reference, "amount": payment.amount, "payment_status": payment.status})


@payments_bp.route("/payments/status", methods=["POST"])
@csrf.exempt
def payment_status():
    require_api_key()
    payload = request.get_json(silent=True) or {}
    payment = Payment.query.filter_by(transaction_reference=payload.get("transaction_reference")).first_or_404()
    return jsonify({"order_id": payment.order_id, "transaction_reference": payment.transaction_reference, "amount": payment.amount, "payment_status": payment.status})


@payments_bp.route("/payments/webhook", methods=["POST"])
@csrf.exempt
def peterpay_webhook():
    return order_status()


@payments_bp.route("/order_status", methods=["POST"])
@csrf.exempt
def order_status():
    raw = request.get_data()
    signature = request.headers.get("X-PETERPAY-SIGNATURE")
    if not verify_hmac_signature(raw, signature, current_app.config["PETERPAY_WEBHOOK_SECRET"]):
        abort(401)
    payload = request.get_json(silent=True) or {}
    reference = payload.get("transaction_reference")
    payment = Payment.query.filter_by(transaction_reference=reference).first_or_404()
    payment.status = payload.get("payment_status", payment.status)
    payment.raw_payload = payload
    if payment.order and payment.status in {"paid", "success", "completed"}:
        payment.order.status = "under_review"
        db.session.add(Notification(user=payment.order.customer, title="Payment received", message=f"Order {payment.order.order_number} is now under review."))
    db.session.commit()
    return jsonify({"ok": True})


@payments_bp.route("/stripe/webhook", methods=["POST"])
@csrf.exempt
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")
    secret = current_app.config["STRIPE_WEBHOOK_SECRET"]
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, secret)
    except Exception:
        abort(400)
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        payment = Payment.query.filter_by(transaction_reference=session["id"]).first()
        if payment:
            payment.status = "paid"
            if payment.order:
                payment.order.status = "under_review"
                db.session.add(Notification(user=payment.order.customer, title="Payment received", message=f"Order {payment.order.order_number} is now under review."))
            db.session.commit()
    return jsonify({"received": True})
