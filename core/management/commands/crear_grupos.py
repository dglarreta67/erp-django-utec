from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from clientes.models       import Cliente
from configuracion.models  import ConfiguracionERP
from productos.models      import Categoria, Producto
from proveedores.models    import Proveedor
from ventas.models         import DetalleVenta, Pedido, Venta


def _permisos(*modelos: type, acciones=('add', 'change', 'delete', 'view')):
    ct_ids = [
        ContentType.objects.get_for_model(m).pk
        for m in modelos
    ]
    return Permission.objects.filter(
        content_type_id__in=ct_ids,
        codename__in=[
            f'{accion}_{m._meta.model_name}'
            for m in modelos
            for accion in acciones
        ]
    )


class Command(BaseCommand):
    help = 'Crea o actualiza los 3 grupos de acceso del ERP'

    def _write(self, options, msg):
        """Escribe el mensaje solo si la verbosidad lo permite."""
        if options.get('verbosity', 1) >= 1:
            self.stdout.write(msg)

    def handle(self, *args, **options):
        self._write(options, self.style.MIGRATE_HEADING(
            '\nConfigurando grupos de acceso del ERP...\n'
        ))

        # GERENTE
        gerente, _ = Group.objects.get_or_create(name='Gerente')
        permisos_gerente = _permisos(
            Cliente, Proveedor, Categoria, Producto,
            Venta, DetalleVenta, Pedido, ConfiguracionERP,
            acciones=('add', 'change', 'delete', 'view')
        )
        gerente.permissions.set(permisos_gerente)
        self._write(options, self.style.SUCCESS(
            f'  ✅ Gerente — {permisos_gerente.count()} permisos asignados'
        ))

        # VENDEDOR
        vendedor, _ = Group.objects.get_or_create(name='Vendedor')
        permisos_vendedor = _permisos(
            Venta, DetalleVenta,
            acciones=('add', 'view')
        ) | _permisos(
            Producto, Cliente,
            acciones=('view',)
        )
        vendedor.permissions.set(permisos_vendedor)
        self._write(options, self.style.SUCCESS(
            f'  ✅ Vendedor — {permisos_vendedor.count()} permisos asignados'
        ))

        # ALMACÉN
        almacen, _ = Group.objects.get_or_create(name='Almacén')
        permisos_almacen = _permisos(
            Producto, Categoria,
            acciones=('add', 'change', 'view')
        ) | _permisos(
            Proveedor,
            acciones=('view',)
        )
        almacen.permissions.set(permisos_almacen)
        self._write(options, self.style.SUCCESS(
            f'  ✅ Almacén — {permisos_almacen.count()} permisos asignados'
        ))

        self._write(options, self.style.SUCCESS(
            '\n🎉 Grupos configurados exitosamente.'
        ))