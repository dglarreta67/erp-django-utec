from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from clientes.models import Cliente


class ClienteTest(TestCase):

    def _cliente(self, **kwargs):
        datos = {'nombre': 'Ana Pérez', 'correo': 'ana@example.com'}
        datos.update(kwargs)
        return Cliente(**datos)

    # --- Valores por defecto y campos automáticos ---

    def test_telefono_es_opcional(self):
        c = self._cliente()
        c.full_clean()  # no debe lanzar error
        self.assertEqual(c.telefono, '')

    def test_activo_por_defecto_es_true(self):
        c = Cliente.objects.create(nombre='Ana', correo='a1@example.com')
        self.assertTrue(c.activo)

    def test_creado_se_asigna_automaticamente(self):
        c = Cliente.objects.create(nombre='Ana', correo='a2@example.com')
        self.assertIsNotNone(c.creado)

    def test_desactivar_cliente_persiste(self):
        c = Cliente.objects.create(nombre='Ana', correo='a3@example.com')
        c.activo = False
        c.save()
        c.refresh_from_db()
        self.assertFalse(c.activo)

    # --- __str__ y ordenamiento ---

    def test_str_devuelve_el_nombre(self):
        c = Cliente.objects.create(nombre='Luis Gómez', correo='luis@example.com')
        self.assertEqual(str(c), 'Luis Gómez')

    def test_ordering_por_nombre(self):
        Cliente.objects.create(nombre='Zoe', correo='zoe@example.com')
        Cliente.objects.create(nombre='Abel', correo='abel@example.com')
        nombres = list(Cliente.objects.values_list('nombre', flat=True))
        self.assertEqual(nombres, ['Abel', 'Zoe'])

    def test_dos_clientes_pueden_tener_el_mismo_nombre(self):
        Cliente.objects.create(nombre='Ana', correo='ana1@example.com')
        Cliente.objects.create(nombre='Ana', correo='ana2@example.com')
        self.assertEqual(Cliente.objects.filter(nombre='Ana').count(), 2)

    # --- Unicidad del correo ---

    def test_correo_es_unico(self):
        Cliente.objects.create(nombre='Ana', correo='repetido@example.com')
        with self.assertRaises(IntegrityError), transaction.atomic():
            Cliente.objects.create(nombre='Otra', correo='repetido@example.com')

    # --- Validaciones de full_clean ---

    def test_correo_valido_pasa_full_clean(self):
        c = self._cliente(correo='valido@example.com')
        c.full_clean()  # no debe lanzar error

    def test_correo_con_formato_invalido_se_rechaza(self):
        c = self._cliente(correo='no-es-correo')
        with self.assertRaises(ValidationError) as cm:
            c.full_clean()
        self.assertIn('correo', cm.exception.message_dict)

    def test_correo_vacio_se_rechaza(self):
        c = self._cliente(correo='')
        with self.assertRaises(ValidationError) as cm:
            c.full_clean()
        self.assertIn('correo', cm.exception.message_dict)

    def test_nombre_vacio_se_rechaza(self):
        c = self._cliente(nombre='')
        with self.assertRaises(ValidationError) as cm:
            c.full_clean()
        self.assertIn('nombre', cm.exception.message_dict)

    def test_nombre_de_151_caracteres_se_rechaza(self):
        c = self._cliente(nombre='a' * 151)
        with self.assertRaises(ValidationError) as cm:
            c.full_clean()
        self.assertIn('nombre', cm.exception.message_dict)

    def test_nombre_de_150_caracteres_se_acepta(self):
        c = self._cliente(nombre='a' * 150)
        c.full_clean()  # no debe lanzar error

    def test_telefono_de_21_caracteres_se_rechaza(self):
        c = self._cliente(telefono='1' * 21)
        with self.assertRaises(ValidationError) as cm:
            c.full_clean()
        self.assertIn('telefono', cm.exception.message_dict)