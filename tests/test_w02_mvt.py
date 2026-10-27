from django.test import TestCase
from django.urls import reverse

class TemplatesRenderTest(TestCase):
    def test_bienvenida(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
