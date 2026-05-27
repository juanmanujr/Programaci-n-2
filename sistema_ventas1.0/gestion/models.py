from django.db import models
from decimal import Decimal

# ====================================================================
# TABLA 1: Cliente
# ====================================================================
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True)
    fecha_registro = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Clientes"

    def __str__(self):
        return f'{self.nombre} {self.apellido}'


# ====================================================================
# TABLA 2: Proveedor
# ====================================================================
class Proveedor(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    contacto = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    email = models.EmailField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Proveedores" # CORREGIDO

    def __str__(self):
        return self.nombre


# ====================================================================
# TABLA 3: Empleado
# ====================================================================
class Empleado(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)
    fecha_contratacion = models.DateField()
    salario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name_plural = "Empleados"

    def __str__(self):
        return f'{self.nombre} {self.apellido} ({self.cargo})'


# ====================================================================
# TABLA 4: Categoría de Producto
# ====================================================================
class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categorías de Productos" # CORREGIDO

    def __str__(self):
        return self.nombre


# ====================================================================
# TABLA 5: Producto
# ====================================================================
class Producto(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True)
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = "Productos"

    def __str__(self):
        return self.nombre


# ====================================================================
# TABLA 6: Venta (Cabecera)
# ====================================================================
class Venta(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    empleado = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=50, default='Pendiente')

    class Meta:
        verbose_name_plural = "Ventas"

    def save(self, *args, **kwargs):
        # Recalcula el total sumando los subtotales de sus detalles (si el objeto existe)
        if self.pk:
            self.total = sum(detalle.subtotal for detalle in self.detalleventa_set.all())
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Venta #{self.id} ({self.fecha.strftime("%Y-%m-%d")})'


# ====================================================================
# TABLA 7: Detalle de Venta (LÓGICA DE SALIDA DE INVENTARIO)
# ====================================================================
class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    _cantidad_original = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.pk:
            self._cantidad_original = self.cantidad

    class Meta:
        verbose_name = "Detalle de Venta" # Singular
        verbose_name_plural = "Detalles de Venta" # Plural

    def save(self, *args, **kwargs):
        # 1. CÁLCULO DEL SUBTOTAL
        self.subtotal = Decimal(self.cantidad) * self.precio_unitario

        # 2. GESTIÓN DEL INVENTARIO
        if self.pk:
            diferencia = self.cantidad - (self._cantidad_original if self._cantidad_original is not None else 0)
            self.producto.stock -= diferencia
            self.producto.save(update_fields=['stock'])
            
            InventarioMovimiento.objects.create(
                producto=self.producto, 
                tipo='Salida', 
                cantidad=abs(diferencia),
                descripcion=f'Venta #{self.venta.id} - {"Modificación" if diferencia != 0 else "Actualización"}'
            )
        else:
            self.producto.stock -= self.cantidad
            self.producto.save(update_fields=['stock'])
            
            InventarioMovimiento.objects.create(
                producto=self.producto, 
                tipo='Salida', 
                cantidad=self.cantidad,
                descripcion=f'Venta #{self.venta.id} - Nueva Venta'
            )

        super().save(*args, **kwargs)
        
        # 3. RECALCULAR EL TOTAL DE LA VENTA PADRE
        if self.venta:
            self.venta.save()
            
    # Lógica para devolver el stock si se borra la línea de detalle
    def delete(self, *args, **kwargs):
        self.producto.stock += self.cantidad
        self.producto.save(update_fields=['stock'])
        InventarioMovimiento.objects.create(
            producto=self.producto, 
            tipo='Entrada', 
            cantidad=self.cantidad,
            descripcion=f'Venta #{self.venta.id} - Eliminación de Detalle'
        )
        super().delete(*args, **kwargs)
            
    def __str__(self):
        return f'{self.producto.nombre} x{self.cantidad}'


# ====================================================================
# TABLA 8: Compra (Cabecera)
# ====================================================================
class Compra(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)
    empleado = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=50, default='Pendiente')

    class Meta:
        verbose_name_plural = "Compras"

    def save(self, *args, **kwargs):
        # Recalcula el total sumando los subtotales de sus detalles (si el objeto existe)
        if self.pk:
            self.total = sum(detalle.subtotal for detalle in self.detallecompra_set.all())
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Compra #{self.id} ({self.fecha.strftime("%Y-%m-%d")})'

# ====================================================================
# TABLA 9: Detalle de Compra (LÓGICA DE ENTRADA DE INVENTARIO)
# ====================================================================
class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    _cantidad_original = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.pk:
            self._cantidad_original = self.cantidad

    class Meta:
        verbose_name = "Detalle de Compra" # Singular
        verbose_name_plural = "Detalles de Compra" # Plural

    def save(self, *args, **kwargs):
        # 1. CÁLCULO DEL SUBTOTAL
        self.subtotal = Decimal(self.cantidad) * self.precio_unitario

        # 2. GESTIÓN DEL INVENTARIO
        if self.pk:
            diferencia = self.cantidad - (self._cantidad_original if self._cantidad_original is not None else 0)
            self.producto.stock += diferencia
            self.producto.save(update_fields=['stock'])
            
            InventarioMovimiento.objects.create(
                producto=self.producto, 
                tipo='Entrada', 
                cantidad=abs(diferencia),
                descripcion=f'Compra #{self.compra.id} - {"Modificación" if diferencia != 0 else "Actualización"}'
            )
        else:
            self.producto.stock += self.cantidad
            self.producto.save(update_fields=['stock'])
            
            InventarioMovimiento.objects.create(
                producto=self.producto, 
                tipo='Entrada', 
                cantidad=self.cantidad,
                descripcion=f'Compra #{self.compra.id} - Nueva Compra'
            )

        super().save(*args, **kwargs)
        
        # 3. RECALCULAR EL TOTAL DE LA COMPRA PADRE
        if self.compra:
            self.compra.save()

    # Lógica para deshacer el movimiento si se borra la línea de detalle
    def delete(self, *args, **kwargs):
        self.producto.stock -= self.cantidad
        self.producto.save(update_fields=['stock'])
        InventarioMovimiento.objects.create(
            producto=self.producto, 
            tipo='Salida', 
            cantidad=self.cantidad,
            descripcion=f'Compra #{self.compra.id} - Eliminación de Detalle'
        )
        super().delete(*args, **kwargs)
            
    def __str__(self):
        return f'{self.producto.nombre} x{self.cantidad}'
        
# ====================================================================
# TABLA 10: Movimiento de Inventario
# ====================================================================
class InventarioMovimiento(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=[('Entrada', 'Entrada'), ('Salida', 'Salida')])
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Movimientos de Inventario" # CORREGIDO

    def __str__(self):
        return f'{self.tipo} - {self.producto.nombre} ({self.cantidad})'

# ====================================================================
# TABLA 11: Método de Pago
# ====================================================================
class MetodoPago(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    
    class Meta:
        verbose_name_plural = "Métodos de Pago" # CORREGIDO

    def __str__(self):
        return self.nombre

# ====================================================================
# TABLA 12: Pago de Venta
# ====================================================================
class PagoVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.PROTECT)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Pagos de Venta" # CORREGIDO

    def __str__(self):
        return f'Pago #{self.id} - Venta {self.venta.id}'