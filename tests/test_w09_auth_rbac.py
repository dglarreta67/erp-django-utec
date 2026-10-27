from decimal import Decimal
from django.contrib.auth.models import Group, Permission, User
from django.test import TestCase
from django.urls import reverse
from productos.models import Categoria, Producto

class AuthRBACTest(TestCase):
    def test_login_page_200(self):
        r = self.client.get(reverse('account_login'))
        self.assertEqual(r.status_code, 200)

    def test_management_command_crea_grupos(self):
        from django.core.management import call_command
        call_command('crear_grupos')
        for g in ['Gerente', 'Vendedor', 'Almacén']:
            self.assertTrue(Group.objects.filter(name=g).exists())
