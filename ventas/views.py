from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView
from .forms import DetalleVentaForm, VentaForm
from .models import DetalleVenta, Venta

class VentaListView(ListView):
    model = Venta
    template_name = 'ventas/lista.html'
    context_object_name = 'ventas'
    paginate_by = 20

    def get_queryset(self):
        return Venta.objects.select_related('cliente').order_by('-fecha')

class VentaDetailView(DetailView):
    model = Venta
    template_name = 'ventas/detalle.html'
    context_object_name = 'venta'
    pk_url_kwarg = 'venta_id'

    def get_queryset(self):
        return Venta.objects.select_related('cliente').prefetch_related('detalles__producto')

@login_required
@permission_required('ventas.add_venta', raise_exception=True)
def crear_venta(request):
    venta_form = VentaForm(request.POST or None)
    detalle_form = DetalleVentaForm(request.POST or None)

    if request.method == 'POST':
        if venta_form.is_valid() and detalle_form.is_valid():
            venta = venta_form.save()
            detalle = detalle_form.save(commit=False)
            detalle.venta = venta
            detalle.save()
            messages.success(request, f'Venta #{venta.pk} registrada. Total: ${venta.total:.2f}')
            return redirect('ventas:detalle', venta_id=venta.pk)

    return render(request, 'ventas/crear.html', {
        'venta_form': venta_form,
        'detalle_form': detalle_form,
    })

class VentaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Venta
    template_name = 'ventas/eliminar.html'
    pk_url_kwarg = 'venta_id'
    success_url = reverse_lazy('ventas:lista')
    permission_required = 'ventas.delete_venta'
    raise_exception = True

    def form_valid(self, form):
        pk = self.object.pk
        response = super().form_valid(form)
        messages.success(self.request, f'Venta #{pk} eliminada.')
        return response
