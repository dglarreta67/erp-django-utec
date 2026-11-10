from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase

from productos.models import Categoria, Producto


class CategoriaTest(TestCase):

    def test_str_devuelve_el_nombre(self):
        cat = Categoria.objects.create(nombre='Bebidas')
        self.assertEqual(str(cat), 'Bebidas')

    def test_nombre_es_unico(self):
        Categoria.objects.create(nombre='Bebidas')
        with self.assertRaises(IntegrityError), transaction.atomic():
            Categoria.objects.create(nombre='Bebidas')

    def test_descripcion_es_opcional(self):
        cat = Categoria(nombre='Limpieza')
        cat.full_clean()  # no debe lanzar error
        self.assertEqual(cat.descripcion, '')

    def test_ordering_por_nombre(self):
        Categoria.objects.create(nombre='Zapatos')
        Categoria.objects.create(nombre='Abarrotes')
        nombres = list(Categoria.objects.values_list('nombre', flat=True))
        self.assertEqual(nombres, ['Abarrotes', 'Zapatos'])


class ProductoTest(TestCase):

    def setUp(self):
        self.categoria = Categoria.objects.create(nombre='General')

    def _producto(self, **kwargs):
        datos = {
            'nombre': 'Refresco',
            'precio': Decimal('10.00'),
            'categoria': self.categoria,
        }
        datos.update(kwargs)
        return Producto(**datos)

    # --- Valores por defecto y campos automáticos ---

    def test_stock_por_defecto_es_cero(self):
        p = Producto.objects.create(
            nombre='Agua', precio=Decimal('5.00'), categoria=self.categoria
        )
        self.assertEqual(p.stock, 0)

    def test_activo_por_defecto_es_true(self):
        p = Producto.objects.create(
            nombre='Agua', precio=Decimal('5.00'), categoria=self.categoria
        )
        self.assertTrue(p.activo)

    def test_creado_se_asigna_automaticamente(self):
        p = Producto.objects.create(
            nombre='Agua', precio=Decimal('5.00'), categoria=self.categoria
        )
        self.assertIsNotNone(p.creado)

    def test_proveedor_es_opcional(self):
        p = Producto.objects.create(
            nombre='Agua', precio=Decimal('5.00'), categoria=self.categoria
        )
        self.assertIsNone(p.proveedor)

    def test_activo_puede_desactivarse_y_persiste(self):
        p = Producto.objects.create(
            nombre='Agua', precio=Decimal('5.00'), categoria=self.categoria
        )
        p.activo = False
        p.save()
        p.refresh_from_db()
        self.assertFalse(p.activo)

    # --- __str__ ---

    def test_str_incluye_nombre_y_precio_con_dos_decimales(self):
        p = self._producto(nombre='Refresco', precio=Decimal('10'))
        self.assertEqual(str(p), 'Refresco ($10.00)')

    def test_str_redondea_a_dos_decimales(self):
        p = self._producto(nombre='Pan', precio=Decimal('5.5'))
        self.assertEqual(str(p), 'Pan ($5.50)')

    # --- Relaciones ---

    def test_related_name_productos_en_categoria(self):
        Producto.objects.create(
            nombre='Agua', precio=Decimal('5.00'), categoria=self.categoria
        )
        Producto.objects.create(
            nombre='Jugo', precio=Decimal('8.00'), categoria=self.categoria
        )
        self.assertEqual(self.categoria.productos.count(), 2)

    def test_no_se_puede_borrar_categoria_con_productos(self):
        Producto.objects.create(
            nombre='Agua', precio=Decimal('5.00'), categoria=self.categoria
        )
        with self.assertRaises(ProtectedError):
            self.categoria.delete()

    # --- Ordenamiento ---

    def test_ordering_por_nombre(self):
        Producto.objects.create(
            nombre='Zanahoria', precio=Decimal('3.00'), categoria=self.categoria
        )
        Producto.objects.create(
            nombre='Ajo', precio=Decimal('2.00'), categoria=self.categoria
        )
        nombres = list(Producto.objects.values_list('nombre', flat=True))
        self.assertEqual(nombres, ['Ajo', 'Zanahoria'])

    # --- Validaciones de clean() ---

    def test_clean_acepta_valores_validos(self):
        p = self._producto(precio=Decimal('0.00'), stock=3)
        p.clean()  # no debe lanzar error

    def test_clean_rechaza_precio_negativo(self):
        p = self._producto(precio=Decimal('-1.00'))
        with self.assertRaises(ValidationError) as cm:
            p.clean()
        self.assertIn('precio', cm.exception.message_dict)

    def test_clean_rechaza_stock_negativo(self):
        p = self._producto(stock=-5)
        with self.assertRaises(ValidationError) as cm:
            p.clean()
        self.assertIn('stock', cm.exception.message_dict)

    # --- Validadores de campo (full_clean) ---

    def test_full_clean_rechaza_precio_negativo(self):
        p = self._producto(precio=Decimal('-0.01'))
        with self.assertRaises(ValidationError) as cm:
            p.full_clean()
        self.assertIn('precio', cm.exception.message_dict)

    def test_full_clean_rechaza_stock_negativo(self):
        p = self._producto(stock=-1)
        with self.assertRaises(ValidationError) as cm:
            p.full_clean()
        self.assertIn('stock', cm.exception.message_dict)