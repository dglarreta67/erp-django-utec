from django.contrib import admin
from .models import Categoria, Producto

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['pk', 'nombre', 'descripcion']
    search_fields = ['nombre']

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['pk', 'nombre', 'precio', 'stock', 'categoria', 'proveedor', 'activo', 'creado']
    search_fields = ['nombre', 'categoria__nombre', 'proveedor__nombre']
    list_filter = ['activo', 'categoria']
    list_editable = ['precio', 'stock', 'activo']
    readonly_fields = ['creado']
    autocomplete_fields = ['proveedor']
    date_hierarchy = 'creado'
    ordering = ['nombre']
