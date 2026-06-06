import stripe
from flask import Blueprint, abort, current_app, jsonify, request, url_for
from flask_login import current_user, login_required

from app.extensions import csrf, db
from app.models import Notification, Order, Payment

payments_bp = Blueprint("payments", __name__)


@payments_bp.route("/orders/<order_number>/stripe-checkout", methods=["POST"])
@login_required
def stripe_checkout(order_number):
    order = Order.query.filter_by(order_number=order_number, customer_id=current_user.id).first_or_404()
    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]
    if not stripe.api_key:
        return jsonify({"error": "Stripe is not configured."}), 503

    minimum_amount = current_app.config["STRIPE_MIN_TZS"]
    if order.amount < minimum_amount:
        return (
            jsonify(
                {
                    "error": f"This order is TZS {order.amount:,}. Stripe checkout requires at least TZS {minimum_amount:,}. Please increase the service price or contact support.",
                }
            ),
            400,
        )

    try:
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
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    payment = Payment(order=order, provider="stripe", amount=order.amount, transaction_reference=session.id, status="pending")
    db.session.add(payment)
    db.session.commit()
    return jsonify({"checkout_url": session.url})


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
