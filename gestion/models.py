from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import JSONField # Importación necesaria para el campo de Auditoría
from django.conf import settings

# ====================================================================
# PARTE A: TABLAS BASE Y CATÁLOGOS (Tablas 1 - 8)
# ====================================================================

# TABLA 1: Cliente
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


# TABLA 2: Proveedor
class Proveedor(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    contacto = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    email = models.EmailField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Proveedores"

    def __str__(self):
        return self.nombre


# TABLA 3: Empleado
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


# TABLA 4: Perfil de Usuario (Relaciona el usuario de Django con un Empleado)
class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    empleado = models.OneToOneField(Empleado, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Perfiles de Usuario"

    def __str__(self):
        return f'Perfil de {self.user.username}'


# TABLA 5: Categoría de Producto
class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categorías de Productos"

    def __str__(self):
        return self.nombre


# TABLA 20: Marca (Definida antes de Producto para evitar problemas de referencia circular)
class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    
    class Meta:
        verbose_name_plural = "Marcas"

    def __str__(self):
        return self.nombre


# TABLA 6: Producto

class Producto(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2) # <--- Precio de VENTA
    
    precio_compra = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name="Precio de Compra/Costo"
    )

    stock = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=5, verbose_name="Stock Mínimo de Alerta")
    # --- Relaciones ---
    proveedor = models.ForeignKey('Proveedor', on_delete=models.SET_NULL, null=True)
    categoria = models.ForeignKey('CategoriaProducto', on_delete=models.SET_NULL, null=True)
    marca = models.ForeignKey('Marca', on_delete=models.SET_NULL, null=True, blank=True)
    # ------------------

    class Meta:
        verbose_name_plural = "Productos"

    def __str__(self):
        return self.nombre


# TABLA 7: Método de Pago
class MetodoPago(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    
    class Meta:
        verbose_name_plural = "Métodos de Pago"

    def __str__(self):
        return self.nombre


# TABLA 8: Movimiento de Inventario (Registro de entradas y salidas de stock)
class InventarioMovimiento(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=[('Entrada', 'Entrada'), ('Salida', 'Salida')])
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Movimientos de Inventario"

    def __str__(self):
        return f'{self.tipo} - {self.producto.nombre} ({self.cantidad})'


# ====================================================================
# PARTE B: MOVIMIENTOS Y PROCESOS PRINCIPALES (Tablas 9 - 19)
# ====================================================================

# --- VENTA ---

# TABLA 9: Venta (Cabecera)
class Venta(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    empleado = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=50, default='Pendiente')

    class Meta:
        verbose_name_plural = "Ventas"

    def __str__(self):
        return f'Venta #{self.id} ({self.fecha.strftime("%Y-%m-%d")})'


# TABLA 10: Detalle de Venta
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
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Venta"

    def save(self, *args, **kwargs):
        # CÁLCULO DEL SUBTOTAL
        self.subtotal = Decimal(self.cantidad) * self.precio_unitario
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f'{self.producto.nombre} x{self.cantidad}'


# TABLA 11: Pago de Venta (Registro de cobro de una venta)
class PagoVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.PROTECT)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Pagos de Venta"

    def __str__(self):
        return f'Pago #{self.id} - Venta {self.venta.id}'


# --- COMPRA ---

# TABLA 12: Compra (Cabecera)
class Compra(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)
    empleado = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=50, default='Pendiente')

    class Meta:
        verbose_name_plural = "Compras"

    def __str__(self):
        return f'Compra #{self.id} ({self.fecha.strftime("%Y-%m-%d")})'


# TABLA 13: Detalle de Compra
class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    #  CAMBIO DE NOMBRE: Ahora es consistente con la vista y el HTML
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2) 
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    _cantidad_original = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.pk:
            self._cantidad_original = self.cantidad

    class Meta:
        verbose_name = "Detalle de Compra"
        verbose_name_plural = "Detalles de Compra"

    def save(self, *args, **kwargs):
        #  CÁLCULO ACTUALIZADO: Usa el nuevo nombre 'precio_compra'
        self.subtotal = Decimal(self.cantidad) * self.precio_compra 
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f'{self.producto.nombre} x{self.cantidad}'


# --- PEDIDO DE CLIENTE ---

# TABLA 14: Pedido de Cliente (Cabecera)
class PedidoCliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    empleado = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    fecha_entrega_estimada = models.DateField(null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=50, default='Pendiente', choices=[('Pendiente', 'Pendiente'), ('Completado', 'Completado'), ('Cancelado', 'Cancelado')])

    class Meta:
        verbose_name_plural = "Pedidos de Clientes"

    def __str__(self):
        return f'Pedido #{self.id} de {self.cliente.nombre}'


# TABLA 15: Detalle de Pedido de Cliente
class PedidoClienteDetalle(models.Model):
    pedido = models.ForeignKey(PedidoCliente, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name_plural = "Detalles de Pedido de Cliente"
        
    def save(self, *args, **kwargs):
        # CÁLCULO DEL SUBTOTAL
        self.subtotal = Decimal(self.cantidad) * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.producto.nombre} x{self.cantidad}'


# --- ORDEN DE COMPRA ---

# TABLA 16: Orden de Compra (Cabecera)
class OrdenDeCompra(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)
    empleado = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_orden = models.DateTimeField(auto_now_add=True)
    fecha_entrega_estimada = models.DateField(null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=50, default='Pendiente', choices=[('Pendiente', 'Pendiente'), ('Recibida', 'Recibida'), ('Cancelada', 'Cancelada')])

    class Meta:
        verbose_name_plural = "Órdenes de Compra"

    def __str__(self):
        return f'OC #{self.id} a {self.proveedor.nombre}'


# TABLA 17: Detalle de Orden de Compra
class OrdenDeCompraDetalle(models.Model):
    orden = models.ForeignKey(OrdenDeCompra, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name_plural = "Detalles de Orden de Compra"
        
    def save(self, *args, **kwargs):
        self.subtotal = Decimal(self.cantidad) * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.producto.nombre} x{self.cantidad}'


# --- PRESUPUESTO ---

# TABLA 18: Presupuesto (Cabecera)
class Presupuesto(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    empleado = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_validez = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=50, default='Pendiente', choices=[('Pendiente', 'Pendiente'), ('Aceptado', 'Aceptado'), ('Rechazado', 'Rechazado')])

    class Meta:
        verbose_name_plural = "Presupuestos"

    def __str__(self):
        return f'Presupuesto #{self.id} para {self.cliente.nombre}'


# TABLA 19: Detalle de Presupuesto
class PresupuestoDetalle(models.Model):
    presupuesto = models.ForeignKey(Presupuesto, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name_plural = "Detalles de Presupuesto"
        
    def save(self, *args, **kwargs):
        self.subtotal = Decimal(self.cantidad) * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.producto.nombre} x{self.cantidad}'


# ====================================================================
# PARTE C: TABLAS DE SOPORTE Y CATÁLOGOS ADICIONALES (Tablas 20 - 30)
# ====================================================================

# ----------------- Catálogos de Producto y Ubicación -----------------

# TABLA 21: Moneda
class Moneda(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    simbolo = models.CharField(max_length=5)
    tipo_cambio = models.DecimalField(max_digits=10, decimal_places=4, default=1.0) # Respecto a la moneda base
    
    class Meta:
        verbose_name_plural = "Monedas"

    def __str__(self):
        return f'{self.nombre} ({self.simbolo})'
        
# TABLA 22: Departamento
class Departamento(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    
    class Meta:
        verbose_name_plural = "Departamentos"

    def __str__(self):
        return self.nombre

# TABLA 23: Ciudad
class Ciudad(models.Model):
    nombre = models.CharField(max_length=100)
    departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT)
    
    class Meta:
        verbose_name_plural = "Ciudades"
        unique_together = ('nombre', 'departamento') # Una ciudad debe ser única dentro de un departamento

    def __str__(self):
        return f'{self.nombre}, {self.departamento.nombre}'
        
# ----------------- Tablas de Contabilidad y Caja -----------------

# TABLA 24: Caja
class Caja(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    empleado_responsable = models.ForeignKey(Empleado, on_delete=models.PROTECT)
    monto_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_apertura = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, default='Abierta', choices=[('Abierta', 'Abierta'), ('Cerrada', 'Cerrada')])
    
    class Meta:
        verbose_name_plural = "Cajas"

    def __str__(self):
        return f'Caja {self.nombre} ({self.estado})'

# TABLA 25: Arqueo
class Arqueo(models.Model):
    caja = models.ForeignKey(Caja, on_delete=models.PROTECT)
    empleado = models.ForeignKey(Empleado, on_delete=models.PROTECT)
    fecha_arqueo = models.DateTimeField(auto_now_add=True)
    monto_contado = models.DecimalField(max_digits=10, decimal_places=2)
    monto_sistema = models.DecimalField(max_digits=10, decimal_places=2)
    diferencia = models.DecimalField(max_digits=10, decimal_places=2, default=0) # Calculado: contado - sistema
    observaciones = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Arqueos"

    def __str__(self):
        return f'Arqueo de {self.caja.nombre} en {self.fecha_arqueo.strftime("%Y-%m-%d")}'


# ----------------- Cuentas a Cobrar / Pagar y Pagos Detallados -----------------

# TABLA 26: Cuenta por Cobrar
class CuentaACobrar(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    venta = models.ForeignKey(Venta, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_vencimiento = models.DateField()
    monto_original = models.DecimalField(max_digits=10, decimal_places=2)
    monto_pendiente = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=50, default='Pendiente', choices=[('Pendiente', 'Pendiente'), ('Pagada', 'Pagada'), ('Vencida', 'Vencida')])

    class Meta:
        verbose_name = "Cuenta por Cobrar"
        verbose_name_plural = "Cuentas por Cobrar"

    def __str__(self):
        return f'CxC #{self.id} de {self.cliente.nombre}'

# TABLA 27: Cuenta por Pagar
class CuentaAPagar(models.Model):
    proveedor = models.ForeignKey('Proveedor', on_delete=models.PROTECT)
    compra = models.ForeignKey('Compra', on_delete=models.SET_NULL, null=True, blank=True)
    fecha_vencimiento = models.DateField()
    monto_original = models.DecimalField(max_digits=10, decimal_places=2)
    monto_pendiente = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=50, default='Pendiente', choices=[('Pendiente', 'Pendiente'), ('Pagada', 'Pagada'), ('Vencida', 'Vencida')])

    class Meta:
        verbose_name = "Cuenta por Pagar"
        verbose_name_plural = "Cuentas por Pagar"

    def __str__(self):
        return f'CxP #{self.id} a {self.proveedor.nombre}'


# TABLA 28: Cobro
class Cobro(models.Model):
    cliente = models.ForeignKey('Cliente', on_delete=models.PROTECT)
    fecha_cobro = models.DateTimeField(auto_now_add=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    moneda = models.ForeignKey('Moneda', on_delete=models.PROTECT)
    caja = models.ForeignKey('Caja', on_delete=models.PROTECT, null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Cobros"

    def __str__(self):
        return f'Cobro #{self.id} de {self.cliente.nombre}'


# TABLA 29: Cobro Detalle
class CobroDetalle(models.Model):
    cobro = models.ForeignKey('Cobro', on_delete=models.CASCADE)
    cuenta_a_cobrar = models.ForeignKey('CuentaACobrar', on_delete=models.PROTECT)
    monto_aplicado = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name_plural = "Detalles de Cobro"

    def __str__(self):
        return f'Cobro {self.cobro.id} aplica {self.monto_aplicado}'


# TABLA 30: Auditoría
class Auditoria(models.Model):
    # CORRECCIÓN CLAVE: Usar settings.AUTH_USER_MODEL para referenciar el modelo de usuario estándar de Django.
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True) 
    
    fecha_hora = models.DateTimeField(auto_now_add=True)
    accion = models.CharField(max_length=50) # Ejemplo: Crear, Modificar, Eliminar
    modelo_afectado = models.CharField(max_length=100)
    registro_id = models.IntegerField()
    datos_anteriores = models.JSONField(null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Auditoría"

    def __str__(self):
        return f'{self.accion} en {self.modelo_afectado} por {self.usuario}'

# ====================================================================
# PARTE D: TABLAS COMPLEMENTARIAS Y DERIVADAS (Tablas 31 - 44)
# ====================================================================

# ----------------- Pagos y Devoluciones -----------------

# TABLA 31: Orden de Pago (corresponde a 'orden_de_pago')
class OrdenDePago(models.Model):
    proveedor = models.ForeignKey('Proveedor', on_delete=models.PROTECT)
    fecha_orden = models.DateTimeField(auto_now_add=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    moneda = models.ForeignKey('Moneda', on_delete=models.PROTECT)
    empleado = models.ForeignKey('Empleado', on_delete=models.SET_NULL, null=True)
    estado = models.CharField(max_length=50, default='Pendiente', choices=[('Pendiente', 'Pendiente'), ('Pagada', 'Pagada'), ('Anulada', 'Anulada')])

    class Meta:
        verbose_name_plural = "Órdenes de Pago"

    def __str__(self):
        return f'OP #{self.id} a {self.proveedor.nombre}'

# TABLA 32: Detalle de Orden de Pago (corresponde a 'orden_de_pago_detalle')
class OrdenDePagoDetalle(models.Model):
    orden_pago = models.ForeignKey(OrdenDePago, on_delete=models.CASCADE)
    cuenta_a_pagar = models.ForeignKey('CuentaAPagar', on_delete=models.PROTECT)
    monto_aplicado = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name_plural = "Detalles de Orden de Pago"

    def __str__(self):
        return f'OP {self.orden_pago.id} aplica a CxP {self.cuenta_a_pagar.id}'
# TABLA 33: Devolución a Proveedor (corresponde a 'devolucion_a_proveedor')
class DevolucionAProveedor(models.Model):
    proveedor = models.ForeignKey('Proveedor', on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)
    compra_original = models.ForeignKey('Compra', on_delete=models.SET_NULL, null=True, blank=True)
    # Cambiado a 'total' para coincidir con la vista 'views_finanzas.py'
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Total Devuelto') 

    estado = models.CharField(
        max_length=10,
        # CORREGIDO: Usar 'PROCESADA' en lugar de 'COMPLETADO' para coincidir con views_finanzas.py
        choices=[('PENDIENTE', 'Pendiente'), ('PROCESADA', 'Procesada'), ('ANULADA', 'Anulada')],
        default='PENDIENTE', 
        verbose_name='Estado'
    )
    # Se recomienda añadir un campo de motivo para trazabilidad
    motivo = models.TextField(max_length=500, blank=True, verbose_name='Motivo') 

    class Meta:
        verbose_name_plural = "Devoluciones a Proveedores"
        ordering = ['-fecha'] # Añadido para mejor listado

    def __str__(self):
        return f'Devolución #{self.id} a {self.proveedor.nombre}'

# TABLA 34: Detalle de Devolución a Proveedor (corresponde a 'devo_prov_deta')
class DevolucionAProveedorDetalle(models.Model):
    devolucion = models.ForeignKey(DevolucionAProveedor, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey('Producto', on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    precio_devuelto = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        # Aseguramos el cálculo del subtotal con Decimal para precisión
        self.subtotal = Decimal(self.cantidad) * self.precio_devuelto
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Detalles de Devolución a Proveedor"
        # Añadida restricción para evitar duplicados en la misma devolución
        unique_together = ('devolucion', 'producto')

    def __str__(self):
        return f'{self.producto.nombre} x{self.cantidad}'
# ----------------- Pedido a Proveedor y Tablas Intermedias -----------------

# TABLA 35: Pedido a Proveedor (Cabecera) (corresponde a 'pedido_a_proveedor')
class PedidoAProveedor(models.Model):
    proveedor = models.ForeignKey('Proveedor', on_delete=models.PROTECT)
    empleado = models.ForeignKey('Empleado', on_delete=models.SET_NULL, null=True, blank=True)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    fecha_recepcion_estimada = models.DateField(null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=50, default='Pendiente', choices=[('Pendiente', 'Pendiente'), ('Recibido', 'Recibido'), ('Cancelado', 'Cancelado')])

    class Meta:
        verbose_name_plural = "Pedidos a Proveedores"

    def __str__(self):
        return f'PdP #{self.id} a {self.proveedor.nombre}'

# TABLA 36: Detalle de Pedido a Proveedor (corresponde a 'pedodo_a_proveedor_detalle')
class PedidoAProveedorDetalle(models.Model):
    pedido = models.ForeignKey(PedidoAProveedor, on_delete=models.CASCADE)
    producto = models.ForeignKey('Producto', on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    precio_acordado = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        # Es necesario importar Decimal de la librería decimal: from decimal import Decimal
        self.subtotal = Decimal(self.cantidad) * self.precio_acordado
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Detalles de Pedido a Proveedor"

    def __str__(self):
        return f'{self.producto.nombre} x{self.cantidad}'

# TABLA 37: Cotización (corresponde a 'cotización')
class Cotizacion(models.Model):
    cliente = models.ForeignKey('Cliente', on_delete=models.PROTECT)
    empleado = models.ForeignKey('Empleado', on_delete=models.SET_NULL, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_validez = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=50, default='Abierta', choices=[('Abierta', 'Abierta'), ('Aceptada', 'Aceptada'), ('Rechazada', 'Rechazada')])

    class Meta:
        verbose_name_plural = "Cotizaciones"

    def __str__(self):
        return f'Cotización #{self.id} para {self.cliente.nombre}'

# TABLA 38: Detalle de Cotización (no estaba en la lista, pero es necesaria)
class CotizacionDetalle(models.Model):
    cotizacion = models.ForeignKey(Cotizacion, on_delete=models.CASCADE)
    producto = models.ForeignKey('Producto', on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        # Es necesario importar Decimal de la librería decimal: from decimal import Decimal
        self.subtotal = Decimal(self.cantidad) * self.precio_unitario
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Detalles de Cotización"

    def __str__(self):
        return f'{self.producto.nombre} x{self.cantidad}'

# TABLA 39: Cobro de Cotización (corresponde a 'cobro_cotiza')
class CobroCotizacion(models.Model):
    cotizacion = models.ForeignKey(Cotizacion, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.ForeignKey('MetodoPago', on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Cobros de Cotización"

    def __str__(self):
        return f'Cobro Cotiza #{self.cotizacion.id}'

# TABLA 40: Tabla Intermedia Presupuesto/Pedido (corresponde a 'presu_pedi')
class PresupuestoPedido(models.Model):
    presupuesto = models.ForeignKey('Presupuesto', on_delete=models.CASCADE)
    pedido = models.ForeignKey('PedidoCliente', on_delete=models.CASCADE)
    fecha_relacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Relación Presupuesto-Pedido"
        verbose_name_plural = "Relaciones Presupuesto-Pedido"
        unique_together = ('presupuesto', 'pedido')

    def __str__(self):
        return f'Presu {self.presupuesto.id} -> Pedido {self.pedido.id}'


# ----------------- Ajustes e Inventario -----------------

# TABLA 41: Tipo de Ajuste (corresponde a 'ajustes_tipo')
class AjusteTipo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    es_entrada = models.BooleanField(default=True) # True = Suma stock, False = Resta stock
    
    class Meta:
        verbose_name_plural = "Tipos de Ajuste de Inventario"

    def __str__(self):
        return self.nombre
        
# TABLA 42: Ajustes de Inventario (Cabecera) - CORREGIDO
class Ajuste(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    empleado = models.ForeignKey('Empleado', on_delete=models.PROTECT)
    
    # AÑADIDO: El tipo debe ir en la cabecera (Todo el Ajuste es Entrada O Salida)
    tipo_ajuste = models.ForeignKey('AjusteTipo', on_delete=models.PROTECT, 
                                    verbose_name="Tipo de Ajuste General") 
    
    motivo = models.TextField(verbose_name="Motivo General")
    # AÑADIDO: Campo para gestionar si el ajuste ya fue aplicado o no.
    estado = models.CharField(max_length=50, default='Pendiente', 
                              choices=[('Pendiente', 'Pendiente'), ('PROCESADO', 'PROCESADO')])

    class Meta:
        verbose_name_plural = "Ajustes de Inventario"

    def __str__(self):
        return f'Ajuste #{self.id} ({self.fecha.strftime("%Y-%m-%d")}) - {self.tipo_ajuste.nombre}'

# TABLA 43: Detalle de Ajuste - CORREGIDO
class AjusteDetalle(models.Model):
    ajuste = models.ForeignKey(Ajuste, on_delete=models.CASCADE)
    producto = models.ForeignKey('Producto', on_delete=models.PROTECT)
    
    # ELIMINADO: Ya no necesita el tipo, lo hereda de la cabecera 'Ajuste'.
    # tipo_ajuste = models.ForeignKey(AjusteTipo, on_delete=models.PROTECT)
    
    cantidad = models.IntegerField()
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Detalles de Ajuste"

    def __str__(self):
        # Ahora accede al tipo a través de la relación de la cabecera
        return f'{self.ajuste.tipo_ajuste.nombre} de {self.producto.nombre} x{self.cantidad}'


# TABLA 44: Tabla Intermedia PedidoCliente/Venta (corresponde a 'pedidoclienteventa')
class PedidoClienteVenta(models.Model):
    pedido = models.ForeignKey('PedidoCliente', on_delete=models.PROTECT)
    venta = models.ForeignKey('Venta', on_delete=models.PROTECT)
    fecha_relacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Relación Pedido-Venta"
        verbose_name_plural = "Relaciones Pedido-Venta"
        unique_together = ('pedido', 'venta')

    def __str__(self):
        return f'Pedido {self.pedido.id} -> Venta {self.venta.id}'

# ====================================================================
# SEÑALES Lógica de Inventario y Totales
# ====================================================================

# ----------------- VENTA (DetalleVenta) -----------------

# ¡CORRECCIÓN AQUÍ! Cambiar sender='DetalleVenta' a sender='gestion.DetalleVenta'
@receiver(post_save, sender='gestion.DetalleVenta')
def actualizar_stock_y_total_venta(sender, instance, created, **kwargs):
    # ... (el resto de la función es correcto)
    producto = instance.producto
    venta = instance.venta
    
    # --- Lógica de Stock e Inventario ---
    if created:
        producto.stock -= instance.cantidad
        tipo_movimiento = 'Salida'
        descripcion = f'Venta #{venta.id} - Nueva Venta'
        diferencia_movimiento = instance.cantidad
    else:
        try:
            original = sender.objects.get(pk=instance.pk)
            diferencia = instance.cantidad - original.cantidad
        except sender.DoesNotExist:
            diferencia = 0

        if diferencia != 0:
            producto.stock -= diferencia
            tipo_movimiento = 'Salida' if diferencia > 0 else 'Entrada'
            descripcion = f'Venta #{venta.id} - Modificación de Detalle'
            diferencia_movimiento = abs(diferencia)
        else:
            tipo_movimiento = None

    if tipo_movimiento:
        InventarioMovimiento.objects.create(
            producto=producto,
            tipo=tipo_movimiento,
            cantidad=diferencia_movimiento,
            descripcion=descripcion
        )

    producto.save(update_fields=['stock'])

    # --- Lógica de Total de Venta (CORRECCIÓN CLAVE) ---
    venta.total = sum(d.subtotal for d in venta.detalleventa_set.all())
    venta.save(update_fields=['total'])


# ¡CORRECCIÓN AQUÍ! Cambiar sender='DetalleVenta' a sender='gestion.DetalleVenta'
@receiver(post_delete, sender='gestion.DetalleVenta')
def devolver_stock_y_total_venta(sender, instance, **kwargs):
    # ... (el resto de la función es correcto)
    producto = instance.producto
    venta = instance.venta

    producto.stock += instance.cantidad
    producto.save(update_fields=['stock'])

    InventarioMovimiento.objects.create(
        producto=producto,
        tipo='Entrada',
        cantidad=instance.cantidad,
        descripcion=f'Venta #{venta.id} - Eliminación de Detalle'
    )

    # --- Lógica de Total de Venta (CORRECCIÓN CLAVE) ---
    venta.total = sum(d.subtotal for d in venta.detalleventa_set.all())
    venta.save(update_fields=['total'])


# ----------------- COMPRA (DetalleCompra) -----------------

# ¡CORRECCIÓN AQUÍ! Cambiar sender='DetalleCompra' a sender='gestion.DetalleCompra'
@receiver(post_save, sender='gestion.DetalleCompra')
def actualizar_stock_y_total_compra(sender, instance, created, **kwargs):
    # ... (el resto de la función es correcto)
    producto = instance.producto
    compra = instance.compra

    # --- Lógica de Stock e Inventario ---
    if created:
        producto.stock += instance.cantidad
        tipo_movimiento = 'Entrada'
        descripcion = f'Compra #{compra.id} - Nueva Compra'
        diferencia_movimiento = instance.cantidad
    else:
        try:
            original = sender.objects.get(pk=instance.pk)
            diferencia = instance.cantidad - original.cantidad
        except sender.DoesNotExist:
            diferencia = 0

        if diferencia != 0:
            producto.stock += diferencia
            tipo_movimiento = 'Entrada' if diferencia > 0 else 'Salida'
            descripcion = f'Compra #{compra.id} - Modificación de Detalle'
            diferencia_movimiento = abs(diferencia)
        else:
            tipo_movimiento = None

    if tipo_movimiento:
        InventarioMovimiento.objects.create(
            producto=producto,
            tipo=tipo_movimiento,
            cantidad=diferencia_movimiento,
            descripcion=descripcion
        )

    producto.save(update_fields=['stock'])

    # --- Lógica de Total de Compra (CORRECCIÓN CLAVE) ---
    compra.total = sum(d.subtotal for d in compra.detallecompra_set.all())
    compra.save(update_fields=['total'])


# ¡CORRECCIÓN AQUÍ! Cambiar sender='DetalleCompra' a sender='gestion.DetalleCompra'
@receiver(post_delete, sender='gestion.DetalleCompra')
def ajustar_stock_y_total_compra_eliminacion(sender, instance, **kwargs):
    # ... (el resto de la función es correcto)
    producto = instance.producto
    compra = instance.compra

    producto.stock -= instance.cantidad
    producto.save(update_fields=['stock'])

    InventarioMovimiento.objects.create(
        producto=producto,
        tipo='Salida',
        cantidad=instance.cantidad,
        descripcion=f'Compra #{compra.id} - Eliminación de Detalle'
    )

    # --- Lógica de Total de Compra (CORRECCIÓN CLAVE) ---
    compra.total = sum(d.subtotal for d in compra.detallecompra_set.all())
    compra.save(update_fields=['total'])


# ----------------- AJUSTES DE INVENTARIO (AjusteDetalle) -----------------

# ¡CORRECCIÓN AQUÍ! Cambiar sender='AjusteDetalle' a sender='gestion.AjusteDetalle'
@receiver(post_save, sender='gestion.AjusteDetalle')
def actualizar_stock_por_ajuste(sender, instance, created, **kwargs):
    # ... (el resto de la función es correcto)
    producto = instance.producto
    ajuste = instance.ajuste
    
    tipo_ajuste = instance.ajuste.tipo_ajuste

    cantidad_ajuste = instance.cantidad
    tipo_movimiento = 'Entrada' if tipo_ajuste.es_entrada else 'Salida'

    if tipo_ajuste.es_entrada:
        producto.stock += cantidad_ajuste
    else:
        producto.stock -= cantidad_ajuste

    InventarioMovimiento.objects.create(
        producto=producto,
        tipo=tipo_movimiento,
        cantidad=cantidad_ajuste,
        descripcion=f'Ajuste #{ajuste.id} - Tipo: {tipo_ajuste.nombre}'
    )
    producto.save(update_fields=['stock'])
