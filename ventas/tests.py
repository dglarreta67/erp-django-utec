from decimal import Decimal
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase
from django.utils import timezone

from clientes.models import Cliente
from productos.models import Categoria, Producto
from ventas.models import DetalleVenta, Pedido, Venta


def _cliente(nombre='Cliente Prueba'):
    # Ajusta esta línea si Cliente requiere campos obligatorios distintos a 'nombre'
    return Cliente.objects.create(nombre=nombre)


class VentaBaseTest(TestCase):

    def setUp(self):
        self.cliente = _cliente()
        self.categoria = Categoria.objects.create(nombre='General')
        self.agua = Producto.objects.create(
            nombre='Agua', precio=Decimal('10.00'), categoria=self.categoria
        )
        self.pan = Producto.objects.create(
            nombre='Pan', precio=Decimal('5.50'), categoria=self.categoria
        )


class VentaTest(VentaBaseTest):

    def test_total_sin_detalles_es_cero(self):
        venta = Venta.objects.create(cliente=self.cliente)
        self.assertEqual(venta.total, Decimal('0.00'))

    def test_total_con_un_detalle(self):
        venta = Venta.objects.create(cliente=self.cliente)
        DetalleVenta.objects.create(venta=venta, producto=self.agua, cantidad=2)
        self.assertEqual(venta.total, Decimal('20.00'))

    def test_total_suma_varios_productos(self):
        venta = Venta.objects.create(cliente=self.cliente)
        DetalleVenta.objects.create(venta=venta, producto=self.agua, cantidad=2)
        DetalleVenta.objects.create(venta=venta, producto=self.pan, cantidad=3)
        self.assertEqual(venta.total, Decimal('36.50'))

    def test_str_incluye_numero_y_cliente(self):
        venta = Venta.objects.create(cliente=self.cliente)
        texto = str(venta)
        self.assertTrue(texto.startswith(f'Venta #{venta.pk}'))
        self.assertIn(str(self.cliente), texto)

    def test_ordering_mas_reciente_primero(self):
        antigua = Venta.objects.create(cliente=self.cliente)
        reciente = Venta.objects.create(cliente=self.cliente)
        Venta.objects.filter(pk=antigua.pk).update(
            fecha=timezone.now() - timedelta(days=2)
        )
        Venta.objects.filter(pk=reciente.pk).update(fecha=timezone.now())
        pks = list(Venta.objects.values_list('pk', flat=True))
        self.assertEqual(pks, [reciente.pk, antigua.pk])

    def test_related_name_ventas_en_cliente(self):
        Venta.objects.create(cliente=self.cliente)
        Venta.objects.create(cliente=self.cliente)
        self.assertEqual(self.cliente.ventas.count(), 2)

    def test_borrar_venta_borra_sus_detalles(self):
        venta = Venta.objects.create(cliente=self.cliente)
        DetalleVenta.objects.create(venta=venta, producto=self.agua, cantidad=1)
        venta.delete()
        self.assertEqual(DetalleVenta.objects.count(), 0)

    def test_no_se_puede_borrar_cliente_con_ventas(self):
        Venta.objects.create(cliente=self.cliente)
        with self.assertRaises(ProtectedError):
            self.cliente.delete()

    def test_no_se_puede_borrar_producto_en_una_venta(self):
        venta = Venta.objects.create(cliente=self.cliente)
        DetalleVenta.objects.create(venta=venta, producto=self.agua, cantidad=1)
        with self.assertRaises(ProtectedError):
            self.agua.delete()


class DetalleVentaTest(VentaBaseTest):

    def setUp(self):
        super().setUp()
        self.venta = Venta.objects.create(cliente=self.cliente)

    def test_subtotal_es_precio_por_cantidad(self):
        d = DetalleVenta.objects.create(
            venta=self.venta, producto=self.pan, cantidad=4
        )
        self.assertEqual(d.subtotal, Decimal('22.00'))

    def test_save_copia_precio_del_producto_si_no_hay_precio(self):
        d = DetalleVenta(venta=self.venta, producto=self.agua, cantidad=1,
                         precio_unitario=None)
        d.save()
        d.refresh_from_db()
        self.assertEqual(d.precio_unitario, Decimal('10.00'))

    def test_precio_unitario_manual_se_respeta(self):
        d = DetalleVenta.objects.create(
            venta=self.venta, producto=self.agua,
            cantidad=1, precio_unitario=Decimal('7.50')
        )
        d.refresh_from_db()
        self.assertEqual(d.precio_unitario, Decimal('7.50'))

    def test_precio_manual_cambia_el_subtotal(self):
        d = DetalleVenta.objects.create(
            venta=self.venta, producto=self.agua,
            cantidad=2, precio_unitario=Decimal('7.50')
        )
        self.assertEqual(d.subtotal, Decimal('15.00'))

    def test_clean_rechaza_cantidad_cero(self):
        d = DetalleVenta(venta=self.venta, producto=self.agua,
                         cantidad=0, precio_unitario=Decimal('10.00'))
        with self.assertRaises(ValidationError) as cm:
            d.clean()
        self.assertIn('cantidad', cm.exception.message_dict)

    def test_clean_acepta_cantidad_uno(self):
        d = DetalleVenta(venta=self.venta, producto=self.agua,
                         cantidad=1, precio_unitario=Decimal('10.00'))
        d.clean()  # no debe lanzar error

    def test_full_clean_rechaza_cantidad_negativa(self):
        d = DetalleVenta(venta=self.venta, producto=self.agua,
                         cantidad=-1, precio_unitario=Decimal('10.00'))
        with self.assertRaises(ValidationError):
            d.full_clean()

    def test_str_muestra_producto_y_cantidad(self):
        d = DetalleVenta.objects.create(
            venta=self.venta, producto=self.agua, cantidad=3
        )
        self.assertEqual(str(d), 'Agua × 3')

    def test_related_name_detalles_en_venta(self):
        DetalleVenta.objects.create(venta=self.venta, producto=self.agua, cantidad=1)
        DetalleVenta.objects.create(venta=self.venta, producto=self.pan, cantidad=1)
        self.assertEqual(self.venta.detalles.count(), 2)


class PedidoTest(VentaBaseTest):

    def _pedido(self, numero='PED-001', **kwargs):
        return Pedido.objects.create(
            numero_pedido=numero, cliente=self.cliente, **kwargs
        )

    def test_estado_por_defecto_es_pendiente(self):
        self.assertEqual(self._pedido().estado, 'pendiente')

    def test_fecha_entrega_es_opcional(self):
        pedido = self._pedido()
        pedido.full_clean()  # no debe lanzar error
        self.assertIsNone(pedido.fecha_entrega)

    def test_numero_pedido_es_unico(self):
        self._pedido(numero='PED-002')
        with self.assertRaises(IntegrityError), transaction.atomic():
            self._pedido(numero='PED-002')

    def test_str_incluye_numero_y_estado_legible(self):
        pedido = self._pedido(numero='PED-003', estado='pagado')
        texto = str(pedido)
        self.assertIn('PED-003', texto)
        self.assertIn('Pago confirmado', texto)

    def test_clean_rechaza_entrega_anterior_al_pedido(self):
        pedido = self._pedido(numero='PED-004')
        pedido.fecha_entrega = pedido.fecha_pedido.date() - timedelta(days=1)
        with self.assertRaises(ValidationError) as cm:
            pedido.clean()
        self.assertIn('fecha_entrega', cm.exception.message_dict)

    def test_clean_acepta_entrega_el_mismo_dia(self):
        pedido = self._pedido(numero='PED-005')
        pedido.fecha_entrega = pedido.fecha_pedido.date()
        pedido.clean()  # no debe lanzar error

    def test_clean_acepta_entrega_posterior(self):
        pedido = self._pedido(numero='PED-006')
        pedido.fecha_entrega = pedido.fecha_pedido.date() + timedelta(days=3)
        pedido.clean()  # no debe lanzar error

    def test_total_pagado_negativo_se_rechaza(self):
        pedido = self._pedido(numero='PED-007')
        pedido.total_pagado = Decimal('-1.00')
        with self.assertRaises(ValidationError):
            pedido.full_clean()

    def test_estado_invalido_se_rechaza(self):
        pedido = self._pedido(numero='PED-008')
        pedido.estado = 'inventado'
        with self.assertRaises(ValidationError):
            pedido.full_clean()

    def test_ordering_mas_reciente_primero(self):
        viejo = self._pedido(numero='PED-009')
        nuevo = self._pedido(numero='PED-010')
        Pedido.objects.filter(pk=viejo.pk).update(
            fecha_pedido=timezone.now() - timedelta(days=5)
        )
        Pedido.objects.filter(pk=nuevo.pk).update(fecha_pedido=timezone.now())
        pks = list(Pedido.objects.values_list('pk', flat=True))
        self.assertEqual(pks, [nuevo.pk, viejo.pk])