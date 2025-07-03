from django.db import models

class Farmacia(models.Model):
    nombre_farmacia = models.CharField(max_length=255)
    distrito = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)
    pais = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre_farmacia

class Producto(models.Model):
    product_id = models.CharField(max_length=50, primary_key=True)
    nombre_producto = models.CharField(max_length=255)
    clase = models.CharField(max_length=100)
    precio_unitario = models.FloatField()
    fecha_vencimiento = models.DateField()

    def __str__(self):
        return self.nombre_producto

class Empleado(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=20)
    farmacia = models.ForeignKey(
        Farmacia,
        on_delete=models.CASCADE,
        related_name='empleados'
    )

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Manager(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    farmacia = models.OneToOneField(
        Farmacia,
        on_delete=models.CASCADE,
        related_name='manager'
    )

    def __str__(self):
        return f"{self.nombre} {self.apellido} (Manager)"

class InventarioFarmacia(models.Model):
    farmacia = models.ForeignKey(
        Farmacia,
        on_delete=models.CASCADE,
        related_name='inventario'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE
    )
    stock = models.IntegerField()

    class Meta:
        unique_together = [['farmacia', 'producto']]
        verbose_name_plural = 'Inventario Farmacias'

    def __str__(self):
        return f"{self.farmacia} - {self.producto}: {self.stock}"

class Compra(models.Model):
    farmacia = models.ForeignKey(
        Farmacia,
        on_delete=models.CASCADE,
        related_name='compras'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE
    )
    proveedor = models.CharField(max_length=255)
    cantidad = models.IntegerField()
    fecha_compra = models.DateField()
    precio_unitarioC = models.FloatField()
    total_compra = models.FloatField()

    def __str__(self):
        return f"Compra #{self.id} - {self.farmacia}"

class Venta(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE
    )
    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        null=True
    )
    quantity = models.IntegerField()
    dia = models.IntegerField()
    month = models.CharField(max_length=20)
    year = models.IntegerField()
    sales = models.FloatField()
    igv = models.FloatField()
    total = models.FloatField()
    moneda = models.CharField(max_length=10)
    estado = models.CharField(max_length=20)
    tipo_comp = models.CharField(max_length=10)

    def __str__(self):
        return f"Venta #{self.id} - {self.producto}"
