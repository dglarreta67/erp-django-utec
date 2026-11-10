import os
from decimal import ROUND_HALF_UP, Decimal
from io import BytesIO

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.staticfiles import finders
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, DeleteView

from xhtml2pdf import pisa

from configuracion.models import ConfiguracionERP
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


# ── Generación de PDF (xhtml2pdf) ────────────────────────────────

def _link_callback(uri: str, rel: str) -> str:
    """Traduce /media/... y /static/... a rutas de disco para xhtml2pdf."""
    if uri.startswith(settings.MEDIA_URL):
        raiz = os.path.abspath(settings.MEDIA_ROOT)
        ruta = os.path.abspath(os.path.join(raiz, uri[len(settings.MEDIA_URL):]))
        if ruta.startswith(raiz + os.sep) and os.path.isfile(ruta):
            return ruta

    if uri.startswith(settings.STATIC_URL):
        relativa = uri[len(settings.STATIC_URL):]
        ruta = os.path.join(settings.STATIC_ROOT, relativa)
        if os.path.isfile(ruta):
            return ruta
        encontrada = finders.find(relativa)  # desarrollo, sin collectstatic
        if encontrada:
            return encontrada

    # Si no se encuentra, xhtml2pdf omite el recurso y sigue generando el PDF
    return uri


def calcular_totales(subtotal, iva_porcentaje) -> dict:
    """Subtotal, IVA y total con 2 decimales (redondeo comercial).

    Venta.total es la suma de las líneas SIN IVA; el IVA se suma aparte.
    Ejemplo: calcular_totales(Decimal("3000"), Decimal("16"))
             -> subtotal 3000.00, iva 480.00, total 3480.00
    """
    centavos = Decimal("0.01")
    subtotal = Decimal(subtotal).quantize(centavos, ROUND_HALF_UP)
    iva = (subtotal * Decimal(iva_porcentaje) / 100).quantize(centavos, ROUND_HALF_UP)
    return {"subtotal": subtotal, "iva": iva, "total_con_iva": subtotal + iva}


@login_required
def venta_pdf(request, venta_id: int) -> HttpResponse:
    """Genera y descarga la factura de una venta en PDF (xhtml2pdf)."""
    venta = get_object_or_404(
        Venta.objects.select_related("cliente").prefetch_related(
            "detalles__producto__categoria"
        ),
        pk=venta_id,
    )
    config = ConfiguracionERP.get_instance()
    context = {
        "venta": venta,
        "config": config,
        "hoy": timezone.localdate(),
        **calcular_totales(venta.total, config.iva_porcentaje),
    }

    html_string = render_to_string("ventas/factura_pdf.html", context, request=request)

    buffer = BytesIO()
    resultado = pisa.CreatePDF(
        html_string,
        dest=buffer,
        encoding="utf-8",
        link_callback=_link_callback,
    )
    if resultado.err:
        return HttpResponse("No se pudo generar el PDF.", status=500)

    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="factura_{venta.pk:05d}.pdf"'
    return response