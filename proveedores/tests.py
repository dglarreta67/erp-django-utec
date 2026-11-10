from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from productos.models import Categoria, Producto
from proveedores.models import Proveedor


class ProveedorTest(TestCase):

    def _proveedor(self, **kwargs):
        datos = {'nombre': 'Distribuidora Norte', 'correo': 'norte@example.com'}
        datos.update(kwargs)
        return Proveedor(**datos)

    # --- Valores por defecto y campos automáticos ---

    def test_contacto_es_opcional(self):
        p = self._proveedor()
        p.full_clean()  # no debe lanzar error
        self.assertEqual(p.contacto, '')

    def test_telefono_es_opcional(self):
        p = self._proveedor()
        p.full_clean()
        self.assertEqual(p.telefono, '')

    def test_activo_por_defecto_es_true(self):
        p = Proveedor.objects.create(nombre='Norte', correo='p1@example.com')
        self.assertTrue(p.activo)

    def test_creado_se_asigna_automaticamente(self):
        p = Proveedor.objects.create(nombre='Norte', correo='p2@example.com')
        self.assertIsNotNone(p.creado)

    def test_desactivar_proveedor_persiste(self):
        p = Proveedor.objects.create(nombre='Norte', correo='p3@example.com')
        p.activo = False
        p.save()
        p.refresh_from_db()
        self.assertFalse(p.activo)

    # --- __str__ y ordenamiento ---

    def test_str_devuelve_el_nombre(self):
        p = Proveedor.objects.create(nombre='Distribuidora Sur', correo='sur@example.com')
        self.assertEqual(str(p), 'Distribuidora Sur')

    def test_ordering_por_nombre(self):
        Proveedor.objects.create(nombre='Zeta', correo='zeta@example.com')
        Proveedor.objects.create(nombre='Alfa', correo='alfa@example.com')
        nombres = list(Proveedor.objects.values_list('nombre', flat=True))
        self.assertEqual(nombres, ['Alfa', 'Zeta'])

    def test_dos_proveedores_pueden_tener_el_mismo_nombre(self):
        Proveedor.objects.create(nombre='Norte', correo='n1@example.com')
        Proveedor.objects.create(nombre='Norte', correo='n2@example.com')
        self.assertEqual(Proveedor.objects.filter(nombre='Norte').count(), 2)

    # --- Unicidad del correo ---

    def test_correo_es_unico(self):
        Proveedor.objects.create(nombre='A', correo='repetido@example.com')
        with self.assertRaises(IntegrityError), transaction.atomic():
            Proveedor.objects.create(nombre='B', correo='repetido@example.com')

    # --- Validaciones de full_clean ---

    def test_correo_valido_pasa_full_clean(self):
        p = self._proveedor(correo='valido@example.com')
        p.full_clean()

    def test_correo_con_formato_invalido_se_rechaza(self):
        p = self._proveedor(correo='no-es-correo')
        with self.assertRaises(ValidationError) as cm:
            p.full_clean()
        self.assertIn('correo', cm.exception.message_dict)

    def test_correo_vacio_se_rechaza(self):
        p = self._proveedor(correo='')
        with self.assertRaises(ValidationError) as cm:
            p.full_clean()
        self.assertIn('correo', cm.exception.message_dict)

    def test_nombre_vacio_se_rechaza(self):
        p = self._proveedor(nombre='')
        with self.assertRaises(ValidationError) as cm:
            p.full_clean()
        self.assertIn('nombre', cm.exception.message_dict)

    def test_nombre_de_151_caracteres_se_rechaza(self):
        p = self._proveedor(nombre='a' * 151)
        with self.assertRaises(ValidationError) as cm:
            p.full_clean()
        self.assertIn('nombre', cm.exception.message_dict)

    def test_contacto_de_101_caracteres_se_rechaza(self):
        p = self._proveedor(contacto='a' * 101)
        with self.assertRaises(ValidationError) as cm:
            p.full_clean()
        self.assertIn('contacto', cm.exception.message_dict)

    def test_telefono_de_21_caracteres_se_rechaza(self):
        p = self._proveedor(telefono='1' * 21)
        with self.assertRaises(ValidationError) as cm:
            p.full_clean()
        self.assertIn('telefono', cm.exception.message_dict)

    # --- Relación con productos ---

    def test_related_name_productos_en_proveedor(self):
        proveedor = Proveedor.objects.create(nombre='Norte', correo='rel@example.com')
        categoria = Categoria.objects.create(nombre='General')
        Producto.objects.create(
            nombre='Agua', precio='5.00', categoria=categoria, proveedor=proveedor
        )
        Producto.objects.create(
            nombre='Jugo', precio='8.00', categoria=categoria, proveedor=proveedor
        )
        self.assertEqual(proveedor.productos.count(), 2)

    def test_borrar_proveedor_deja_producto_sin_proveedor(self):
        proveedor = Proveedor.objects.create(nombre='Norte', correo='del@example.com')
        categoria = Categoria.objects.create(nombre='General')
        producto = Producto.objects.create(
            nombre='Agua', precio='5.00', categoria=categoria, proveedor=proveedor
        )
        proveedor.delete()
        producto.refresh_from_db()
        self.assertIsNone(producto.proveedor)