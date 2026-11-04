import unittest

from app.utils import verify_hmac_signature


class ExistingSecurityTests(unittest.TestCase):
    def test_valid_hmac_is_accepted(self):
        import hashlib
        import hmac
        body = b'{"reference":"ABC"}'
        digest = hmac.new(b"test-secret", body, hashlib.sha256).hexdigest()
        self.assertTrue(verify_hmac_signature(body, digest, "test-secret"))

    def test_invalid_and_missing_signatures_are_rejected(self):
        self.assertFalse(verify_hmac_signature(b"body", "bad", "test-secret"))
        self.assertFalse(verify_hmac_signature(b"body", "", "test-secret"))
        self.assertFalse(verify_hmac_signature(b"body", "anything", ""))
