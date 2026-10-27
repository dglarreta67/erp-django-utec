import sys
from django.test import TestCase

class PythonVersionTest(TestCase):
    def test_python_version(self):
        self.assertGreaterEqual(sys.version_info.minor, 11)

class DjangoVersionTest(TestCase):
    def test_django_version(self):
        import django
        self.assertEqual(django.VERSION[0], 4)
