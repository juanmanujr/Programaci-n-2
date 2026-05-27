# gestion/urls.py
from django.urls import path
from .views import (
    dashboard, # Vista de función (Dashboard)

    # Clientes
    ClienteListView, ClienteCreateView, ClienteUpdateView, ClienteDeleteView, 
    
    # Proveedores
    ProveedorCreateView, ProveedorListView, ProveedorUpdateView, ProveedorDeleteView,
    
    # Productos
    ProductoCreateView, ProductoListView, ProductoUpdateView, ProductoDeleteView, 
    
    # Ventas
    VentaCreateView, VentaListView, VentaDetalleView, VentaUpdateView, VentaFinalizarView, VentaDeleteView,
    
    # Compras
    CompraCreateView, CompraListView, 
    # 🚨 Importaciones faltantes para COMPRAS 🚨
    CompraUpdateView, CompraDetalleView, CompraFinalizarView, CompraDeleteView, 
)

urlpatterns = [
    # ===================================================================
    # INTERFACES PRINCIPALES
    # ===================================================================
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
    # VENTAS (Cabecera y Detalle)
    # ===================================================================
    path('ventas/', VentaListView.as_view(), name='venta_lista'),
    path('ventas/nuevo/', VentaCreateView.as_view(), name='venta_crear'), 
    path('ventas/<int:pk>/', VentaDetalleView.as_view(), name='venta_detalle'), 
    path('ventas/editar/<int:pk>/', VentaUpdateView.as_view(), name='venta_editar'),
    path('ventas/<int:pk>/finalizar/', VentaFinalizarView.as_view(), name='venta_finalizar'),
    path('ventas/<int:pk>/eliminar/', VentaDeleteView.as_view(), name='venta_eliminar'),
    
    # ===================================================================
    # COMPRAS (COMPLETO: Cabecera, Detalle, Finalizar) 🛠️ CORREGIDO
    # ===================================================================
    path('compras/', CompraListView.as_view(), name='compra_lista'),
    path('compras/nuevo/', CompraCreateView.as_view(), name='compra_crear'), 
    
    # 🎯 RUTA FALTANTE: Detalle/Edición de Items
    path('compras/<int:pk>/', CompraDetalleView.as_view(), name='compra_detalle'), 
    
    # 🎯 RUTA FALTANTE: Edición de Cabecera (Proveedor, etc.)
    path('compras/editar/<int:pk>/', CompraUpdateView.as_view(), name='compra_editar'),
    
    # 🎯 RUTA FALTANTE: Finalizar Compra (Aumentar Stock)
    path('compras/<int:pk>/finalizar/', CompraFinalizarView.as_view(), name='compra_finalizar'),
    
    # 🎯 RUTA FALTANTE: Eliminación
    path('compras/<int:pk>/eliminar/', CompraDeleteView.as_view(), name='compra_eliminar'),
]