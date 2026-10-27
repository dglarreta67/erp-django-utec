from django.test import TestCase
from django.urls import reverse

class EscrituraVistasTest(TestCase):
    def test_crear_sin_auth_redirige(self):
        r = self.client.get(reverse('productos:crear'))
        self.assertEqual(r.status_code, 302)
