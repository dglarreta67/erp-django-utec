from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from configuracion.models import ConfiguracionERP


class ConfiguracionSingletonTest(TestCase):

    def test_get_instance_crea_registro_si_no_existe(self):
        self.assertEqual(ConfiguracionERP.objects.count(), 0)
        ConfiguracionERP.get_instance()
        self.assertEqual(ConfiguracionERP.objects.count(), 1)

    def test_get_instance_usa_pk_1(self):
        obj = ConfiguracionERP.get_instance()
        self.assertEqual(obj.pk, 1)

    def test_get_instance_devuelve_el_mismo_registro(self):
        a = ConfiguracionERP.get_instance()
        b = ConfiguracionERP.get_instance()
        self.assertEqual(a.pk, b.pk)
        self.assertEqual(ConfiguracionERP.objects.count(), 1)

    def test_get_instance_aplica_valores_por_defecto(self):
        obj = ConfiguracionERP.get_instance()
        self.assertEqual(obj.nombre_empresa, 'Mi Empresa ERP')
        self.assertEqual(obj.moneda, 'MXN')
        self.assertEqual(obj.iva_porcentaje, Decimal('16.00'))

    def test_save_fuerza_pk_1_aunque_se_asigne_otro(self):
        obj = ConfiguracionERP(nombre_empresa='Empresa X', pk=99)
        obj.save()
        self.assertEqual(obj.pk, 1)
        self.assertTrue(ConfiguracionERP.objects.filter(pk=1).exists())

    def test_guardar_dos_veces_no_crea_otro_registro(self):
        ConfiguracionERP(nombre_empresa='Uno').save()
        ConfiguracionERP(nombre_empresa='Dos').save()
        self.assertEqual(ConfiguracionERP.objects.count(), 1)
        self.assertEqual(ConfiguracionERP.objects.get().nombre_empresa, 'Dos')

    def test_str_incluye_empresa_e_iva(self):
        obj = ConfiguracionERP(nombre_empresa='UTEC Celaya')
        self.assertEqual(str(obj), 'UTEC Celaya — IVA 16.00%')


class ConfiguracionCamposTest(TestCase):

    def _config(self, **kwargs):
        datos = {'nombre_empresa': 'Empresa Prueba'}
        datos.update(kwargs)
        return ConfiguracionERP(**datos)

    def test_rfc_es_opcional(self):
        self._config().full_clean()  # no debe lanzar error

    def test_rfc_de_14_caracteres_se_rechaza(self):
        with self.assertRaises(ValidationError) as cm:
            self._config(rfc='A' * 14).full_clean()
        self.assertIn('rfc', cm.exception.message_dict)

    def test_logo_es_opcional(self):
        self._config().full_clean()  # no debe lanzar error

    def test_iva_negativo_se_rechaza(self):
        with self.assertRaises(ValidationError) as cm:
            self._config(iva_porcentaje=Decimal('-0.01')).full_clean()
        self.assertIn('iva_porcentaje', cm.exception.message_dict)

    def test_iva_mayor_a_100_se_rechaza(self):
        with self.assertRaises(ValidationError) as cm:
            self._config(iva_porcentaje=Decimal('100.01')).full_clean()
        self.assertIn('iva_porcentaje', cm.exception.message_dict)

    def test_iva_en_los_limites_se_acepta(self):
        self._config(iva_porcentaje=Decimal('0.00')).full_clean()
        self._config(iva_porcentaje=Decimal('100.00')).full_clean()

    def test_nombre_empresa_vacio_se_rechaza(self):
        with self.assertRaises(ValidationError) as cm:
            self._config(nombre_empresa='').full_clean()
        self.assertIn('nombre_empresa', cm.exception.message_dict)