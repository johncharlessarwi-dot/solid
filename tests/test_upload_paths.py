import tempfile
import unittest
from pathlib import Path

from app.utils import resolve_upload_directory


class UploadPathTests(unittest.TestCase):
    def test_valid_nested_directory(self):
        with tempfile.TemporaryDirectory() as root:
            target = resolve_upload_directory(root, "orders/JOA-123")
            self.assertTrue(target.is_relative_to(Path(root).resolve()))
            self.assertEqual(target.name, "JOA-123")

    def test_rejects_traversal_absolute_and_empty_paths(self):
        with tempfile.TemporaryDirectory() as root:
            for folder in ("../outside", "", "/tmp", "orders/../../../outside"):
                with self.subTest(folder=folder), self.assertRaises(ValueError):
                    resolve_upload_directory(root, folder)

    def test_does_not_create_directories_during_validation(self):
        with tempfile.TemporaryDirectory() as root:
            path = resolve_upload_directory(root, "orders/123")
            self.assertFalse(path.exists())


class UploadPathRegression_10 (unittest.TestCase):
    def test_path(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(ValueError): resolve_upload_directory(root, 'orders/\x00evil')


class UploadPathRegression_11 (unittest.TestCase):
    def test_path(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(ValueError): resolve_upload_directory(root, 'orders/./123')


class UploadPathRegression_12 (unittest.TestCase):
    def test_path(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(ValueError): resolve_upload_directory(root, 'orders//123')
