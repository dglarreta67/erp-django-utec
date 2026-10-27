from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from proveedores.models import Proveedor

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self) -> str:
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    precio = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Precio ($)'
    )
    stock = models.IntegerField(
        default=0, validators=[MinValueValidator(0)],
        verbose_name='Stock disponible'
    )
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT,
        related_name='productos', verbose_name='Categoría'
    )
    proveedor = models.ForeignKey(
        Proveedor, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='productos', verbose_name='Proveedor'
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')
    creado = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de registro')

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']

    def clean(self) -> None:
        errors = {}
        if self.precio is not None and self.precio < 0:
            errors['precio'] = f'El precio no puede ser negativo. Valor recibido: {self.precio}'
        if self.stock is not None and self.stock < 0:
            errors['stock'] = f'El stock no puede ser negativo. Valor recibido: {self.stock}'
        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"{self.nombre} (${self.precio:.2f})"
