import unittest

from app.quote_math import calculate_quote_total


class QuoteMathTests(unittest.TestCase):
    def test_valid_quote(self):
        result = calculate_quote_total([{"unit_price": 5000, "quantity": 2}], discount=1000)
        self.assertEqual(result, {"subtotal": 10000, "discount": 1000, "total": 9000})

    def test_rejects_invalid_values(self):
        for items, discount in [
            ([{"unit_price": 1.5, "quantity": 1}], 0),
            ([{"unit_price": 2, "quantity": True}], 0),
            ([{"unit_price": 100, "quantity": 1}], 101),
            ([{"unit_price": 100000000, "quantity": 2}], 0),
        ]:
            with self.subTest(items=items), self.assertRaises(ValueError):
                calculate_quote_total(items, discount)


class QuoteRegression_18(unittest.TestCase):
    def test_case(self):
        with self.assertRaises(ValueError): calculate_quote_total([{'unit_price': 10}])


class QuoteRegression_19(unittest.TestCase):
    def test_case(self):
        with self.assertRaises(ValueError): calculate_quote_total([{'quantity': 1}])
