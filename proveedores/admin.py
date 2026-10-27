from django.contrib import admin
from .models import Proveedor

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['pk', 'nombre', 'contacto', 'correo', 'telefono', 'activo', 'creado']
    search_fields = ['nombre', 'contacto', 'correo']
    list_filter = ['activo']
    list_editable = ['activo']
    readonly_fields = ['creado']
    date_hierarchy = 'creado'
