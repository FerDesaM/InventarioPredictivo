from django.test import TestCase, Client
from django.urls import reverse
from farmacia_app.models import Farmacia, Producto, Empleado, Venta, Manager
from datetime import date

class ModelTests(TestCase):

    def setUp(self):
        # Configuración inicial para las pruebas
        self.farmacia = Farmacia.objects.create(nombre_farmacia="Farmacia Central", distrito="Centro", ciudad="Ciudad", pais="País")
        self.producto = Producto.objects.create(product_id="P001", nombre_producto="Paracetamol", clase="Analgésico", precio_unitario=5.00, fecha_vencimiento=date(2025, 12, 31))
        self.empleado = Empleado.objects.create(dni="12345678", nombre="Juan", apellido="Pérez", farmacia=self.farmacia, password="initial_password")
        self.empleado.set_password("password123")
        self.empleado.save()

    def test_creacion_farmacia(self):
        # Prueba la creación de una farmacia
        self.assertEqual(self.farmacia.nombre_farmacia, "Farmacia Central")
        self.assertEqual(str(self.farmacia), "Farmacia Central")

    def test_creacion_producto(self):
        # Prueba la creación de un producto
        self.assertEqual(self.producto.nombre_producto, "Paracetamol")
        self.assertEqual(str(self.producto), "P001")

    def test_creacion_empleado(self):
        # Prueba la creación de un empleado y la verificación de la contraseña
        self.assertEqual(self.empleado.nombre, "Juan")
        self.assertTrue(self.empleado.check_password("password123"))
        self.assertFalse(self.empleado.check_password("wrongpassword"))
        self.assertEqual(str(self.empleado), "Juan Pérez")

    def test_creacion_venta(self):
        # Prueba la creación de una venta
        venta = Venta.objects.create(
            codigo_venta=1,
            producto=self.producto,
            empleado=self.empleado,
            quantity=10,
            dia=25,
            month="Julio",
            year=2025,
            sales=50.00,
            igv=9.00,
            total=59.00,
            moneda="USD",
            estado="Completado",
            tipo_comp="Boleta"
        )
        self.assertEqual(venta.codigo_venta, 1)
        self.assertEqual(venta.producto.nombre_producto, "Paracetamol")
        self.assertEqual(str(venta), "1")

class ViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.farmacia = Farmacia.objects.create(nombre_farmacia="Farmacia Central", distrito="Centro", ciudad="Ciudad", pais="País")
        
        self.empleado = Empleado.objects.create(dni="12345678", nombre="Juan", apellido="Pérez", farmacia=self.farmacia, es_admin=True, password="initial_password")
        self.empleado.set_password("password123")
        self.empleado.save()

        self.manager = Manager.objects.create(email="manager@test.com", nombre="Manager", apellido="Test", farmacia=self.farmacia, password="initial_password")
        self.manager.set_password("password123")
        self.manager.save()

    def test_login_view_empleado(self):
        response = self.client.post(reverse("login"), {"usuario": "12345678", "password": "password123"}, follow=True)
        self.assertRedirects(response, reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard")

    def test_login_view_manager(self):
        response = self.client.post(reverse("login"), {"usuario": "manager@test.com", "password": "password123"}, follow=True)
        self.assertRedirects(response, reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard")

    def test_login_view_fail(self):
        response = self.client.post(reverse("login"), {"usuario": "12345678", "password": "wrongpassword"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Contraseña incorrecta")

    def test_dashboard_view_unauthenticated(self):
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(response, "/login/?next=/dashboard/")

    def test_dashboard_view_authenticated(self):
        # Simular el login del empleado
        self.client.post(reverse("login"), {"usuario": "12345678", "password": "password123"})
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard")

