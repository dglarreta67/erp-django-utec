from decimal import Decimal
from django.core.exceptions import ValidationError
from django.test import TestCase
from productos.models import Categoria, Producto

class ValidadoresTest(TestCase):
    def test_precio_negativo(self):
        cat = Categoria.objects.create(nombre='Cat')
        p = Producto(nombre='Prod', precio=Decimal('-10.00'), stock=1, categoria=cat)
        with self.assertRaises(ValidationError):
            p.full_clean()
