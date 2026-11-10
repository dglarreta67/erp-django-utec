from django.conf import settings
from django.test import TestCase
from django.urls import get_resolver, resolve, reverse


class RutasProyectoTest(TestCase):

    def test_raiz_se_llama_inicio(self):
        self.assertEqual(reverse('inicio'), '/')

    def test_raiz_usa_la_vista_bienvenida(self):
        self.assertEqual(resolve('/').func.__name__, 'bienvenida')

    def test_raiz_responde_200(self):
        # Depende de que exista la plantilla de bienvenida
        r = self.client.get('/')
        self.assertEqual(r.status_code, 200)

    def test_cada_app_tiene_namespace_registrado(self):
        namespaces = get_resolver().namespace_dict
        for ns in ['clientes', 'proveedores', 'productos', 'ventas', 'reportes']:
            with self.subTest(namespace=ns):
                self.assertIn(ns, namespaces)

    def test_admin_se_resuelve_bajo_su_namespace(self):
        self.assertEqual(resolve('/admin/').namespace, 'admin')

    def test_admin_redirige_a_login_si_no_hay_sesion(self):
        r = self.client.get('/admin/')
        self.assertEqual(r.status_code, 302)
        self.assertIn('/admin/login/', r['Location'])

    def test_login_de_allauth_esta_en_accounts(self):
        self.assertEqual(reverse('account_login'), '/accounts/login/')

    def test_login_url_de_settings_coincide_con_allauth(self):
        self.assertEqual(settings.LOGIN_URL, reverse('account_login'))

    def test_ruta_inexistente_responde_404(self):
        r = self.client.get('/ruta-que-no-existe/')
        self.assertEqual(r.status_code, 404)