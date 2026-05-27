# gestion/views.py

from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, redirect
from django.db.models import F, Count, Sum
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.db import IntegrityError
from decimal import Decimal 
from django import forms
from django.forms import inlineformset_factory

# ===================================================================
# 🔑 IMPORTACIONES DE SEGURIDAD
# ===================================================================
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.views import LoginView as AuthLoginView, LogoutView as AuthLogoutView 
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin, LoginRequiredMixin
from django.views import View
from django.views.generic import DetailView, UpdateView, CreateView, ListView, DeleteView, FormView

# Importaciones de clases base y modelos
from .models import (
    Cliente, Producto, Venta, Proveedor, Compra,
    DetalleVenta, DetalleCompra, Ajuste, CategoriaProducto, Marca, InventarioMovimiento,
    AjusteDetalle
)
# Importación de formularios y formset
from .forms import (
    ClienteForm, ProveedorForm, ProductoForm, CategoriaProductoForm, MarcaForm,
    DetalleVentaFormset, VentaForm,
    DetalleCompraFormset, CompraForm,
)

# Definiciones de formularios placeholder para Ajuste
class DummyAjusteForm(forms.ModelForm):
    class Meta:
        model = Ajuste
        fields = ['tipo_ajuste', 'empleado', 'motivo', 'estado']
AjusteForm = DummyAjusteForm

DetalleAjusteFormset = inlineformset_factory(
    Ajuste, AjusteDetalle, fields=['producto', 'cantidad'], extra=1, can_delete=True
) 

# Se asume que views_base existe y tiene las clases correctas
from .views_base import BaseListView, BaseCreateView, BaseUpdateView, BaseDeleteView

# ===================================================================
# 🔑 VISTAS DE AUTENTICACIÓN
# ===================================================================

class LoginView(AuthLoginView):
    """ Vista personalizada para el login. Usa el template 'login.html'. """
    template_name = 'login.html'
    
    def get_success_url(self):
        return reverse_lazy('dashboard') 

    def form_invalid(self, form):
        messages.error(self.request, "Credenciales incorrectas. Intente de nuevo.")
        return super().form_invalid(form)


class LogoutView(AuthLogoutView):
    """ Vista para el cierre de sesión. Redirige a la URL de login. """
    next_page = reverse_lazy('login')


# -------------------------------------------------------------------
# 1. VISTA DEL DASHBOARD (PROTEGIDA)
# -------------------------------------------------------------------
# Se mantiene el decorador @login_required, aunque LoginRequiredMixin es mejor en CBVs.
# Para este ejemplo con función, se deja así.
@login_required(login_url='/login/')
def dashboard(request):
    """
    Muestra la página de inicio (Dashboard) con métricas básicas y alertas.
    """
    
    conteo_clientes = Cliente.objects.count()
    conteo_proveedores = Proveedor.objects.count()
    conteo_productos = Producto.objects.count()
    
    try:
        conteo_ventas_pendientes = Venta.objects.filter(estado__iexact='PENDIENTE').count()
        ultimas_ventas = Venta.objects.all().order_by('-fecha')[:5]
    except Exception:
        conteo_ventas_pendientes = 0
        ultimas_ventas = []

    try:
        productos_bajo_stock = Producto.objects.filter(stock__lte=F('stock_minimo')).order_by('stock')[:5]
    except Exception:
        productos_bajo_stock = []

    context = {
        'total_clientes': conteo_clientes,
        'total_proveedores': conteo_proveedores,
        'total_productos': conteo_productos,
        'ventas_pendientes': conteo_ventas_pendientes,
        'ultimas_ventas': ultimas_ventas,
        'productos_bajo_stock': productos_bajo_stock,
        'titulo_pagina': 'Dashboard Principal',
        'usuario': request.user,
    }
    
    return render(request, 'gestion/dashboard.html', context)


# ===================================================================
# MÓDULO CLIENTES (CRUD Completo)
# ===================================================================

class ClienteCreateView(BaseCreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'gestion/clientes/cliente_form.html'
    success_url_name = 'cliente_lista'
    success_message = "El cliente fue registrado exitosamente."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Registrar Nuevo Cliente'
        return context

class ClienteListView(BaseListView):
    model = Cliente
    template_name = 'gestion/clientes/cliente_list.html'
    context_object_name = 'clientes'
    titulo_pagina = 'Listado de Clientes'

class ClienteUpdateView(BaseUpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'gestion/clientes/cliente_form.html'
    success_url_name = 'cliente_lista'
    success_message = "Cliente actualizado correctamente."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = f'Editar Cliente: {self.object}'
        return context

class ClienteDeleteView(PermissionRequiredMixin, BaseDeleteView):
    permission_required = 'is_staff'
    raise_exception = True
    model = Cliente
    template_name = 'gestion/confirm_delete.html'
    success_url_name = 'cliente_lista'
    success_message = "Cliente eliminado permanentemente."


# ===================================================================
# MÓDULO PROVEEDORES (CRUD Completo)
# ===================================================================

class ProveedorCreateView(BaseCreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'gestion/proveedores/proveedor_form.html'
    success_url_name = 'proveedor_lista'
    success_message = "Proveedor registrado exitosamente."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Registrar Nuevo Proveedor'
        return context


class ProveedorListView(BaseListView):
    model = Proveedor
    template_name = 'gestion/proveedores/proveedor_list.html'
    context_object_name = 'proveedores'
    titulo_pagina = 'Listado de Proveedores'
    
class ProveedorUpdateView(BaseUpdateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'gestion/proveedores/proveedor_form.html'
    success_url_name = 'proveedor_lista'
    success_message = "Proveedor actualizado correctamente."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = f'Editar Proveedor: {self.object}'
        return context

class ProveedorDeleteView(PermissionRequiredMixin, BaseDeleteView):
    permission_required = 'is_staff'
    raise_exception = True
    model = Proveedor
    template_name = 'gestion/confirm_delete.html'
    success_url_name = 'proveedor_lista'
    success_message = "Proveedor eliminado permanentemente."

# ===================================================================
# MÓDULO PRODUCTOS (CRUD Completo)
# ===================================================================

class ProductoCreateView(BaseCreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'gestion/productos/producto_form.html'
    success_url_name = 'producto_lista'
    success_message = "Producto registrado exitosamente. Stock inicial: 0"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Registrar Nuevo Producto'
        return context

class ProductoListView(BaseListView):
    model = Producto
    template_name = 'gestion/productos/producto_list.html'
    context_object_name = 'productos'
    titulo_pagina = 'Catálogo de Productos'
    
class ProductoUpdateView(BaseUpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'gestion/productos/producto_form.html'
    success_url_name = 'producto_lista'
    success_message = "Producto actualizado correctamente."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = f'Editar Producto: {self.object}'
        return context

class ProductoDeleteView(PermissionRequiredMixin, BaseDeleteView):
    permission_required = 'is_staff'
    raise_exception = True
    model = Producto
    template_name = 'gestion/confirm_delete.html'
    success_url_name = 'producto_lista'
    success_message = "Producto eliminado permanentemente."

# ===================================================================
# MÓDULO CATÁLOGOS (Categoría y Marca)
# ===================================================================

# 1. CATEGORÍA
class CategoriaProductoCreateView(BaseCreateView):
    model = CategoriaProducto
    fields = ['nombre']
    template_name = 'gestion/categorias/categoria_form.html' 
    success_url_name = 'categoria_lista'
    success_message = "Categoría creada exitosamente."

class CategoriaProductoListView(BaseListView):
    model = CategoriaProducto
    template_name = 'gestion/categorias/categoria_list.html'
    context_object_name = 'categorias'
    titulo_pagina = 'Listado de Categorías'

class CategoriaProductoUpdateView(BaseUpdateView):
    model = CategoriaProducto
    fields = ['nombre']
    
    template_name = 'gestion/categorias/categoria_form.html'
    success_url_name = 'categoria_lista'
    success_message = "Categoría actualizada correctamente."

class CategoriaProductoDeleteView(PermissionRequiredMixin, BaseDeleteView):
    permission_required = 'is_staff'
    model = CategoriaProducto
    template_name = 'gestion/confirm_delete.html' 
    success_url_name = 'categoria_lista'
    success_message = "Categoría eliminada permanentemente."
# 2. MARCA
class MarcaCreateView(BaseCreateView):
    model = Marca
    fields = ['nombre']
    
    template_name = 'gestion/marcas/marca_form.html'
    success_url_name = 'marca_lista'
    success_message = "Marca creada exitosamente."

class MarcaListView(BaseListView):
    model = Marca
 
    template_name = 'gestion/marcas/marca_list.html'
    context_object_name = 'marcas'
    titulo_pagina = 'Listado de Marcas'

class MarcaUpdateView(BaseUpdateView):
    model = Marca
    fields = ['nombre']
  
    template_name = 'gestion/marcas/marca_form.html'
    success_url_name = 'marca_lista'
    success_message = "Marca actualizada correctamente."

class MarcaDeleteView(PermissionRequiredMixin, BaseDeleteView):
    permission_required = 'is_staff'
    model = Marca
    template_name = 'gestion/confirm_delete.html' 
    success_url_name = 'marca_lista'
    success_message = "Marca eliminada permanentemente."

# ===================================================================
# MÓDULO VENTAS (Cabecera y Detalle)
# ===================================================================

class VentaCreateView(BaseCreateView):
    model = Venta
    form_class = VentaForm
    template_name = 'gestion/ventas/venta_form.html'
    success_message = "Cabecera de Venta registrada exitosamente. Continúe añadiendo los productos."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Registrar Nueva Venta (Cabecera)'
        return context
    
    def form_valid(self, form):
        if self.request.user.is_authenticated and hasattr(form.instance, 'empleado'):
             # form.instance.empleado = self.request.user # Descomentar si usas un campo 'empleado'
             pass
             
        form.instance.total = 0 # Inicializar el total a cero
        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse_lazy('venta_detalle', kwargs={'pk': self.object.pk})

class VentaListView(BaseListView):
    model = Venta
    template_name = 'gestion/ventas/venta_list.html'
    context_object_name = 'ventas'
    titulo_pagina = 'Listado de Ventas'
    ordering = ['-fecha']

class VentaUpdateView(PermissionRequiredMixin, BaseUpdateView):
    permission_required = 'gestion.change_venta'
    raise_exception = True
    
    model = Venta
    form_class = VentaForm
    template_name = 'gestion/ventas/venta_form.html'
    success_message = "Cabecera de Venta actualizada exitosamente."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = f'Editar Venta N°{self.object.pk}'
        return context
    
    def get_success_url(self):
        return reverse_lazy('venta_detalle', kwargs={'pk': self.object.pk})
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Bloqueo de Edición si está FINALIZADA
        if self.object.estado == 'FINALIZADA':
            messages.error(request, f"No se puede editar la Venta N°{self.object.id} porque ya ha sido FINALIZADA.")
            return redirect(self.get_success_url())
            
        return super().post(request, *args, **kwargs)

class VentaDetalleView(PermissionRequiredMixin, UpdateView):
    permission_required = 'gestion.change_venta'
    
    model = Venta
    form_class = VentaForm
    template_name = 'gestion/ventas/venta_detalle.html'
    context_object_name = 'venta'
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        venta = self.object
        
        if self.request.POST:
            data['formset'] = DetalleVentaFormset(self.request.POST, instance=venta)
        elif 'formset' in kwargs:
            data['formset'] = kwargs['formset']
        else:
            data['formset'] = DetalleVentaFormset(instance=venta)
            
        data['titulo_pagina'] = f'Detalle de Venta #{venta.id}'
        data['detalles'] = DetalleVenta.objects.filter(venta=venta).select_related('producto')
        
        return data
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # VERIFICACIÓN DE SEGURIDAD CRÍTICA (Estado de Venta)
        if self.object.estado == 'FINALIZADA':
            messages.error(request, f"No se puede modificar la Venta N°{self.object.id} porque ya ha sido FINALIZADA.")
            return redirect(self.get_success_url())
        
        form = VentaForm(request.POST, instance=self.object)
        formset = DetalleVentaFormset(request.POST, instance=self.object)

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    self.object = form.save()
                    
                    # 2. Guardar los detalles (crea/actualiza/elimina DetalleVenta)
                    formset.save()
                    
                    # 3. CÁLCULO Y ACTUALIZACIÓN DEL TOTAL DE LA VENTA
                    nuevo_total = DetalleVenta.objects.filter(venta=self.object).aggregate(
                        total_sum=Sum(F('cantidad') * F('precio_unitario'))
                    )
                    
                    self.object.total = nuevo_total.get('total_sum') or Decimal('0.00')
                    
                    self.object.save(update_fields=['total'])
                        
                # 4. ÉXITO (La transacción se completa)
                messages.success(request, f"Venta #{self.object.id} y sus detalles fueron actualizados correctamente. Total actualizado.")
                return redirect(self.get_success_url())
                        
            except Exception as e:
                messages.error(request, f"Error al guardar los detalles: {e}. La operación ha sido anulada.")
                return self.render_to_response(self.get_context_data(form=form, formset=formset))

        else:
            # 5. ERRORES DE VALIDACIÓN DEL FORMULARIO
            messages.error(request, "Hubo errores en el formulario de detalles. Revise la cantidad y los campos obligatorios.")
            return self.render_to_response(self.get_context_data(form=form, formset=formset))
            
    def get_success_url(self):
        return reverse_lazy('venta_detalle', kwargs={'pk': self.object.pk})

class VentaFinalizarView(PermissionRequiredMixin, View):
    """
    Vista que procesa y finaliza una venta, decrementando el stock de los productos.
    """
    permission_required = 'gestion.change_venta'
    raise_exception = True

    def post(self, request, pk):
        venta = get_object_or_404(Venta, pk=pk)

        if venta.estado == 'FINALIZADA':
            messages.warning(request, f"La Venta N°{venta.id} ya ha sido FINALIZADA y no puede procesarse de nuevo.")
            return redirect('venta_detalle', pk=pk)

        detalles = DetalleVenta.objects.filter(venta=venta)
        if not detalles.exists():
            messages.error(request, "No se puede finalizar una venta sin productos. Añada al menos un detalle.")
            return redirect('venta_detalle', pk=pk)

        try:
            with transaction.atomic():
                # 1. Verificar y Descontar Stock para cada detalle
                for detalle in detalles:
                    producto = detalle.producto
                    cantidad_vendida = detalle.cantidad
                    
                    if producto.stock < cantidad_vendida:
                        # Levantar un error que la transacción atrapará
                        raise IntegrityError(f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}, Solicitado: {cantidad_vendida}.")
                    
                    # Descontar el stock (usando F() para evitar condiciones de carrera)
                    Producto.objects.filter(pk=producto.pk).update(stock=F('stock') - cantidad_vendida)

                # 2. Actualizar el estado de la Venta
                venta.estado = 'FINALIZADA'
                venta.save(update_fields=['estado'])
                
            messages.success(request, f"¡Venta N°{venta.id} finalizada exitosamente! Stock descontado.")
            
        except IntegrityError as e:
            messages.error(request, f"ERROR CRÍTICO DE STOCK: {e}")
        except Exception as e:
            messages.error(request, f"Error al procesar la venta: {e}")
            
        return redirect('venta_detalle', pk=pk)
        
class VentaDeleteView(PermissionRequiredMixin, BaseDeleteView):
    permission_required = 'is_staff'
    raise_exception = True
    model = Venta
    template_name = 'gestion/confirm_delete.html'
    success_url_name = 'venta_lista'
    success_message = "Venta eliminada permanentemente (solo si estaba PENDIENTE)."
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Solo permitir eliminar si la venta está PENDIENTE
        if self.object.estado == 'FINALIZADA':
            messages.error(request, f"No se puede eliminar la Venta N°{self.object.id} porque ya ha sido FINALIZADA.")
            return redirect('venta_lista') 
            
        return super().post(request, *args, **kwargs)

# ===================================================================
# MÓDULO COMPRAS (VISTAS COMPLETAS AÑADIDAS)
# ===================================================================

class CompraCreateView(BaseCreateView):
    model = Compra
    form_class = CompraForm
    template_name = 'gestion/compras/compra_form.html'
    success_message = "Cabecera de Compra registrada. Añada los productos."
    
    def form_valid(self, form):
        form.instance.total = 0
        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse_lazy('compra_detalle', kwargs={'pk': self.object.pk})

class CompraListView(BaseListView):
    model = Compra
    template_name = 'gestion/compras/compra_list.html'
    context_object_name = 'compras'
    titulo_pagina = 'Listado de Compras'
    ordering = ['-fecha']

class CompraUpdateView(PermissionRequiredMixin, BaseUpdateView):
    permission_required = 'gestion.change_compra'
    model = Compra
    form_class = CompraForm
    template_name = 'gestion/compras/compra_form.html'
    success_message = "Cabecera de Compra actualizada."
    
    def get_success_url(self):
        return reverse_lazy('compra_detalle', kwargs={'pk': self.object.pk})
# gestion/views.py

from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, redirect
from django.db.models import F, Count, Sum
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.db import IntegrityError
from decimal import Decimal 
from django import forms
from django.forms import inlineformset_factory

# ===================================================================
# 🔑 IMPORTACIONES DE SEGURIDAD
# ===================================================================
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.views import LoginView as AuthLoginView, LogoutView as AuthLogoutView 
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin, LoginRequiredMixin
from django.views import View
from django.views.generic import DetailView, UpdateView, CreateView, ListView, DeleteView, FormView

# Importaciones de clases base y modelos
from .models import (
    Cliente, Producto, Venta, Proveedor, Compra,
    DetalleVenta, DetalleCompra, Ajuste, CategoriaProducto, Marca, InventarioMovimiento,
    AjusteDetalle, PedidoCliente, PedidoClienteDetalle, AjusteTipo # <-- ¡Nuevos Modelos Importados!
)

# Importación de formularios y formset (ASUMIMOS QUE ESTOS YA EXISTEN EN forms.py)
from .forms import (
    ClienteForm, ProveedorForm, ProductoForm, CategoriaProductoForm, MarcaForm,
    DetalleVentaFormset, VentaForm,
    DetalleCompraFormset, CompraForm,
    # Nuevas Importaciones para Pedido y Ajuste
    PedidoClienteForm, PedidoClienteDetalleFormset,
    AjusteInventarioForm, DetalleAjusteFormset 
)

# Se asume que views_base existe y tiene las clases correctas
from .views_base import BaseListView, BaseCreateView, BaseUpdateView, BaseDeleteView


# ===================================================================
# 🔑 VISTAS DE AUTENTICACIÓN
# ===================================================================

class LoginView(AuthLoginView):
    """ Vista personalizada para el login. Usa el template 'login.html'. """
    template_name = 'login.html'
    
    def get_success_url(self):
        return reverse_lazy('dashboard') 

    def form_invalid(self, form):
        messages.error(self.request, "Credenciales incorrectas. Intente de nuevo.")
        return super().form_invalid(form)


class LogoutView(AuthLogoutView):
    """ Vista para el cierre de sesión. Redirige a la URL de login. """
    next_page = reverse_lazy('login')


# -------------------------------------------------------------------
# 1. VISTA DEL DASHBOARD (PROTEGIDA)
# -------------------------------------------------------------------

@login_required(login_url='/login/')
def dashboard(request):
    """
    Muestra la página de inicio (Dashboard) con métricas básicas y alertas.
    """
    
    conteo_clientes = Cliente.objects.count()
    conteo_proveedores = Proveedor.objects.count()
    conteo_productos = Producto.objects.count()
    
    try:
        conteo_ventas_pendientes = Venta.objects.filter(estado__iexact='PENDIENTE').count()
        ultimas_ventas = Venta.objects.all().order_by('-fecha')[:5]
    except Exception:
        conteo_ventas_pendientes = 0
        ultimas_ventas = []

    try:
        productos_bajo_stock = Producto.objects.filter(stock__lte=F('stock_minimo')).order_by('stock')[:5]
    except Exception:
        productos_bajo_stock = []

    context = {
        'total_clientes': conteo_clientes,
        'total_proveedores': conteo_proveedores,
        'total_productos': conteo_productos,
        'ventas_pendientes': conteo_ventas_pendientes,
        'ultimas_ventas': ultimas_ventas,
        'productos_bajo_stock': productos_bajo_stock,
        'titulo_pagina': 'Dashboard Principal',
        'usuario': request.user,
    }
    
    return render(request, 'gestion/dashboard.html', context)


# ===================================================================
# MÓDULO CLIENTES (CRUD Completo)
# ===================================================================

class ClienteCreateView(BaseCreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'gestion/clientes/cliente_form.html'
    success_url_name = 'cliente_lista'
    success_message = "El cliente fue registrado exitosamente."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Registrar Nuevo Cliente'
        return context

class ClienteListView(BaseListView):
    model = Cliente
    template_name = 'gestion/clientes/cliente_list.html'
    context_object_name = 'clientes'
    titulo_pagina = 'Listado de Clientes'

class ClienteUpdateView(BaseUpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'gestion/clientes/cliente_form.html'
    success_url_name = 'cliente_lista'
    success_message = "Cliente actualizado correctamente."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = f'Editar Cliente: {self.object}'
        return context

class ClienteDeleteView(PermissionRequiredMixin, BaseDeleteView):
    permission_required = 'is_staff'
    raise_exception = True
    model = Cliente
    template_name = 'gestion/confirm_delete.html'
    success_url_name = 'cliente_lista'
    success_message = "Cliente eliminado permanentemente."


# ===================================================================
# MÓDULO PROVEEDORES (CRUD Completo)
# ===================================================================

class ProveedorCreateView(BaseCreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'gestion/proveedores/proveedor_form.html'
    success_url_name = 'proveedor_lista'
    success_message = "Proveedor registrado exitosamente."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Registrar Nuevo Proveedor'
        return context


class ProveedorListView(BaseListView):
    model = Proveedor
    template_name = 'gestion/proveedores/proveedor_list.html'
    context_object_name = 'proveedores'
    titulo_pagina = 'Listado de Proveedores'
    
class ProveedorUpdateView(BaseUpdateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'gestion/proveedores/proveedor_form.html'
    success_url_name = 'proveedor_lista'
    success_message = "Proveedor actualizado correctamente."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = f'Editar Proveedor: {self.object}'
        return context

class ProveedorDeleteView(PermissionRequiredMixin, BaseDeleteView):
    permission_required = 'is_staff'
    raise_exception = True
    model = Proveedor
    template_name = 'gestion/confirm_delete.html'
    success_url_name = 'proveedor_lista'
    success_message = "Proveedor eliminado permanentemente."

# ===================================================================
# MÓDULO PRODUCTOS (CRUD Completo)
# ===================================================================

class ProductoCreateView(BaseCreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'gestion/productos/producto_form.html'
    success_url_name = 'producto_lista'
    success_message = "Producto registrado exitosamente. Stock inicial: 0"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Registrar Nuevo Producto'
        return context

class ProductoListView(BaseListView):
    model = Producto
    template_name = 'gestion/productos/producto_list.html'
    context_object_name = 'productos'
    titulo_pagina = 'Catálogo de Productos'
    
class ProductoUpdateView(BaseUpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'gestion/productos/producto_form.html'
    success_url_name = 'producto_lista'
    success_message = "Producto actualizado correctamente."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = f'Editar Producto: {self.object}'
        return context

class ProductoDeleteView(PermissionRequiredMixin, BaseDeleteView):
    permission_required = 'is_staff'
    raise_exception = True
    model = Producto
    template_name = 'gestion/confirm_delete.html'
    success_url_name = 'producto_lista'
    success_message = "Producto eliminado permanentemente."

# ===================================================================
# MÓDULO CATÁLOGOS (Categoría y Marca)
# ===================================================================

# 1. CATEGORÍA
class CategoriaProductoCreateView(BaseCreateView):
    model = CategoriaProducto
    fields = ['nombre']
    template_name = 'gestion/categorias/categoria_form.html' 
    success_url_name = 'categoria_lista'
    success_message = "Categoría creada exitosamente."

class CategoriaProductoListView(BaseListView):
    model = CategoriaProducto
    template_name = 'gestion/categorias/categoria_list.html'
    context_object_name = 'categorias'
    titulo_pagina = 'Listado de Categorías'

class CategoriaProductoUpdateView(BaseUpdateView):
    model = CategoriaProducto
    fields = ['nombre']
    
    template_name = 'gestion/categorias/categoria_form.html'
    success_url_name = 'categoria_lista'
    success_message = "Categoría actualizada correctamente."

class CategoriaProductoDeleteView(PermissionRequiredMixin, BaseDeleteView):
    permission_required = 'is_staff'
    model = CategoriaProducto
    template_name = 'gestion/confirm_delete.html' 
    success_url_name = 'categoria_lista'
    success_message = "Categoría eliminada permanentemente."
    
# 2. MARCA
class MarcaCreateView(BaseCreateView):
    model = Marca
    fields = ['nombre']
    
    template_name = 'gestion/marcas/marca_form.html'
    success_url_name = 'marca_lista'
    success_message = "Marca creada exitosamente."

class MarcaListView(BaseListView):
    model = Marca
 
    template_name = 'gestion/marcas/marca_list.html'
    context_object_name = 'marcas'
    titulo_pagina = 'Listado de Marcas'

class MarcaUpdateView(BaseUpdateView):
    model = Marca
    fields = ['nombre']
 
    template_name = 'gestion/marcas/marca_form.html'
    success_url_name = 'marca_lista'
    success_message = "Marca actualizada correctamente."

class MarcaDeleteView(PermissionRequiredMixin, BaseDeleteView):
    permission_required = 'is_staff'
    model = Marca
    template_name = 'gestion/confirm_delete.html' 
    success_url_name = 'marca_lista'
    success_message = "Marca eliminada permanentemente."

# ===================================================================
# MÓDULO VENTAS (Cabecera y Detalle)
# ===================================================================

class VentaCreateView(BaseCreateView):
    model = Venta
    form_class = VentaForm
    template_name = 'gestion/ventas/venta_form.html'
    success_message = "Cabecera de Venta registrada exitosamente. Continúe añadiendo los productos."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Registrar Nueva Venta (Cabecera)'
        return context
    
    def form_valid(self, form):
        if self.request.user.is_authenticated and hasattr(form.instance, 'empleado'):
             # form.instance.empleado = self.request.user # Descomentar si usas un campo 'empleado'
             pass
             
        form.instance.total = 0 # Inicializar el total a cero
        return super().form_valid(form)
         
    def get_success_url(self):
        return reverse_lazy('venta_detalle', kwargs={'pk': self.object.pk})

class VentaListView(BaseListView):
    model = Venta
    template_name = 'gestion/ventas/venta_list.html'
    context_object_name = 'ventas'
    titulo_pagina = 'Listado de Ventas'
    ordering = ['-fecha']

class VentaUpdateView(PermissionRequiredMixin, BaseUpdateView):
    permission_required = 'gestion.change_venta'
    raise_exception = True
    
    model = Venta
    form_class = VentaForm
    template_name = 'gestion/ventas/venta_form.html'
    success_message = "Cabecera de Venta actualizada exitosamente."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = f'Editar Venta N°{self.object.pk}'
        return context
    
    def get_success_url(self):
        return reverse_lazy('venta_detalle', kwargs={'pk': self.object.pk})
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Bloqueo de Edición si está FINALIZADA
        if self.object.estado == 'FINALIZADA':
            messages.error(request, f"No se puede editar la Venta N°{self.object.id} porque ya ha sido FINALIZADA.")
            return redirect(self.get_success_url())
            
        return super().post(request, *args, **kwargs)

class VentaDetalleView(PermissionRequiredMixin, UpdateView):
    permission_required = 'gestion.change_venta'
    
    model = Venta
    form_class = VentaForm
    template_name = 'gestion/ventas/venta_detalle.html'
    context_object_name = 'venta'
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        venta = self.object
        
        if self.request.POST:
            data['formset'] = DetalleVentaFormset(self.request.POST, instance=venta)
        elif 'formset' in kwargs:
            data['formset'] = kwargs['formset']
        else:
            data['formset'] = DetalleVentaFormset(instance=venta)
            
        data['titulo_pagina'] = f'Detalle de Venta #{venta.id}'
        data['detalles'] = venta.detalleventa_set.all().select_related('producto')
        
        return data
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # VERIFICACIÓN DE SEGURIDAD CRÍTICA (Estado de Venta)
        if self.object.estado == 'FINALIZADA':
            messages.error(request, f"No se puede modificar la Venta N°{self.object.id} porque ya ha sido FINALIZADA.")
            return redirect(self.get_success_url())
        
        form = VentaForm(request.POST, instance=self.object)
        formset = DetalleVentaFormset(request.POST, instance=self.object)

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    self.object = form.save()
                    
                    # 2. Guardar los detalles (crea/actualiza/elimina DetalleVenta)
                    formset.save()
                    
                    # 3. CÁLCULO Y ACTUALIZACIÓN DEL TOTAL DE LA VENTA
                    # Este cálculo sirve como fallback si los signals fallan
                    nuevo_total = DetalleVenta.objects.filter(venta=self.object).aggregate(
                        total_sum=Sum(F('cantidad') * F('precio_unitario'))
                    )
                    
                    self.object.total = nuevo_total.get('total_sum') or Decimal('0.00')
                    
                    self.object.save(update_fields=['total'])
                            
                # 4. ÉXITO (La transacción se completa)
                messages.success(request, f"Venta #{self.object.id} y sus detalles fueron actualizados correctamente. Total actualizado.")
                return redirect(self.get_success_url())
                            
            except Exception as e:
                messages.error(request, f"Error al guardar los detalles: {e}. La operación ha sido anulada.")
                return self.render_to_response(self.get_context_data(form=form, formset=formset))

        else:
            # 5. ERRORES DE VALIDACIÓN DEL FORMULARIO
            messages.error(request, "Hubo errores en el formulario de detalles. Revise la cantidad y los campos obligatorios.")
            return self.render_to_response(self.get_context_data(form=form, formset=formset))
            
    def get_success_url(self):
        return reverse_lazy('venta_detalle', kwargs={'pk': self.object.pk})

class VentaFinalizarView(PermissionRequiredMixin, View):
    """
    Vista que procesa y finaliza una venta, decrementando el stock de los productos.
    """
    permission_required = 'gestion.change_venta'
    raise_exception = True

    def post(self, request, pk):
        venta = get_object_or_404(Venta, pk=pk)

        if venta.estado == 'FINALIZADA':
            messages.warning(request, f"La Venta N°{venta.id} ya ha sido FINALIZADA y no puede procesarse de nuevo.")
            return redirect('venta_detalle', pk=pk)

        detalles = DetalleVenta.objects.filter(venta=venta)
        if not detalles.exists():
            messages.error(request, "No se puede finalizar una venta sin productos. Añada al menos un detalle.")
            return redirect('venta_detalle', pk=pk)

        try:
            with transaction.atomic():
                # 1. Verificar y Descontar Stock para cada detalle
                for detalle in detalles:
                    producto = detalle.producto
                    cantidad_vendida = detalle.cantidad
                    
                    if producto.stock < cantidad_vendida:
                        # Levantar un error que la transacción atrapará
                        raise IntegrityError(f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}, Solicitado: {cantidad_vendida}.")
                    
                    # Descontar el stock (usando F() para evitar condiciones de carrera)
                    # NOTA: Los signals deberían manejar esto, pero este F() asegura la validación aquí.
                    Producto.objects.filter(pk=producto.pk).update(stock=F('stock') - cantidad_vendida)

                # 2. Actualizar el estado de la Venta
                venta.estado = 'FINALIZADA'
                venta.save(update_fields=['estado'])
                
            messages.success(request, f"¡Venta N°{venta.id} finalizada exitosamente! Stock descontado.")
            
        except IntegrityError as e:
            messages.error(request, f"ERROR CRÍTICO DE STOCK: {e}")
        except Exception as e:
            messages.error(request, f"Error al procesar la venta: {e}")
            
        return redirect('venta_detalle', pk=pk)
        
class VentaDeleteView(PermissionRequiredMixin, BaseDeleteView):
    permission_required = 'is_staff'
    raise_exception = True
    model = Venta
    template_name = 'gestion/confirm_delete.html'
    success_url_name = 'venta_lista'
    success_message = "Venta eliminada permanentemente (solo si estaba PENDIENTE)."
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Solo permitir eliminar si la venta está PENDIENTE
        if self.object.estado == 'FINALIZADA':
            messages.error(request, f"No se puede eliminar la Venta N°{self.object.id} porque ya ha sido FINALIZADA.")
            return redirect('venta_lista') 
            
        return super().post(request, *args, **kwargs)

# ===================================================================
# MÓDULO COMPRAS (VISTAS COMPLETAS)
# ===================================================================

class CompraCreateView(BaseCreateView):
    model = Compra
    form_class = CompraForm
    template_name = 'gestion/compras/compra_form.html'
    success_message = "Cabecera de Compra registrada. Añada los productos."
    
    def form_valid(self, form):
        form.instance.total = 0
        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse_lazy('compra_detalle', kwargs={'pk': self.object.pk})

class CompraListView(BaseListView):
    model = Compra
    template_name = 'gestion/compras/compra_list.html'
    context_object_name = 'compras'
    titulo_pagina = 'Listado de Compras'
    ordering = ['-fecha']

class CompraUpdateView(PermissionRequiredMixin, BaseUpdateView):
    permission_required = 'gestion.change_compra'
    model = Compra
    form_class = CompraForm
    template_name = 'gestion/compras/compra_form.html'
    success_message = "Cabecera de Compra actualizada."
    
    def get_success_url(self):
        return reverse_lazy('compra_detalle', kwargs={'pk': self.object.pk})

class CompraDetalleView(PermissionRequiredMixin, UpdateView):
    permission_required = 'gestion.change_compra'
    model = Compra
    form_class = CompraForm
    template_name = 'gestion/compras/compra_detalle.html'
    context_object_name = 'compra'
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        compra = self.object
        
        if self.request.POST:
            data['formset'] = DetalleCompraFormset(self.request.POST, instance=compra)
        else:
            data['formset'] = DetalleCompraFormset(instance=compra)

        data['titulo_pagina'] = f'Detalle de Compra #{compra.id}'
        data['detalles'] = compra.detallecompra_set.all().select_related('producto')
        return data
        
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        if self.object.estado == 'FINALIZADA':
            messages.error(request, f"No se puede modificar la Compra N°{self.object.id} porque ya ha sido FINALIZADA.")
            return redirect(self.get_success_url())
        
        form = CompraForm(request.POST, instance=self.object)
        formset = DetalleCompraFormset(request.POST, instance=self.object)

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    self.object = form.save()
                    formset.save()
                    
                    # CÁLCULO Y ACTUALIZACIÓN DEL TOTAL DE LA COMPRA
                    nuevo_total = DetalleCompra.objects.filter(compra=self.object).aggregate(
                        total_sum=Sum(F('cantidad') * F('costo_unitario'))
                    )
                    
                    self.object.total = nuevo_total.get('total_sum') or Decimal('0.00')
                    self.object.save(update_fields=['total'])
                            
                messages.success(request, f"Compra #{self.object.id} y sus detalles fueron actualizados correctamente. Total actualizado.")
                return redirect(self.get_success_url())
                            
            except Exception as e:
                messages.error(request, f"Error al guardar los detalles de Compra: {e}. La operación ha sido anulada.")
                return self.render_to_response(self.get_context_data(form=form, formset=formset))
        else:
            messages.error(request, "Hubo errores en el formulario de detalles de Compra.")
            return self.render_to_response(self.get_context_data(form=form, formset=formset))
            
    def get_success_url(self):
        return reverse_lazy('compra_detalle', kwargs={'pk': self.object.pk})
        
class CompraFinalizarView(PermissionRequiredMixin, View):
    """
    Vista que procesa y finaliza una compra, INCREMENTANDO el stock de los productos.
    """
    permission_required = 'gestion.change_compra'
    raise_exception = True

    def post(self, request, pk):
        compra = get_object_or_404(Compra, pk=pk)

        if compra.estado == 'FINALIZADA':
            messages.warning(request, f"La Compra N°{compra.id} ya ha sido FINALIZADA.")
            return redirect('compra_detalle', pk=pk)

        detalles = DetalleCompra.objects.filter(compra=compra)
        if not detalles.exists():
            messages.error(request, "No se puede finalizar una compra sin productos.")
            return redirect('compra_detalle', pk=pk)

        try:
            with transaction.atomic():
                # 1. Incrementar Stock para cada detalle
                for detalle in detalles:
                    producto = detalle.producto
                    cantidad_comprada = detalle.cantidad
                    
                    # Incrementar el stock
                    # NOTA: Los signals deberían manejar esto, pero este F() asegura la validación aquí.
                    Producto.objects.filter(pk=producto.pk).update(stock=F('stock') + cantidad_comprada)

                # 2. Actualizar el estado de la Compra
                compra.estado = 'FINALIZADA'
                compra.save(update_fields=['estado'])
                
            messages.success(request, f"¡Compra N°{compra.id} finalizada exitosamente! Stock actualizado.")
            
        except Exception as e:
            messages.error(request, f"Error al procesar la compra: {e}")
            
        return redirect('compra_detalle', pk=pk)

class CompraDeleteView(PermissionRequiredMixin, BaseDeleteView):
    permission_required = 'is_staff'
    model = Compra
    template_name = 'gestion/confirm_delete.html'
    success_url_name = 'compra_lista'
    success_message = "Compra eliminada (solo si estaba PENDIENTE)."
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        if self.object.estado == 'FINALIZADA':
            messages.error(request, f"No se puede eliminar la Compra N°{self.object.id} porque ya ha sido FINALIZADA.")
            return redirect('compra_lista') 
            
        return super().post(request, *args, **kwargs)

# ===================================================================
# MÓDULO PEDIDOS DE CLIENTE (VISTAS COMPLETAS AÑADIDAS)
# ===================================================================

class PedidoClienteCreateView(BaseCreateView):
    model = PedidoCliente
    form_class = PedidoClienteForm
    template_name = 'gestion/pedidos/pedido_cliente_form.html'
    success_message = "Cabecera de Pedido registrada. Continúe añadiendo los productos."
    
    def form_valid(self, form):
        form.instance.total = 0 
        return super().form_valid(form)
            
    def get_success_url(self):
        return reverse_lazy('pedido_cliente_detalle', kwargs={'pk': self.object.pk})

class PedidoClienteListView(BaseListView):
    model = PedidoCliente
    template_name = 'gestion/pedidos/pedido_cliente_list.html'
    context_object_name = 'pedidos'
    titulo_pagina = 'Listado de Pedidos de Clientes'
    ordering = ['-fecha_pedido']
    
class PedidoClienteUpdateView(PermissionRequiredMixin, BaseUpdateView):
    permission_required = 'gestion.change_pedidocliente'
    model = PedidoCliente
    form_class = PedidoClienteForm
    template_name = 'gestion/pedidos/pedido_cliente_form.html'
    success_message = "Cabecera de Pedido actualizada exitosamente."
    
    def get_success_url(self):
        # Redirige a la vista de detalle para editar los productos
        return reverse_lazy('pedido_cliente_detalle', kwargs={'pk': self.object.pk})

class PedidoClienteDetalleView(PermissionRequiredMixin, UpdateView):
    permission_required = 'gestion.change_pedidocliente'
    model = PedidoCliente
    form_class = PedidoClienteForm
    template_name = 'gestion/pedidos/pedido_cliente_detalle.html'
    context_object_name = 'pedido'
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        pedido = self.object
        
        if self.request.POST:
            data['formset'] = PedidoClienteDetalleFormset(self.request.POST, instance=pedido)
        else:
            data['formset'] = PedidoClienteDetalleFormset(instance=pedido)
            
        data['titulo_pagina'] = f'Detalle de Pedido #{pedido.id}'
        data['detalles'] = pedido.pedidoclientedetalle_set.all().select_related('producto')
        data['puede_modificar'] = pedido.estado == 'PENDIENTE'
        return data
        
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Bloqueo de Edición si no está PENDIENTE
        if self.object.estado != 'PENDIENTE':
            messages.error(request, f"No se puede modificar el Pedido N°{self.object.id} porque su estado es '{self.object.estado}'.")
            return redirect(self.get_success_url())
        
        form = PedidoClienteForm(request.POST, instance=self.object)
        formset = PedidoClienteDetalleFormset(request.POST, instance=self.object)

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    self.object = form.save()
                    formset.save()
                    
                    # CÁLCULO Y ACTUALIZACIÓN DEL TOTAL
                    nuevo_total = self.object.pedidoclientedetalle_set.aggregate(
                        total_sum=Sum(F('cantidad') * F('precio_acordado'))
                    )
                    
                    self.object.total = nuevo_total.get('total_sum') or Decimal('0.00')
                    self.object.save(update_fields=['total'])
                        
                messages.success(request, f"Pedido #{self.object.id} y sus detalles fueron actualizados correctamente.")
                return redirect(self.get_success_url())
                        
            except Exception as e:
                messages.error(request, f"Error al guardar los detalles de Pedido: {e}. La operación ha sido anulada.")
                return self.render_to_response(self.get_context_data(form=form, formset=formset))

        else:
            messages.error(request, "Hubo errores en el formulario de detalles de Pedido. Revise la cantidad y los campos obligatorios.")
            return self.render_to_response(self.get_context_data(form=form, formset=formset))
            
    def get_success_url(self):
        return reverse_lazy('pedido_cliente_detalle', kwargs={'pk': self.object.pk})
        
class PedidoClienteDeleteView(PermissionRequiredMixin, BaseDeleteView):
    permission_required = 'is_staff'
    model = PedidoCliente
    template_name = 'gestion/confirm_delete.html'
    success_url_name = 'pedido_cliente_lista'
    success_message = "Pedido de Cliente eliminado permanentemente."
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.estado != 'PENDIENTE':
            messages.error(request, f"Solo se puede eliminar un pedido PENDIENTE. Estado actual: {self.object.estado}")
            return redirect('pedido_cliente_lista') 
        return super().post(request, *args, **kwargs)

# ===================================================================
# MÓDULO AJUSTES DE INVENTARIO (VISTAS COMPLETAS - CORREGIDAS)
# ===================================================================

class AjusteCreateView(BaseCreateView):
    model = Ajuste
    form_class = AjusteInventarioForm # Usamos el nombre real
    template_name = 'gestion/ajustes/ajuste_form.html'
    success_message = "Cabecera de Ajuste creada. Añada los productos."
    def get_success_url(self):
        return reverse_lazy('ajuste_detalle', kwargs={'pk': self.object.pk})

class AjusteListView(BaseListView):
    model = Ajuste
    template_name = 'gestion/ajustes/ajuste_list.html'
    context_object_name = 'ajustes'
    titulo_pagina = 'Listado de Ajustes de Inventario'

class AjusteDetalleView(PermissionRequiredMixin, UpdateView):
    permission_required = 'gestion.change_ajuste'
    model = Ajuste
    form_class = AjusteInventarioForm # Usamos el nombre real
    template_name = 'gestion/ajustes/ajuste_detalle.html'
    context_object_name = 'ajuste'
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        ajuste = self.object
        
        if self.request.POST:
            data['formset'] = DetalleAjusteFormset(self.request.POST, instance=ajuste)
        else:
            data['formset'] = DetalleAjusteFormset(instance=ajuste)
            
        data['titulo_pagina'] = f'Detalle de Ajuste #{ajuste.id}'
        data['detalles'] = AjusteDetalle.objects.filter(ajuste=ajuste).select_related('producto')
        data['puede_modificar'] = ajuste.estado != 'PROCESADO'
        return data
        
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        if self.object.estado == 'PROCESADO':
            messages.error(request, f"No se puede modificar el Ajuste N°{self.object.id} porque ya ha sido PROCESADO.")
            return redirect(self.get_success_url())
        
        form = AjusteInventarioForm(request.POST, instance=self.object) # Usamos el nombre real
        formset = DetalleAjusteFormset(request.POST, instance=self.object)

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    self.object = form.save()
                    formset.save()
                        
                messages.success(request, f"Ajuste #{self.object.id} y sus detalles fueron actualizados correctamente.")
                return redirect(self.get_success_url())
                            
            except Exception as e:
                messages.error(request, f"Error al guardar los detalles de Ajuste: {e}. La operación ha sido anulada.")
                return self.render_to_response(self.get_context_data(form=form, formset=formset))
        else:
            messages.error(request, "Hubo errores en el formulario de detalles de Ajuste.")
            return self.render_to_response(self.get_context_data(form=form, formset=formset))
            
    def get_success_url(self):
        return reverse_lazy('ajuste_detalle', kwargs={'pk': self.object.pk})

class AjusteProcesarView(PermissionRequiredMixin, View):
    """
    Vista que procesa un ajuste, sumando o restando stock según el tipo de ajuste.
    *** Lógica corregida para usar ajuste.tipo_ajuste.es_entrada ***
    """
    permission_required = 'gestion.change_ajuste'
    raise_exception = True

    def post(self, request, pk):
        ajuste = get_object_or_404(Ajuste, pk=pk)

        if ajuste.estado == 'PROCESADO':
            messages.warning(request, f"El Ajuste N°{ajuste.id} ya ha sido PROCESADO.")
            return redirect('ajuste_detalle', pk=pk)

        detalles = AjusteDetalle.objects.filter(ajuste=ajuste)
        if not detalles.exists():
            messages.error(request, "No se puede procesar un ajuste sin detalles de producto.")
            return redirect('ajuste_detalle', pk=pk)

        # 1. Obtener la dirección del ajuste (CORRECCIÓN CRÍTICA)
        try:
            es_entrada = ajuste.tipo_ajuste.es_entrada 
        except AttributeError:
            messages.error(request, "ERROR: El tipo de ajuste no está accesible. Asegúrese que el campo tipo_ajuste esté lleno.")
            return redirect('ajuste_detalle', pk=pk)

        try:
            with transaction.atomic():
                for detalle in detalles:
                    producto = detalle.producto
                    cantidad = detalle.cantidad
                    
                    if es_entrada:
                        # SUMAR stock (entrada: robos/devoluciones de proveedor)
                        Producto.objects.filter(pk=producto.pk).update(stock=F('stock') + cantidad)
                    else:
                        # RESTAR stock (salida: obsolescencia/merma)
                        if producto.stock < cantidad:
                            raise IntegrityError(f"Stock insuficiente para Ajuste de SALIDA para {producto.nombre}. Disponible: {producto.stock}, Solicitado: {cantidad}.")
                        Producto.objects.filter(pk=producto.pk).update(stock=F('stock') - cantidad)

                # 2. Actualizar el estado del Ajuste
                ajuste.estado = 'PROCESADO'
                ajuste.save(update_fields=['estado'])
                
            messages.success(request, f"¡Ajuste N°{ajuste.id} procesado exitosamente! Stock actualizado.")
            
        except IntegrityError as e:
            messages.error(request, f"ERROR DE STOCK en ajuste: {e}")
        except Exception as e:
            messages.error(request, f"Error al procesar el ajuste: {e}")
            
        return redirect('ajuste_detalle', pk=pk)

class AjusteDeleteView(PermissionRequiredMixin, BaseDeleteView):
    permission_required = 'is_staff'
    model = Ajuste
    template_name = 'gestion/confirm_delete.html'
    success_url_name = 'ajuste_lista'
    success_message = "Ajuste eliminado (solo si no ha sido PROCESADO)."
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        if self.object.estado == 'PROCESADO':
            messages.error(request, f"No se puede eliminar el Ajuste N°{self.object.id} porque ya ha sido PROCESADO.")
            return redirect('ajuste_lista') 
            
        return super().post(request, *args, **kwargs)