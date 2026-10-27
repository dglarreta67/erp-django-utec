from django.contrib import admin
from .models import ConfiguracionERP

@admin.register(ConfiguracionERP)
class ConfiguracionERPAdmin(admin.ModelAdmin):
    list_display = ['nombre_empresa', 'rfc', 'moneda', 'iva_porcentaje']

    def has_add_permission(self, request) -> bool:
        return not ConfiguracionERP.objects.exists()

    def has_delete_permission(self, request, obj=None) -> bool:
        return False
