from django.test import TestCase
from django.urls import reverse

class LecturaVistasTest(TestCase):
    def test_lista_productos(self):
        r = self.client.get(reverse('productos:lista'))
        self.assertEqual(r.status_code, 200)
