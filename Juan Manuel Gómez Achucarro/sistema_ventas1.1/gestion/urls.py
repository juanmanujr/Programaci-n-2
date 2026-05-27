# ===================================================================
# gestion/urls.py 
# ===================================================================

from django.urls import path
from .views import (
    # La vista de Login y Logout DEBEN ser importadas aquí
    LoginView, LogoutView, 
    dashboard, # Vista de función (Dashboard)

    # Clientes
    ClienteListView, ClienteCreateView, ClienteUpdateView, ClienteDeleteView, 
    
    # Proveedores
    ProveedorCreateView, ProveedorListView, ProveedorUpdateView, ProveedorDeleteView,
    
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
    
    # PEDIDOS DE CLIENTE (NUEVAS VISTAS IMPORTADAS)
    PedidoClienteCreateView, PedidoClienteListView, PedidoClienteDetalleView, PedidoClienteUpdateView, PedidoClienteDeleteView,

    # AJUSTES DE INVENTARIO
    AjusteCreateView, AjusteListView, AjusteDetalleView, AjusteProcesarView, AjusteDeleteView,
)

# ➡️ IMPORTACIÓN DE VISTAS DEL MÓDULO DE FINANZAS
from . import views_finanzas 

urlpatterns = [
    # ===================================================================
    #   AUTENTICACIÓN E INTERFACES PRINCIPALES
    # ===================================================================
    # NOTA: Estas rutas (login/logout) también deben estar en sistema_ventas/urls.py
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # 1. Dashboard (General)
    path('', dashboard, name='dashboard'),

    # ===================================================================
    # CLIENTES (CRUD Completo)
    # ===================================================================
    path('clientes/', ClienteListView.as_view(), name='cliente_lista'),
    path('clientes/nuevo/', ClienteCreateView.as_view(), name='cliente_crear'), 
    path('clientes/editar/<int:pk>/', ClienteUpdateView.as_view(), name='cliente_editar'),
    path('clientes/eliminar/<int:pk>/', ClienteDeleteView.as_view(), name='cliente_eliminar'),
    
    # ===================================================================
    # PROVEEDORES (CRUD Completo)
    # ===================================================================
    path('proveedores/', ProveedorListView.as_view(), name='proveedor_lista'),
    path('proveedores/nuevo/', ProveedorCreateView.as_view(), name='proveedor_crear'), 
    path('proveedores/editar/<int:pk>/', ProveedorUpdateView.as_view(), name='proveedor_editar'),
    path('proveedores/eliminar/<int:pk>/', ProveedorDeleteView.as_view(), name='proveedor_eliminar'),
    
    # ===================================================================
    # PRODUCTOS (CRUD Completo)
    # ===================================================================
    path('productos/', ProductoListView.as_view(), name='producto_lista'),
    path('productos/nuevo/', ProductoCreateView.as_view(), name='producto_crear'), 
    path('productos/editar/<int:pk>/', ProductoUpdateView.as_view(), name='producto_editar'),
    path('productos/eliminar/<int:pk>/', ProductoDeleteView.as_view(), name='producto_eliminar'),
    
    # ===================================================================
    #   CATEGORÍAS (CRUD Completo)
    # ===================================================================
    path('categorias/', CategoriaProductoListView.as_view(), name='categoria_lista'), 
    path('categorias/nuevo/', CategoriaProductoCreateView.as_view(), name='categoria_crear'), 
    path('categorias/editar/<int:pk>/', CategoriaProductoUpdateView.as_view(), name='categoria_editar'),
    path('categorias/eliminar/<int:pk>/', CategoriaProductoDeleteView.as_view(), name='categoria_eliminar'),

    # ===================================================================
    #   MARCAS (CRUD Completo)
    # ===================================================================
    path('marcas/', MarcaListView.as_view(), name='marca_lista'), 
    path('marcas/nuevo/', MarcaCreateView.as_view(), name='marca_crear'), 
    path('marcas/editar/<int:pk>/', MarcaUpdateView.as_view(), name='marca_editar'),
    path('marcas/eliminar/<int:pk>/', MarcaDeleteView.as_view(), name='marca_eliminar'),


    # ===================================================================
    # VENTAS (Cabecera y Detalle)
    # ===================================================================
    path('ventas/', VentaListView.as_view(), name='venta_lista'),
    path('ventas/nuevo/', VentaCreateView.as_view(), name='venta_crear'), 
    path('ventas/<int:pk>/', VentaDetalleView.as_view(), name='venta_detalle'), 
    path('ventas/editar/cabecera/<int:pk>/', VentaUpdateView.as_view(), name='venta_editar_cabecera'), # Cambié nombre para diferenciar de detalle
    path('ventas/<int:pk>/finalizar/', VentaFinalizarView.as_view(), name='venta_finalizar'),
    path('ventas/<int:pk>/eliminar/', VentaDeleteView.as_view(), name='venta_eliminar'),
    
    # ===================================================================
    # COMPRAS (COMPLETO: Cabecera, Detalle, Finalizar)
    # ===================================================================
    path('compras/', CompraListView.as_view(), name='compra_lista'),
    path('compras/nuevo/', CompraCreateView.as_view(), name='compra_crear'), 
    path('compras/<int:pk>/', CompraDetalleView.as_view(), name='compra_detalle'), 
    path('compras/editar/cabecera/<int:pk>/', CompraUpdateView.as_view(), name='compra_editar_cabecera'), # Cambié nombre para diferenciar de detalle
    path('compras/<int:pk>/finalizar/', CompraFinalizarView.as_view(), name='compra_finalizar'),
    path('compras/<int:pk>/eliminar/', CompraDeleteView.as_view(), name='compra_eliminar'),
    
    # ===================================================================
    # PEDIDOS DE CLIENTE (NUEVO MÓDULO INTEGRADO)
    # ===================================================================
    path('pedidos/', PedidoClienteListView.as_view(), name='pedido_cliente_lista'),
    path('pedidos/nuevo/', PedidoClienteCreateView.as_view(), name='pedido_cliente_crear'), 
    path('pedidos/<int:pk>/', PedidoClienteDetalleView.as_view(), name='pedido_cliente_detalle'), 
    path('pedidos/editar/cabecera/<int:pk>/', PedidoClienteUpdateView.as_view(), name='pedido_cliente_editar_cabecera'), # Única URL de edición de cabecera
    path('pedidos/<int:pk>/eliminar/', PedidoClienteDeleteView.as_view(), name='pedido_cliente_eliminar'),

    # ===================================================================
    # AJUSTES DE INVENTARIO (Completo)
    # ===================================================================
    path('ajustes/', AjusteListView.as_view(), name='ajuste_lista'),
    path('ajustes/nuevo/', AjusteCreateView.as_view(), name='ajuste_crear'), 
    path('ajustes/<int:pk>/', AjusteDetalleView.as_view(), name='ajuste_detalle'), 
    path('ajustes/<int:pk>/procesar/', AjusteProcesarView.as_view(), name='ajuste_procesar'),
    path('ajustes/<int:pk>/eliminar/', AjusteDeleteView.as_view(), name='ajuste_eliminar'),
    
    # ===================================================================
    # 💰 MÓDULO DE FINANZAS
    # ===================================================================
    
    # A. ÓRDENES DE COMPRA (OC)
    path('finanzas/ordenes-compra/', 
          views_finanzas.OrdenDeCompraListView.as_view(), 
          name='ordencompra_lista'),
          
    path('finanzas/ordenes-compra/crear/', 
          views_finanzas.OrdenDeCompraCreateView.as_view(), 
          name='ordencompra_crear'),
          
    path('finanzas/ordenes-compra/<int:pk>/', 
          views_finanzas.OrdenDeCompraDetailView.as_view(), 
          name='ordencompra_detalle'),
          
    path('finanzas/ordenes-compra/<int:pk>/editar/', 
          views_finanzas.OrdenDeCompraUpdateView.as_view(), 
          name='ordencompra_update'), # Usamos _update para evitar conflictos o por convención
          
    path('finanzas/ordenes-compra/<int:pk>/eliminar/', 
          views_finanzas.OrdenDeCompraDeleteView.as_view(), 
          name='ordencompra_eliminar'),

    # Lógica de PROCESAMIENTO (Crea Compra y CxP)
    path('finanzas/ordenes-compra/<int:pk>/procesar/', 
          views_finanzas.OrdenDeCompraProcesarView.as_view(), 
          name='ordencompra_procesar'),

    # --- B. CUENTAS POR PAGAR (CxP) ---
    path('finanzas/cuentas-pagar/', 
          views_finanzas.CuentaAPagarListView.as_view(), 
          name='cuentapagar_lista'),
          
    path('finanzas/cuentas-pagar/<int:pk>/', 
          views_finanzas.CuentaAPagarDetailView.as_view(), 
          name='cuentapagar_detalle'),
          
    path('finanzas/cuentas-pagar/<int:pk>/editar/', 
          views_finanzas.CuentaAPagarUpdateView.as_view(), 
          name='cuentapagar_update'), # Añadida CRUD-Update

    # --- C. ÓRDENES DE PAGO (OP) ---
    path('finanzas/ordenes-pago/', 
          views_finanzas.OrdenDePagoListView.as_view(), 
          name='ordenpago_lista'),
          
    path('finanzas/ordenes-pago/crear/', 
          views_finanzas.OrdenDePagoCreateView.as_view(), 
          name='ordenpago_crear'),
          
    path('finanzas/ordenes-pago/<int:pk>/', 
          views_finanzas.OrdenDePagoDetailView.as_view(), 
          name='ordenpago_detalle'),
          
    path('finanzas/ordenes-pago/<int:pk>/editar/', 
          views_finanzas.OrdenDePagoUpdateView.as_view(), 
          name='ordenpago_update'), # Añadida CRUD-Update

    path('finanzas/ordenes-pago/<int:pk>/eliminar/', 
          views_finanzas.OrdenDePagoDeleteView.as_view(), 
          name='ordenpago_eliminar'), # Añadida CRUD-Delete

    # Lógica de PROCESAMIENTO (Aplica el pago a la CxP)
    path('finanzas/ordenes-pago/<int:pk>/procesar/', 
          views_finanzas.OrdenDePagoProcesarView.as_view(), 
          name='ordenpago_procesar'),

    # --- D. DEVOLUCIÓN A PROVEEDOR (DAP) ---
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
          name='devolucionproveedor_update'), # Añadida CRUD-Update
          
    path('finanzas/devoluciones-proveedor/<int:pk>/eliminar/', 
          views_finanzas.DevolucionAProveedorDeleteView.as_view(), 
          name='devolucionproveedor_eliminar'), # Añadida CRUD-Delete

    # Lógica de PROCESAMIENTO (Ajusta stock y CxP)
    path('finanzas/devoluciones-proveedor/<int:pk>/procesar/', 
          views_finanzas.DevolucionAProveedorProcesarView.as_view(), 
          name='devolucionproveedor_procesar'),
]