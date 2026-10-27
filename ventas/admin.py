from django.contrib import admin
from .models import DetalleVenta, Pedido, Venta

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    fields = ['producto', 'cantidad', 'precio_unitario']

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['pk', 'cliente', 'fecha', 'total_admin']
    search_fields = ['cliente__nombre', 'cliente__correo']
    readonly_fields = ['fecha']
    inlines = [DetalleVentaInline]
    date_hierarchy = 'fecha'

    @admin.display(description='Total ($)')
    def total_admin(self, obj: Venta) -> str:
        return f"${obj.total:.2f}"

@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ['pk', 'venta', 'producto', 'cantidad', 'precio_unitario', 'subtotal_admin']
    search_fields = ['producto__nombre', 'venta__pk']

    @admin.display(description='Subtotal ($)')
    def subtotal_admin(self, obj: DetalleVenta) -> str:
        return f"${obj.subtotal:.2f}"

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['numero_pedido', 'cliente', 'estado', 'fecha_pedido', 'total_pagado']
    search_fields = ['numero_pedido', 'cliente__nombre']
    list_filter = ['estado']
    readonly_fields = ['fecha_pedido']
