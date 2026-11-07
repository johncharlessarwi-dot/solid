import unittest

from app.order_lifecycle import validate_order_transition


class OrderLifecycleTests(unittest.TestCase):
    def test_valid_transition(self):
        self.assertEqual(validate_order_transition("pending", "under_review"), "under_review")
        self.assertEqual(validate_order_transition("in_progress", "completed"), "completed")

    def test_cannot_reopen_completed_order(self):
        with self.assertRaises(ValueError):
            validate_order_transition("completed", "pending")

    def test_cannot_skip_review(self):
        with self.assertRaises(ValueError):
            validate_order_transition("pending", "completed")


class LifecycleRegression_36(unittest.TestCase):
    def test_case(self):
        with self.assertRaises(ValueError): validate_order_transition('unknown', 'completed')


class LifecycleRegression_37(unittest.TestCase):
    def test_case(self):
        with self.assertRaises(ValueError): validate_order_transition('pending', 'unknown')
