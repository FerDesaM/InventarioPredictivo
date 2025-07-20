from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Farmacia(models.Model):
    nombre_farmacia = models.CharField(max_length=255)
    distrito        = models.CharField(max_length=100)
    ciudad          = models.CharField(max_length=100)
    pais            = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre_farmacia

class Producto(models.Model):
    
    product_id      = models.CharField(max_length=50, primary_key=True)
    nombre_producto = models.CharField(max_length=255)
    clase           = models.CharField(max_length=100)
    precio_unitario = models.FloatField()
    fecha_vencimiento = models.DateField()

    def __str__(self):
        return self.product_id



class Empleado(models.Model):
    dni       = models.CharField(max_length=20,unique=True)
    nombre    = models.CharField(max_length=100)
    apellido  = models.CharField(max_length=100)
    password  = models.CharField(max_length=128)
    es_admin  = models.BooleanField(default=False)
    farmacia  = models.ForeignKey("Farmacia", on_delete=models.CASCADE)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Manager(models.Model):
    
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    farmacia = models.ForeignKey('Farmacia', on_delete=models.CASCADE)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class InventarioFarmacia(models.Model):
    
    farmacia = models.ForeignKey(Farmacia, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    stock    = models.IntegerField()

    class Meta:
        unique_together = [['farmacia','producto']]

class Venta(models.Model):
    
    codigo_venta = models.IntegerField(primary_key=True)
    producto     = models.ForeignKey(Producto, on_delete=models.CASCADE)
    empleado     = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True)
    quantity     = models.IntegerField()
    dia          = models.IntegerField()
    month        = models.CharField(max_length=20)
    year         = models.IntegerField()
    sales        = models.FloatField()
    igv          = models.FloatField()
    total        = models.FloatField()
    moneda       = models.CharField(max_length=10)
    estado       = models.CharField(max_length=20)
    tipo_comp    = models.CharField(max_length=50)

    def __str__(self):
        return str(self.codigo_venta)
class Compra(models.Model):
    farmacia           = models.ForeignKey(Farmacia, on_delete=models.CASCADE)
    producto           = models.ForeignKey(Producto, on_delete=models.CASCADE)
    proveedor          = models.CharField(max_length=255)
    cantidad           = models.IntegerField()
    fecha_compra       = models.DateField()
    precio_unitarioC   = models.FloatField()
    total_compra       = models.FloatField()

    def __str__(self):
        return f"Compra {self.id}"