import unittest
from types import SimpleNamespace
from unittest.mock import patch

import stripe
from flask import Flask
from flask_login import LoginManager

from app.payments import routes


class CheckoutErrorTests(unittest.TestCase):
    def test_provider_error_is_redacted_and_no_payment_is_created(self):
        app = Flask(__name__)
        app.config.update(LOGIN_DISABLED=True, STRIPE_SECRET_KEY="unit-test-only",
                          STRIPE_MIN_USD=100, BASE_URL="https://example.test")
        LoginManager(app)
        app.register_blueprint(routes.payments_bp)
        app.add_url_rule("/orders/<order_number>", "orders.detail", lambda order_number: "")
        order = SimpleNamespace(id=1, order_number="TEST", amount=1000,
                                service=SimpleNamespace(name="Printing"))
        marker = "SENSITIVE_PROVIDER_DETAIL"
        with (
            patch.object(routes, "current_user", SimpleNamespace(id=1)),
            patch.object(routes, "Order") as orders,
            patch.object(routes, "db") as database,
            patch.object(stripe, "api_key"),
            patch.object(stripe.checkout.Session, "create", side_effect=stripe.StripeError(marker)),
            self.assertLogs(app.logger, level="WARNING") as logs,
        ):
            orders.query.filter_by.return_value.first_or_404.return_value = order
            response = app.test_client().post("/orders/TEST/stripe-checkout")
        self.assertEqual(response.status_code, 502)
        self.assertNotIn(marker, response.get_data(as_text=True))
        self.assertNotIn(marker, "\n".join(logs.output))
        database.session.add.assert_not_called()
        database.session.commit.assert_not_called()
