from decimal import Decimal
from django.test import TestCase
from clientes.models import Cliente
from productos.models import Categoria, Producto

class ModelosBaseTest(TestCase):
    def test_crear_cliente(self):
        c = Cliente.objects.create(nombre='Test', correo='test@example.com')
        self.assertEqual(c.nombre, 'Test')
