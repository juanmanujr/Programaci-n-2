from django.contrib import admin
from .models import (
    # PARTE A: TABLAS BASE Y CATÁLOGOS (1-8)
    Cliente, Proveedor, Empleado, PerfilUsuario, CategoriaProducto, Producto,
    MetodoPago, InventarioMovimiento,

    # PARTE B: MOVIMIENTOS Y PROCESOS PRINCIPALES (9-19)
    Venta, DetalleVenta, PagoVenta, Compra, DetalleCompra, PedidoCliente,
    PedidoClienteDetalle, OrdenDeCompra, OrdenDeCompraDetalle, Presupuesto,
    PresupuestoDetalle,

    # PARTE C: TABLAS DE SOPORTE Y CATÁLOGOS ADICIONALES (20-30)
    Marca, Moneda, Departamento, Ciudad, Caja, Arqueo, CuentaACobrar,
    CuentaAPagar, Cobro, CobroDetalle, Auditoria,

    # PARTE D: TABLAS COMPLEMENTARIAS Y DERIVADAS (31-44)
    OrdenDePago, OrdenDePagoDetalle, DevolucionAProveedor, DevolucionAProveedorDetalle,
    PedidoAProveedor, PedidoAProveedorDetalle, Cotizacion, CotizacionDetalle,
    CobroCotizacion, PresupuestoPedido, AjusteTipo, Ajuste, AjusteDetalle,
    PedidoClienteVenta
)

# ====================================================================
# CONFIGURACIONES INLINE (Para formularios anidados en el Admin)
# ====================================================================

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    raw_id_fields = ['producto']
    readonly_fields = ('subtotal',)

class PagoVentaInline(admin.TabularInline):
    model = PagoVenta
    extra = 1

class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 0
    raw_id_fields = ['producto']
    readonly_fields = ('subtotal',)

class PedidoClienteDetalleInline(admin.TabularInline):
    model = PedidoClienteDetalle
    extra = 0
    raw_id_fields = ['producto']
    readonly_fields = ('subtotal',)

class OrdenDeCompraDetalleInline(admin.TabularInline):
    model = OrdenDeCompraDetalle
    extra = 0
    raw_id_fields = ['producto']
    readonly_fields = ('subtotal',)

class PresupuestoDetalleInline(admin.TabularInline):
    model = PresupuestoDetalle
    extra = 0
    raw_id_fields = ['producto']
    readonly_fields = ('subtotal',)

class AjusteDetalleInline(admin.TabularInline):
    model = AjusteDetalle
    extra = 0
    raw_id_fields = ['producto']

class CobroDetalleInline(admin.TabularInline):
    model = CobroDetalle
    extra = 0

class OrdenDePagoDetalleInline(admin.TabularInline):
    model = OrdenDePagoDetalle
    extra = 0

class DevolucionAProveedorDetalleInline(admin.TabularInline):
    model = DevolucionAProveedorDetalle
    extra = 0

class PedidoAProveedorDetalleInline(admin.TabularInline):
    model = PedidoAProveedorDetalle
    extra = 0

class CotizacionDetalleInline(admin.TabularInline):
    model = CotizacionDetalle
    extra = 0

# ====================================================================
# PARTE A: TABLAS BASE Y CATÁLOGOS (Admin Models)
# ====================================================================

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'email', 'telefono', 'fecha_registro')
    search_fields = ('nombre', 'apellido', 'email')
    list_filter = ('fecha_registro',)

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto', 'telefono', 'email')
    search_fields = ('nombre', 'contacto')

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'cargo', 'fecha_contratacion', 'salario')
    list_filter = ('cargo', 'fecha_contratacion')
    search_fields = ('nombre', 'apellido', 'cargo')

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'empleado')
    search_fields = ('user__username', 'empleado__nombre')

@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'categoria', 'proveedor', 'marca')
    list_filter = ('categoria', 'proveedor', 'marca')
    search_fields = ('nombre', 'descripcion')
    raw_id_fields = ('proveedor', 'categoria', 'marca') # Para campos ForeignKey con muchas opciones

@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(InventarioMovimiento)
class InventarioMovimientoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'tipo', 'cantidad', 'fecha', 'descripcion')
    list_filter = ('tipo', 'fecha')
    search_fields = ('producto__nombre', 'descripcion')
    readonly_fields = ('fecha',)


# ====================================================================
# PARTE B: MOVIMIENTOS Y PROCESOS PRINCIPALES (Admin Models)
# ====================================================================

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'cliente', 'empleado', 'total', 'estado')
    list_filter = ('estado', 'fecha')
    search_fields = ('cliente__nombre', 'empleado__nombre')
    inlines = [DetalleVentaInline, PagoVentaInline]
    readonly_fields = ('total',)
    raw_id_fields = ('cliente', 'empleado')

@admin.register(DetalleVenta)
class DetalleVentaSoloAdmin(admin.ModelAdmin):
    list_display = ('venta', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('venta__fecha',)
    raw_id_fields = ('venta', 'producto')
    readonly_fields = ('subtotal',)

@admin.register(PagoVenta)
class PagoVentaAdmin(admin.ModelAdmin):
    list_display = ('venta', 'metodo_pago', 'monto', 'fecha')
    list_filter = ('metodo_pago', 'fecha')
    raw_id_fields = ('venta',)


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'proveedor', 'empleado', 'total', 'estado')
    list_filter = ('estado', 'fecha')
    search_fields = ('proveedor__nombre', 'empleado__nombre')
    inlines = [DetalleCompraInline]
    readonly_fields = ('total',)
    raw_id_fields = ('proveedor', 'empleado')

@admin.register(PedidoCliente)
class PedidoClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha_pedido', 'fecha_entrega_estimada', 'total', 'estado')
    list_filter = ('estado', 'fecha_pedido')
    inlines = [PedidoClienteDetalleInline]
    readonly_fields = ('total',)
    raw_id_fields = ('cliente', 'empleado')

@admin.register(OrdenDeCompra)
class OrdenDeCompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'fecha_orden', 'fecha_entrega_estimada', 'total', 'estado')
    list_filter = ('estado', 'fecha_orden')
    inlines = [OrdenDeCompraDetalleInline]
    readonly_fields = ('total',)
    raw_id_fields = ('proveedor', 'empleado')

@admin.register(Presupuesto)
class PresupuestoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha_creacion', 'fecha_validez', 'total', 'estado')
    list_filter = ('estado', 'fecha_creacion')
    inlines = [PresupuestoDetalleInline]
    readonly_fields = ('total',)
    raw_id_fields = ('cliente', 'empleado')

# El resto de DetalleCompra, DetallePedido, DetalleOrdenCompra, DetallePresupuesto se dejan como inlines o si se necesitan solas:
admin.site.register(DetalleCompra)
admin.site.register(PedidoClienteDetalle)
admin.site.register(OrdenDeCompraDetalle)
admin.site.register(PresupuestoDetalle)


# ====================================================================
# PARTE C: TABLAS DE SOPORTE Y CATÁLOGOS ADICIONALES (Admin Models)
# ====================================================================

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(Moneda)
class MonedaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'simbolo', 'tipo_cambio')

@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(Ciudad)
class CiudadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'departamento')
    list_filter = ('departamento',)

@admin.register(Caja)
class CajaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'empleado_responsable', 'monto_inicial', 'estado', 'fecha_apertura', 'fecha_cierre')
    list_filter = ('estado',)
    raw_id_fields = ('empleado_responsable',)

@admin.register(Arqueo)
class ArqueoAdmin(admin.ModelAdmin):
    list_display = ('caja', 'empleado', 'fecha_arqueo', 'monto_contado', 'monto_sistema', 'diferencia')
    readonly_fields = ('diferencia',)

@admin.register(CuentaACobrar)
class CuentaACobrarAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'venta', 'monto_original', 'monto_pendiente', 'fecha_vencimiento', 'estado')
    list_filter = ('estado', 'fecha_vencimiento')
    raw_id_fields = ('cliente', 'venta')

@admin.register(CuentaAPagar)
class CuentaAPagarAdmin(admin.ModelAdmin):
    list_display = ('proveedor', 'compra', 'monto_original', 'monto_pendiente', 'fecha_vencimiento', 'estado')
    list_filter = ('estado', 'fecha_vencimiento')
    raw_id_fields = ('proveedor', 'compra')

@admin.register(Cobro)
class CobroAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha_cobro', 'monto_total', 'moneda', 'caja')
    inlines = [CobroDetalleInline]
    raw_id_fields = ('cliente', 'caja')
    readonly_fields = ('monto_total',)

@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ('fecha_hora', 'usuario', 'accion', 'modelo_afectado', 'registro_id')
    list_filter = ('accion', 'modelo_afectado')
    search_fields = ('usuario__username', 'modelo_afectado', 'registro_id')
    readonly_fields = ('fecha_hora', 'usuario', 'accion', 'modelo_afectado', 'registro_id', 'datos_anteriores')


# ====================================================================
# PARTE D: TABLAS COMPLEMENTARIAS Y DERIVADAS (Admin Models)
# ====================================================================

@admin.register(OrdenDePago)
class OrdenDePagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'fecha_orden', 'monto_total', 'moneda', 'estado')
    list_filter = ('estado', 'fecha_orden')
    inlines = [OrdenDePagoDetalleInline]
    raw_id_fields = ('proveedor', 'empleado')

@admin.register(DevolucionAProveedor)
class DevolucionAProveedorAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'fecha', 'compra_original', 'total_devuelto')
    inlines = [DevolucionAProveedorDetalleInline]
    raw_id_fields = ('proveedor', 'compra_original')

@admin.register(PedidoAProveedor)
class PedidoAProveedorAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'fecha_pedido', 'fecha_recepcion_estimada', 'total', 'estado')
    list_filter = ('estado',)
    inlines = [PedidoAProveedorDetalleInline]
    raw_id_fields = ('proveedor', 'empleado')

@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha_creacion', 'fecha_validez', 'total', 'estado')
    list_filter = ('estado',)
    inlines = [CotizacionDetalleInline]
    raw_id_fields = ('cliente', 'empleado')
    

@admin.register(Ajuste)
class AjusteAdmin(admin.ModelAdmin):
    # CORRECCIÓN: Usamos 'motivo' para sincronizar con models.py
    list_display = ('id', 'fecha', 'empleado', 'motivo', 'tipo_ajuste', 'estado') # Agregué tipo_ajuste y estado para que sea más informativo
    inlines = [AjusteDetalleInline]
    raw_id_fields = ('empleado',)

@admin.register(AjusteTipo)
class AjusteTipoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'es_entrada')

# Tablas intermedias y de detalle que no son inlines
admin.site.register(CobroDetalle)
admin.site.register(OrdenDePagoDetalle)
admin.site.register(DevolucionAProveedorDetalle)
admin.site.register(PedidoAProveedorDetalle)
admin.site.register(CotizacionDetalle)
admin.site.register(CobroCotizacion)
admin.site.register(PresupuestoPedido)
admin.site.register(AjusteDetalle)
admin.site.register(PedidoClienteVenta)