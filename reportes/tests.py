from django.test import TestCase
from django.urls import resolve, reverse

from reportes import views


class ReportesUrlsTest(TestCase):

    def test_lista_se_resuelve_con_nombre_namespaced(self):
        self.assertEqual(reverse('reportes:lista'), '/reportes/')

    def test_lista_usa_la_vista_index(self):
        self.assertIs(resolve('/reportes/').func, views.index)

    def test_lista_usa_el_namespace_reportes(self):
        self.assertEqual(resolve('/reportes/').namespace, 'reportes')

    def test_lista_nombre_de_ruta_es_lista(self):
        self.assertEqual(resolve('/reportes/').url_name, 'lista')

    def test_ruta_sin_slash_final_no_resuelve(self):
        r = self.client.get('/reportes')
        self.assertIn(r.status_code, (301, 404))

    def test_subruta_inexistente_responde_404(self):
        r = self.client.get('/reportes/no-existe/')
        self.assertEqual(r.status_code, 404)


class ReportesVistaTest(TestCase):

    def test_index_responde_200_sin_login(self):
        r = self.client.get(reverse('reportes:lista'))
        self.assertEqual(r.status_code, 200)

    def test_index_usa_la_plantilla_correcta(self):
        r = self.client.get(reverse('reportes:lista'))
        self.assertTemplateUsed(r, 'reportes/index.html')

    def test_index_pasa_el_titulo_en_el_contexto(self):
        r = self.client.get(reverse('reportes:lista'))
        self.assertEqual(r.context['titulo'], 'Reportes')