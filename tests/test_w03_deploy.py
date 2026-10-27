from django.test import TestCase

class DeployConfigTest(TestCase):
    def test_settings_prod(self):
        from core import settings_prod
        self.assertFalse(settings_prod.DEBUG)
