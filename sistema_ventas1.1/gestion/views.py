from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, redirect
from django.db.models import F, Count, Sum
from django.urls import reverse_lazy
# Mixins de Permisos
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin, LoginRequiredMixin
from django.views import View
from django.views.generic import DetailView, UpdateView, CreateView, ListView, DeleteView
from django.contrib import messages
from django.db import transaction
from django.db import IntegrityError
from decimal import Decimal # Necesario para cálculos

# Importaciones de clases base y modelos
from .models import (
    Cliente, Producto, Venta, Proveedor, Compra,
    DetalleVenta, DetalleCompra, Ajuste, CategoriaProducto, Marca, InventarioMovimiento,
    AjusteDetalle
)
# Importación de formularios y formset
from .forms import (
    ClienteForm, ProveedorForm, ProductoForm,
    DetalleVentaFormset, VentaForm,
    # NUEVOS: Incluir formularios y formsets de Compra
    DetalleCompraFormset, CompraForm
)
# Se asume que views_base existe y tiene las clases correctas
from .views_base import BaseListView, BaseCreateView, BaseUpdateView, BaseDeleteView

# -------------------------------------------------------------------
# 1. VISTA DEL DASHBOARD
# -------------------------------------------------------------------
def dashboard(request):
    """
    Muestra la página de inicio (Dashboard) con métricas básicas y alertas.
    """
    
    conteo_clientes = Cliente.objects.count()
    conteo_proveedores = Proveedor.objects.count()
    conteo_productos = Producto.objects.count()
    
    try:
        # Usar la constante del modelo si existe (o asegurar la consistencia del case)
        conteo_ventas_pendientes = Venta.objects.filter(estado__iexact='PENDIENTE').count()
        ultimas_ventas = Venta.objects.all().order_by('-fecha')[:5]
    except Exception:
        conteo_ventas_pendientes = 0
        ultimas_ventas = []

    try:
        # Se asume que tienes un campo 'stock_minimo' en Producto
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
        'titulo_pagina': 'Dashboard Principal'
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
# MÓDULO VENTAS (Cabecera y Detalle)
# ===================================================================

# 14. CREAR VENTA (Cabecera)
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
        # Asignación del empleado logueado (si aplicable) y estado inicial
        if self.request.user.is_authenticated and hasattr(form.instance, 'empleado'):
            # form.instance.empleado = self.request.user
            pass
            
        form.instance.total = 0 # Inicializar el total a cero
        return super().form_valid(form)
        
    def get_success_url(self):
        # Redirigir al detalle para añadir productos
        return reverse_lazy('venta_detalle', kwargs={'pk': self.object.pk})

# 15. LISTAR VENTAS
class VentaListView(BaseListView):
    model = Venta
    template_name = 'gestion/ventas/venta_list.html'
    context_object_name = 'ventas'
    titulo_pagina = 'Listado de Ventas'
    ordering = ['-fecha']

# 15.5. EDITAR SOLO CABECERA (VentaUpdateView)
class VentaUpdateView(PermissionRequiredMixin, BaseUpdateView):
    """Permite la edición solo de los campos de la cabecera (VentaForm)."""
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
        # Redirige al detalle de venta para continuar
        return reverse_lazy('venta_detalle', kwargs={'pk': self.object.pk})
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Bloqueo de Edición si está FINALIZADA
        if self.object.estado == 'FINALIZADA':
            messages.error(request, f"No se puede editar la Venta N°{self.object.id} porque ya ha sido FINALIZADA.")
            return redirect(self.get_success_url())
            
        return super().post(request, *args, **kwargs)

# 16. VISTA DE DETALLE COMPLETO (Listar detalles y añadir nuevos items con Formset)
class VentaDetalleView(PermissionRequiredMixin, UpdateView):
    # Usamos UpdateView para aprovechar la funcionalidad de cargar la instancia 'venta' (self.object)
    permission_required = 'gestion.change_venta'
    
    model = Venta
    form_class = VentaForm # Se usa para el formulario oculto de cabecera
    template_name = 'gestion/ventas/venta_detalle.html'
    context_object_name = 'venta'
    
    def get_context_data(self, **kwargs):
        """Añade el formset y los detalles existentes al contexto."""
        data = super().get_context_data(**kwargs)
        venta = self.object
        
        # Mantiene el estado del formulario si hay errores
        if self.request.POST:
            # Asegurarse de que el formset maneje la data del POST
            data['formset'] = DetalleVentaFormset(self.request.POST, instance=venta)
        elif 'formset' in kwargs:
            data['formset'] = kwargs['formset']
        else:
            # En GET, crea el formset inicial
            data['formset'] = DetalleVentaFormset(instance=venta)
            
        data['titulo_pagina'] = f'Detalle de Venta #{venta.id}'
        # Optimización: Usamos .select_related() si es posible para Producto
        data['detalles'] = DetalleVenta.objects.filter(venta=venta).select_related('producto')
        
        return data
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # VERIFICACIÓN DE SEGURIDAD CRÍTICA (Estado de Venta)
        if self.object.estado == 'FINALIZADA':
            messages.error(request, f"No se puede modificar la Venta N°{self.object.id} porque ya ha sido FINALIZADA.")
            return redirect(self.get_success_url())
        
        # Se crean los formularios con la data del POST
        form = VentaForm(request.POST, instance=self.object)
        formset = DetalleVentaFormset(request.POST, instance=self.object)

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    # 1. Guardar la cabecera (Venta) - Se guarda el form oculto (cliente/empleado)
                    self.object = form.save()
                    
                    # 2. Guardar los detalles (crea/actualiza/elimina DetalleVenta)
                    # La validación de stock (si es necesaria) debería estar en el clean() de DetalleVentaForm
                    formset.save()
                    
                    # 3. CÁLCULO Y ACTUALIZACIÓN DEL TOTAL DE LA VENTA (Usando el método de agregación)
                    nuevo_total = DetalleVenta.objects.filter(venta=self.object).aggregate(
                        total_sum=Sum(F('cantidad') * F('precio_unitario'))
                    )
                    
                    # Guardamos el campo total de la cabecera (incluyendo los cambios de form.save())
                    self.object.total = nuevo_total.get('total_sum') or Decimal('0.00')
                    
                    # Guardamos el campo total de la cabecera
                    self.object.save(update_fields=['total'])
                        
                # 4. ÉXITO (La transacción se completa)
                messages.success(request, f"Venta #{self.object.id} y sus detalles fueron actualizados correctamente. Total actualizado.")
                return redirect(self.get_success_url())
                
            except Exception as e:
                # Manejo general de excepciones (IntegrityError, Stock, etc.)
                messages.error(request, f"Error al guardar los detalles: {e}. La operación ha sido anulada.")
                # Renderizar la respuesta manteniendo el contexto de error
                return self.render_to_response(self.get_context_data(form=form, formset=formset))

        else:
            # 5. ERRORES DE VALIDACIÓN DEL FORMULARIO
            messages.error(request, "Hubo errores en el formulario de detalles. Revise la cantidad y los campos obligatorios.")
            # Renderizar la respuesta con los errores de form y formset
            return self.render_to_response(self.get_context_data(form=form, formset=formset))
            
    def get_success_url(self):
        """Redirige de nuevo a la misma página de detalle de venta."""
        return reverse_lazy('venta_detalle', kwargs={'pk': self.object.pk})

# 17. VISTA PARA FINALIZAR VENTA
class VentaFinalizarView(PermissionRequiredMixin, View):
    permission_required = 'gestion.change_venta'
    raise_exception = True
    
    def post(self, request, pk):
        try:
            venta = get_object_or_404(Venta, pk=pk)
            
            # 1. Bloqueo
            if venta.estado == 'FINALIZADA':
                messages.warning(request, f"La Venta N°{venta.id} ya está FINALIZADA.")
                return redirect('venta_detalle', pk=pk)
            
            # Lógica clave: cambiar el estado y DISMINUIR STOCK
            with transaction.atomic():
                detalles = DetalleVenta.objects.filter(venta=venta)
                
                if not detalles.exists():
                    messages.error(request, "La venta no tiene productos. No se puede finalizar.")
                    return redirect('venta_detalle', pk=pk)
                
                # VERIFICACIÓN Y DISMINUCIÓN DE STOCK
                for detalle in detalles:
                    producto = detalle.producto
                    cantidad_vendida = detalle.cantidad
                    
                    # Verificación: asegurar que el stock es suficiente
                    if producto.stock < cantidad_vendida:
                        raise IntegrityError(f"Stock insuficiente para el producto {producto.nombre}. Disponible: {producto.stock}, Necesario: {cantidad_vendida}")

                    # Disminución de stock
                    # USO DE QUERYSET.UPDATE() para actualización atómica segura
                    Producto.objects.filter(pk=producto.pk).update(
                        stock=F('stock') - cantidad_vendida
                    )
                    
                # Finalizar la venta
                venta.estado = 'FINALIZADA'
                venta.save(update_fields=['estado'])
            
            messages.success(request, f"¡Venta N°{venta.pk} finalizada con éxito! Stock actualizado.")
            
        except IntegrityError as e:
            messages.error(request, f"Error de stock: {e}")
        except Venta.DoesNotExist:
            messages.error(request, "La venta especificada no existe.")
        except Exception as e:
            messages.error(request, f"Ocurrió un error inesperado al finalizar la venta: {e}")
        
        return redirect('venta_detalle', pk=pk)

# 18. ELIMINAR VENTA
class VentaDeleteView(UserPassesTestMixin, BaseDeleteView):
    model = Venta
    template_name = 'gestion/confirm_delete.html'
    success_url_name = 'venta_lista'
    success_message = "Venta eliminada permanentemente."
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.estado == 'FINALIZADA':
            messages.error(request, "No se puede eliminar una Venta FINALIZADA. Considere la Anulación.")
            return redirect('venta_detalle', pk=self.object.pk)
        return super().dispatch(request, *args, **kwargs)

# ===================================================================
# MÓDULO COMPRAS (Cabecera y Detalle)
# ===================================================================

# 1. CREAR COMPRA (Cabecera)
class CompraCreateView(BaseCreateView):
    model = Compra
    form_class = CompraForm
    template_name = 'gestion/compras/compra_form.html'
    success_message = "Cabecera de Compra registrada exitosamente. Agrega los productos."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Registrar Nueva Compra (Cabecera)'
        return context
    
    def form_valid(self, form):
        form.instance.total = 0
        return super().form_valid(form)
    
    def get_success_url(self):
        # Redirigir al detalle para añadir productos
        return reverse_lazy('compra_detalle', kwargs={'pk': self.object.pk})


# 2. LISTAR COMPRAS
class CompraListView(BaseListView):
    model = Compra
    template_name = 'gestion/compras/compra_list.html'
    context_object_name = 'compras'
    titulo_pagina = 'Listado de Compras'
    ordering = ['-fecha']
    
# 3. EDITAR SOLO CABECERA (CompraUpdateView)
class CompraUpdateView(PermissionRequiredMixin, BaseUpdateView):
    """Permite la edición solo de los campos de la cabecera (CompraForm)."""
    permission_required = 'gestion.change_compra'
    raise_exception = True
    
    model = Compra
    form_class = CompraForm
    template_name = 'gestion/compras/compra_form.html'
    success_message = "Cabecera de Compra actualizada exitosamente."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = f'Editar Compra N°{self.object.pk}'
        return context
    
    def get_success_url(self):
        # Redirige al detalle de compra para continuar
        return reverse_lazy('compra_detalle', kwargs={'pk': self.object.pk})
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Bloqueo de Edición si está FINALIZADA
        if self.object.estado == 'FINALIZADA':
            messages.error(request, f"No se puede editar la Compra N°{self.object.id} porque ya ha sido FINALIZADA.")
            return redirect(self.get_success_url())
            
        return super().post(request, *args, **kwargs)

# 4. VISTA DE DETALLE COMPLETO (Formset de productos)
class CompraDetalleView(PermissionRequiredMixin, UpdateView):
    permission_required = 'gestion.change_compra'
    
    model = Compra
    form_class = CompraForm
    template_name = 'gestion/compras/compra_detalle.html'
    context_object_name = 'compra'
    
    def get_context_data(self, **kwargs):
        """Añade el formset y los detalles existentes al contexto."""
        data = super().get_context_data(**kwargs)
        compra = self.object
        
        if self.request.POST:
            # Si hay POST, usa la data enviada
            data['formset'] = DetalleCompraFormset(self.request.POST, instance=compra)
        elif 'formset' in kwargs:
            # Si se pasa un formset con errores al render_to_response
            data['formset'] = kwargs['formset']
        else:
            # En GET, crea el formset inicial
            data['formset'] = DetalleCompraFormset(instance=compra)
            
        data['titulo_pagina'] = f'Detalle de Compra #{compra.id}'
        data['detalles'] = DetalleCompra.objects.filter(compra=compra).select_related('producto')
        
        return data
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # 1. Chequeo de estado FINALIZADA
        if self.object.estado == 'FINALIZADA':
            messages.error(request, f"No se puede modificar la Compra N°{self.object.id} porque ya ha sido FINALIZADA.")
            return redirect(self.get_success_url())
        
        form = CompraForm(request.POST, instance=self.object)
        formset = DetalleCompraFormset(request.POST, instance=self.object)

        if form.is_valid() and formset.is_valid():
            # 🟢 CAMINO DE ÉXITO: Guardado y Cálculo del Total
            try:
                with transaction.atomic():
                    self.object = form.save()
                    
                    # Guardar los detalles
                    formset.save() # Esto crea/actualiza/elimina los DetalleCompra
                    
                    # CÁLCULO Y ACTUALIZACIÓN DEL TOTAL DE LA COMPRA (¡Esta parte es crítica!)
                    nuevo_total = DetalleCompra.objects.filter(compra=self.object).aggregate(
                        total_sum=Sum(F('cantidad') * F('precio_compra'))
                    )
                    self.object.total = nuevo_total.get('total_sum') or Decimal('0.00')
                    self.object.save(update_fields=['total'])
                        
                messages.success(request, f"Compra #{self.object.id} y sus detalles fueron actualizados correctamente. Total actualizado a ${self.object.total}.")
                # 🎯 DEVOLUCIÓN OBLIGATORIA EN CASO DE ÉXITO
                return redirect(self.get_success_url()) 

            except Exception as e:
                # Lógica de manejo si falla la base de datos
                messages.error(request, f"Error al guardar los detalles: {e}. La operación ha sido anulada.")
                # 🎯 DEVOLUCIÓN OBLIGATORIA EN CASO DE ERROR EN LA TRANSACCIÓN
                return self.render_to_response(self.get_context_data(form=form, formset=formset))

        else:
            # 🔴 CAMINO DE FALLO DE VALIDACIÓN
            # 🎯 DEVOLUCIÓN OBLIGATORIA EN CASO DE FALLO DE VALIDACIÓN
            messages.error(request, "Hubo errores en el formulario de detalles de compra. Revise la cantidad y los campos obligatorios.")
            return self.render_to_response(self.get_context_data(form=form, formset=formset))
            
    def get_success_url(self):
        """Redirige de nuevo a la misma página de detalle de compra."""
        return reverse_lazy('compra_detalle', kwargs={'pk': self.object.pk})

# 5. VISTA PARA FINALIZAR COMPRA (AUMENTA STOCK)
class CompraFinalizarView(PermissionRequiredMixin, View):
    permission_required = 'gestion.change_compra'
    raise_exception = True
    
    def post(self, request, pk):
        try:
            compra = get_object_or_404(Compra, pk=pk)

            if compra.estado == 'FINALIZADA':
                messages.warning(request, "Esta compra ya fue finalizada anteriormente. No se realizó ningún cambio.")
                return redirect('compra_detalle', pk=pk)
            
            # Lógica clave: cambiar el estado y AUMENTAR STOCK
            with transaction.atomic():
                detalles = DetalleCompra.objects.filter(compra=compra)
                
                if not detalles.exists():
                    messages.error(request, "La compra no tiene productos. No se puede finalizar.")
                    return redirect('compra_detalle', pk=pk)
                    
                for detalle in detalles:
                    cantidad_comprada = detalle.cantidad
                    
                    # 🚨 CORRECCIÓN CRÍTICA: Se actualiza el stock directamente usando QuerySet.update() para ser atómico y evitar race conditions.
                    Producto.objects.filter(pk=detalle.producto_id).update(
                        stock=F('stock') + cantidad_comprada
                    )
                    
                # Finalizar la compra
                compra.estado = 'FINALIZADA'
                compra.save(update_fields=['estado'])
            
            messages.success(request, f"¡Compra N°{compra.pk} finalizada con éxito! Stock actualizado.")
            
        except Compra.DoesNotExist:
            messages.error(request, "La compra especificada no existe.")
        except Exception as e:
            messages.error(request, f"Ocurrió un error inesperado al finalizar la compra: {e}")
        
        return redirect('compra_detalle', pk=pk)

# 6. ELIMINAR COMPRA
class CompraDeleteView(UserPassesTestMixin, BaseDeleteView):
    model = Compra
    template_name = 'gestion/confirm_delete.html'
    success_url_name = 'compra_lista'
    success_message = "Compra eliminada permanentemente."
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.estado == 'FINALIZADA':
            messages.error(request, "No se puede eliminar una Compra FINALIZADA.")
            return redirect('compra_detalle', pk=self.object.pk)
        return super().dispatch(request, *args, **kwargs)