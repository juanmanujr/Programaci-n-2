from django.contrib import admin
from .models import (
    Cliente, Proveedor, Empleado, CategoriaProducto, Producto,
    Venta, DetalleVenta, Compra, DetalleCompra,
    InventarioMovimiento, MetodoPago, PagoVenta
)

# ====================================================================
# INLINES (Detalles dentro de la Cabecera)
# ====================================================================
class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    # Nombres limpios:
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')
    # Subtotal es de sólo lectura porque se calcula automáticamente
    readonly_fields = ('subtotal',)
    extra = 1

class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    # Nombres limpios:
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')
    # Subtotal es de sólo lectura porque se calcula automáticamente
    readonly_fields = ('subtotal',)
    extra = 1


# ====================================================================
# ADMINS PERSONALIZADOS
# ====================================================================

# Admin de Venta
@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    # Campos que se ven en la lista de ventas:
    list_display = ('id', 'cliente', 'empleado', 'total', 'estado', 'fecha')
    # Campos por los que se puede filtrar:
    list_filter = ('estado', 'fecha', 'empleado')
    # Campos por los que se puede buscar:
    search_fields = ('cliente__nombre', 'cliente__apellido', 'id')
    # DetalleVenta aparece dentro del formulario:
    inlines = [DetalleVentaInline]
    # El total es de sólo lectura porque se calcula automáticamente
    readonly_fields = ('total',)


# Admin de Compra
@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    # Campos que se ven en la lista de compras:
    list_display = ('id', 'proveedor', 'empleado', 'total', 'estado', 'fecha')
    # Campos por los que se puede filtrar:
    list_filter = ('estado', 'fecha', 'proveedor')
    # DetalleCompra aparece dentro del formulario:
    inlines = [DetalleCompraInline]
    # El total es de sólo lectura porque se calcula automáticamente
    readonly_fields = ('total',)


# Admin de Producto (personalizado para ver stock)
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'categoria', 'proveedor')
    list_filter = ('categoria', 'proveedor', 'stock')
    search_fields = ('nombre',)
    # Hacer que el stock sea de sólo lectura, ya que lo maneja la lógica de compra/venta
    readonly_fields = ('stock',)


# ====================================================================
# REGISTRO SIMPLE DE OTRAS TABLAS
# ====================================================================

admin.site.register(Cliente)
admin.site.register(Proveedor)
admin.site.register(Empleado)
admin.site.register(CategoriaProducto)
admin.site.register(InventarioMovimiento)
admin.site.register(MetodoPago)
admin.site.register(PagoVenta)

# Ocultar DetalleVenta y DetalleCompra del menú principal, ya que se acceden vía Inlines
class OcultarAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
        
admin.site.register(DetalleVenta, OcultarAdmin)
admin.site.register(DetalleCompra, OcultarAdmin)