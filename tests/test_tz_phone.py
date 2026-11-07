import unittest

from app.tz_phone import normalize_tz_mobile


class TanzaniaMobileTests(unittest.TestCase):
    def test_supported_formats(self):
        for value in ("0698170989", "698170989", "255698170989", "+255 698 170 989"):
            with self.subTest(value=value):
                self.assertEqual(normalize_tz_mobile(value), "+255698170989")

    def test_rejects_invalid_or_foreign_numbers(self):
        for value in (None, "1234", "+254712345678", "0281234567", "0698170989x"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalize_tz_mobile(value)


class PhoneRegression_28(unittest.TestCase):
    def test_case(self):
        with self.assertRaises(ValueError): normalize_tz_mobile('069817A989')


class PhoneRegression_29(unittest.TestCase):
    def test_case(self):
        with self.assertRaises(ValueError): normalize_tz_mobile('0598170989')


class PhoneRegression_30(unittest.TestCase):
    def test_case(self):
        with self.assertRaises(ValueError): normalize_tz_mobile('06981709891')
