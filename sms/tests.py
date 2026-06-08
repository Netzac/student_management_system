from django.test import TestCase

from sms.services import normalize_phone


class NormalizePhoneTests(TestCase):
    def test_e164_passthrough(self):
        self.assertEqual(normalize_phone("+233241234567"), "+233241234567")

    def test_local_format(self):
        self.assertEqual(normalize_phone("0241234567", "233"), "+233241234567")

    def test_invalid_returns_none(self):
        self.assertIsNone(normalize_phone("abc"))
