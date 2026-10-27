from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['pk', 'nombre', 'correo', 'telefono', 'activo', 'creado']
    search_fields = ['nombre', 'correo', 'telefono']
    list_filter = ['activo']
    list_editable = ['activo']
    readonly_fields = ['creado']
    date_hierarchy = 'creado'
    ordering = ['nombre']
