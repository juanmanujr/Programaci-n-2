from django.urls import path, include
from .views import (
    # Importaciones de vistas del módulo principal (gestion)
    LoginView, LogoutView, 
    dashboard, 

    # Clientes
    ClienteListView, ClienteCreateView, ClienteUpdateView, ClienteDeleteView, 
    
    # Proveedores
    ProveedorCreateView, ProveedorListView, ProveedorUpdateView, ProveedorDeleteView,
    ProveedorDetailView, 
    
    # Productos
    ProductoCreateView, ProductoListView, ProductoUpdateView, ProductoDeleteView, 

    # CATÁLOGOS DE PRODUCTO
    CategoriaProductoListView, CategoriaProductoCreateView, CategoriaProductoUpdateView, CategoriaProductoDeleteView,
    MarcaListView, MarcaCreateView, MarcaUpdateView, MarcaDeleteView,
    
    # Ventas
    VentaCreateView, VentaListView, VentaDetalleView, VentaUpdateView, VentaFinalizarView, VentaDeleteView,
    
    # Compras
    CompraCreateView, CompraListView, 
    CompraUpdateView, CompraDetalleView, CompraFinalizarView, CompraDeleteView, 
    
    # PEDIDOS DE CLIENTE 
    PedidoClienteCreateView, PedidoClienteListView, PedidoClienteDetalleView, PedidoClienteUpdateView, PedidoClienteDeleteView,

    # AJUSTES DE INVENTARIO
    AjusteCreateView, AjusteListView, AjusteDetalleView, AjusteProcesarView, AjusteDeleteView,
)

# ➡️ IMPORTACIÓN DE VISTAS DEL MÓDULO DE FINANZAS
from . import views_finanzas 

urlpatterns = [
    # Rutas básicas
    path('', dashboard, name='dashboard'), 
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Rutas para Clientes
    path('clientes/', ClienteListView.as_view(), name='cliente_lista'),
    path('clientes/nuevo/', ClienteCreateView.as_view(), name='cliente_crear'),
    path('clientes/<int:pk>/editar/', ClienteUpdateView.as_view(), name='cliente_editar'),
    path('clientes/<int:pk>/eliminar/', ClienteDeleteView.as_view(), name='cliente_eliminar'),
    
    # Rutas para Proveedores
    path('proveedores/', ProveedorListView.as_view(), name='proveedor_lista'),
    path('proveedores/nuevo/', ProveedorCreateView.as_view(), name='proveedor_crear'),
    path('proveedores/<int:pk>/', ProveedorDetailView.as_view(), name='proveedor_detalle'),
    path('proveedores/<int:pk>/editar/', ProveedorUpdateView.as_view(), name='proveedor_editar'),
    path('proveedores/<int:pk>/eliminar/', ProveedorDeleteView.as_view(), name='proveedor_eliminar'),
    
    # Rutas para Productos
    path('productos/', ProductoListView.as_view(), name='producto_lista'),
    path('productos/nuevo/', ProductoCreateView.as_view(), name='producto_crear'),
    path('productos/<int:pk>/editar/', ProductoUpdateView.as_view(), name='producto_editar'),
    path('productos/<int:pk>/eliminar/', ProductoDeleteView.as_view(), name='producto_eliminar'),
    
    # Rutas para Catálogos de Producto (Categoría)
    path('categorias/', CategoriaProductoListView.as_view(), name='categoria_lista'),
    path('categorias/nueva/', CategoriaProductoCreateView.as_view(), name='categoria_crear'),
    path('categorias/<int:pk>/editar/', CategoriaProductoUpdateView.as_view(), name='categoria_editar'),
    path('categorias/<int:pk>/eliminar/', CategoriaProductoDeleteView.as_view(), name='categoria_eliminar'),
    
    # Rutas para Catálogos de Producto (Marca)
    path('marcas/', MarcaListView.as_view(), name='marca_lista'),
    path('marcas/nueva/', MarcaCreateView.as_view(), name='marca_crear'),
    path('marcas/<int:pk>/editar/', MarcaUpdateView.as_view(), name='marca_editar'),
    path('marcas/<int:pk>/eliminar/', MarcaDeleteView.as_view(), name='marca_eliminar'),
    
    # Rutas para Ventas
    path('ventas/', VentaListView.as_view(), name='venta_lista'),
    path('ventas/nueva/', VentaCreateView.as_view(), name='venta_crear'),
    path('ventas/<int:pk>/', VentaDetalleView.as_view(), name='venta_detalle'),
    path('ventas/<int:pk>/editar/', VentaUpdateView.as_view(), name='venta_editar'),
    path('ventas/<int:pk>/finalizar/', VentaFinalizarView.as_view(), name='venta_finalizar'),
    path('ventas/<int:pk>/eliminar/', VentaDeleteView.as_view(), name='venta_eliminar'),
    
    # Rutas para Compras
    path('compras/', CompraListView.as_view(), name='compra_lista'),
    path('compras/nueva/', CompraCreateView.as_view(), name='compra_crear'),
    path('compras/<int:pk>/', CompraDetalleView.as_view(), name='compra_detalle'),
    path('compras/<int:pk>/editar/', CompraUpdateView.as_view(), name='compra_editar'),
    path('compras/<int:pk>/finalizar/', CompraFinalizarView.as_view(), name='compra_finalizar'),
    path('compras/<int:pk>/eliminar/', CompraDeleteView.as_view(), name='compra_eliminar'),
    
    # Rutas para Pedidos de Cliente
    path('pedidos/', PedidoClienteListView.as_view(), name='pedido_cliente_lista'),
    path('pedidos/nuevo/', PedidoClienteCreateView.as_view(), name='pedido_cliente_crear'),
    path('pedidos/<int:pk>/', PedidoClienteDetalleView.as_view(), name='pedido_cliente_detalle'),
    path('pedidos/<int:pk>/editar/', PedidoClienteUpdateView.as_view(), name='pedido_cliente_editar'),
    path('pedidos/<int:pk>/eliminar/', PedidoClienteDeleteView.as_view(), name='pedido_cliente_eliminar'),
    
    # ===================================================================
    # AJUSTES DE INVENTARIO
    # ===================================================================
    path('ajustes/', AjusteListView.as_view(), name='ajuste_lista'),
    path('ajustes/nuevo/', AjusteCreateView.as_view(), name='ajuste_nuevo'), 
    path('ajustes/<int:pk>/', AjusteDetalleView.as_view(), name='ajuste_detalle'), 
    path('ajustes/<int:pk>/procesar/', AjusteProcesarView.as_view(), name='ajuste_procesar'),
    path('ajustes/<int:pk>/eliminar/', AjusteDeleteView.as_view(), name='ajuste_eliminar'),
    
    # ===================================================================
    # 💰 MÓDULO DE FINANZAS
    # ===================================================================
    
    # A. ÓRDENES DE COMPRA (OC)
    path('finanzas/ordenes-compra/', views_finanzas.OrdenDeCompraListView.as_view(), name='ordencompra_lista'),
    path('finanzas/ordenes-compra/crear/', views_finanzas.OrdenDeCompraCreateView.as_view(), name='ordencompra_crear'),
    path('finanzas/ordenes-compra/<int:pk>/', views_finanzas.OrdenDeCompraDetailView.as_view(), name='ordencompra_detalle'),
    path('finanzas/ordenes-compra/<int:pk>/editar/', views_finanzas.OrdenDeCompraUpdateView.as_view(), name='ordencompra_update'), 
    path('finanzas/ordenes-compra/<int:pk>/eliminar/', views_finanzas.OrdenDeCompraDeleteView.as_view(), name='ordencompra_eliminar'),
    path('finanzas/ordenes-compra/<int:pk>/procesar/', views_finanzas.OrdenDeCompraProcesarView.as_view(), name='ordencompra_procesar'),

    # --- B. CUENTAS POR PAGAR (CxP) ---
    path('finanzas/cuentas-pagar/', views_finanzas.CuentaAPagarListView.as_view(), name='cuentapagar_lista'),
    path('finanzas/cuentas-pagar/<int:pk>/', views_finanzas.CuentaAPagarDetailView.as_view(), name='cuentapagar_detalle'),
    path('finanzas/cuentas-pagar/<int:pk>/editar/', views_finanzas.CuentaAPagarUpdateView.as_view(), name='cuentapagar_update'), 

    # --- C. ÓRDENES DE PAGO (OP) ---
    path('finanzas/ordenes-pago/', views_finanzas.OrdenDePagoListView.as_view(), name='ordenpago_lista'),
    path('finanzas/ordenes-pago/crear/', views_finanzas.OrdenDePagoCreateView.as_view(), name='ordenpago_crear'),
    path('finanzas/ordenes-pago/<int:pk>/', views_finanzas.OrdenDePagoDetailView.as_view(), name='ordenpago_detalle'),
    path('finanzas/ordenes-pago/<int:pk>/editar/', views_finanzas.OrdenDePagoUpdateView.as_view(), name='ordenpago_update'), 
    path('finanzas/ordenes-pago/<int:pk>/eliminar/', views_finanzas.OrdenDePagoDeleteView.as_view(), name='ordenpago_eliminar'), 
    path('finanzas/ordenes-pago/<int:pk>/procesar/', views_finanzas.OrdenDePagoProcesarView.as_view(), name='ordenpago_procesar'),

    # 🔄 --- D. DEVOLUCIÓN A PROVEEDOR (DAP) ---
    path('finanzas/devoluciones-proveedor/', 
         views_finanzas.DevolucionAProveedorListView.as_view(), 
         name='devolucionproveedor_lista'),

    path('finanzas/devoluciones-proveedor/crear/', 
         views_finanzas.DevolucionAProveedorCreateView.as_view(), 
         name='devolucionproveedor_crear'),

    path('finanzas/devoluciones-proveedor/<int:pk>/', 
         views_finanzas.DevolucionAProveedorDetailView.as_view(), 
         name='devolucionproveedor_detalle'),

    path('finanzas/devoluciones-proveedor/<int:pk>/editar/', 
         views_finanzas.DevolucionAProveedorUpdateView.as_view(), 
         name='devolucionproveedor_editar'),

    path('finanzas/devoluciones-proveedor/<int:pk>/procesar/', 
         views_finanzas.DevolucionAProveedorProcesarView.as_view(), 
         name='devolucionproveedor_procesar'),

    # ===================================================================
    # 🆕 E. CUENTAS POR COBRAR (CxC) 💰
    # ===================================================================
    path('finanzas/cuentas-cobrar/', 
         views_finanzas.CuentaACobrarListView.as_view(), 
         name='cuentacobrar_lista'),
    
    path('finanzas/cuentas-cobrar/<int:pk>/', 
         views_finanzas.CuentaACobrarDetailView.as_view(), 
         name='cuentacobrar_detalle'),
      # Crear cuenta   
     path('finanzas/cuentas-cobrar/crear/', 
     views_finanzas.CuentaACobrarCreateView.as_view(), 
     name='cuentacobrar_crear'),

# Editar cuenta  
path('finanzas/cuentas-cobrar/<int:pk>/editar/', 
     views_finanzas.CuentaACobrarUpdateView.as_view(), 
     name='cuentacobrar_editar'),

 # ===================================================================
# 🆕 F. GESTIÓN DE CAJAS 🏦
# ===================================================================
path('finanzas/cajas/', 
     views_finanzas.CajaListView.as_view(), 
     name='caja_lista'),
    
path('finanzas/cajas/<int:pk>/',  # ← EL pk DEBE SER int
     views_finanzas.CajaDetailView.as_view(), 
     name='caja_detalle'),
    
path('finanzas/cajas/crear/', 
     views_finanzas.CajaCreateView.as_view(), 
     name='caja_crear'),

path('finanzas/cajas/<int:pk>/cerrar/', 
     views_finanzas.CajaCerrarView.as_view(), 
     name='caja_cerrar'),

# ===================================================================
# 🆕 H. ARQUEO DE CAJA 📊
# ===================================================================
path('finanzas/arqueos/crear/', 
     views_finanzas.ArqueoCreateView.as_view(), 
     name='arqueo_crear'),   

# ===================================================================
# 🆕 I. INFORMES FINANCIEROS 📈
# ===================================================================
path('finanzas/estado-cuentas/', 
     views_finanzas.EstadoCuentasView.as_view(), 
     name='estado_cuentas'),

path('finanzas/flujo-caja/', 
     views_finanzas.FlujoCajaView.as_view(), 
     name='flujo_caja'),

]