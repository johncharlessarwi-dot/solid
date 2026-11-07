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


class LifecycleRegression_38(unittest.TestCase):
    def test_case(self):
        with self.assertRaises(ValueError): validate_order_transition('pending', 'in_progress')


class LifecycleRegression_39(unittest.TestCase):
    def test_case(self):
        with self.assertRaises(ValueError): validate_order_transition('pending', 'pending')


class LifecycleRegression_40(unittest.TestCase):
    def test_case(self):
        with self.assertRaises(ValueError): validate_order_transition('rejected', 'under_review')


class LifecycleRegression_41(unittest.TestCase):
    def test_case(self):
        self.assertEqual(validate_order_transition('waiting_documents', 'under_review'), 'under_review')


class LifecycleRegression_42(unittest.TestCase):
    def test_case(self):
        self.assertEqual(validate_order_transition('in_progress', 'waiting_documents'), 'waiting_documents')
