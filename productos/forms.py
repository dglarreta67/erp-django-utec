import os

from django import forms

from .models import Producto

MAX_IMAGEN_BYTES = 5 * 1024 * 1024  # 5 MB
EXTENSIONES_IMAGEN = ('.jpg', '.jpeg', '.png', '.webp')


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre', 'precio', 'stock', 'categoria',
            'proveedor', 'activo', 'imagen',
        ]

    def clean_imagen(self):
        imagen = self.cleaned_data.get('imagen')
        if imagen:
            if imagen.size > MAX_IMAGEN_BYTES:
                raise forms.ValidationError('La imagen no puede superar 5 MB.')
            extension = os.path.splitext(imagen.name)[1].lower()
            if extension not in EXTENSIONES_IMAGEN:
                raise forms.ValidationError('Formato no permitido. Usa JPEG, PNG o WEBP.')
        return imagen