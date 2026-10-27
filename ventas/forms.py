from django import forms
from .models import DetalleVenta, Venta

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['cliente']
        widgets = {'cliente': forms.Select(attrs={'class': 'erp-input'})}

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['producto', 'cantidad', 'precio_unitario']
        widgets = {
            'producto': forms.Select(attrs={'class': 'erp-input'}),
            'cantidad': forms.NumberInput(attrs={'class': 'erp-input', 'min': '1', 'value': '1'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'erp-input', 'step': '0.01', 'min': '0'}),
        }
        labels = {'precio_unitario': 'Precio unitario ($)'}
