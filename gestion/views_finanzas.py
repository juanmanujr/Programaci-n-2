# gestion/views_finanzas.py

from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import F, Sum, Q
from django.core.exceptions import FieldError  # ¡CORREGIDO AQUÍ!
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.utils import timezone
from decimal import Decimal 
from datetime import date
# Mixins y Views genéricas de Django
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.views import View
from django.views.generic import DetailView, UpdateView, CreateView, ListView, DeleteView ,TemplateView
from django.forms import inlineformset_factory 
from datetime import timedelta
# Importación de modelos 
from .models import (
    Empleado, PerfilUsuario, 
    Producto, Compra, CuentaAPagar, Proveedor,
    OrdenDeCompra, OrdenDeCompraDetalle, DetalleCompra, 
    OrdenDePago, OrdenDePagoDetalle,
    DevolucionAProveedor, DevolucionAProveedorDetalle,
    Empleado, Cobro, CobroDetalle, Arqueo, Cliente,
    CuentaACobrar,  
    Caja,
    InventarioMovimiento, Moneda, Venta
)

# Importación de formularios y formsets (de gestion/forms.py)
# Asegúrate de que estos nombres coincidan con los de tu forms.py
from .forms import (
    OrdenDeCompraForm, DetalleOrdenDeCompraForm,
    CuentaAPagarForm, 
    OrdenDePagoForm, DetalleOrdenDePagoForm, CajaForm,
    DevolucionAProveedorForm, DetalleDevolucionAProveedorForm, 
    CuentaACobrarForm,  
    CajaForm,           
    CobroForm,          
    CobroDetalleForm,   
    ArqueoForm,         
    CobroDetalleFormset, 
)

# ===================================================================
# 🏗️ CONFIGURACIÓN DE FORMSETS
# ===================================================================

DetalleOrdenDeCompraFormset = inlineformset_factory(
    OrdenDeCompra, OrdenDeCompraDetalle, form=DetalleOrdenDeCompraForm, extra=1, can_delete=True
)
DetalleOrdenDePagoFormset = inlineformset_factory(
    OrdenDePago, OrdenDePagoDetalle, form=DetalleOrdenDePagoForm, extra=1, can_delete=True
)
DetalleDevolucionAProveedorFormset = inlineformset_factory(
    DevolucionAProveedor, DevolucionAProveedorDetalle, form=DetalleDevolucionAProveedorForm, extra=1, can_delete=True
)

# ===================================================================
# 🏗️ CLASE BASE DE VISTA PARA MÓDULO DE FINANZAS
# ===================================================================

class BaseFinanzasView(LoginRequiredMixin, PermissionRequiredMixin):
    """Clase base que asegura que el usuario esté logueado y tenga permisos de staff."""
    permission_required = 'is_staff' 
    
    def get_empleado_instance(self):
        """Intenta obtener la instancia de Empleado vinculada al usuario logueado."""
        try:
            # Obtiene el PerfilUsuario asociado al usuario logueado
            perfil_usuario = PerfilUsuario.objects.get(user=self.request.user)
            # Intenta devolver la instancia de Empleado
            return perfil_usuario.empleado
        except PerfilUsuario.DoesNotExist:
            return None # El usuario no tiene PerfilUsuario
        except AttributeError:
            # Si perfil_usuario.empleado es None, o si el atributo no existe
            return None




# --- Lógica de Procesamiento de OC (Genera Compra y CxP) ---
class OrdenDeCompraProcesarView(BaseFinanzasView, View):
    
    def post(self, request, pk):
        oc = get_object_or_404(OrdenDeCompra, pk=pk)
        
        if oc.estado != 'Pendiente':
            messages.warning(request, f"La Orden de Compra N°{oc.pk} ya fue procesada o cancelada.")
            return redirect('ordencompra_detalle', pk=pk)
            
        if not oc.empleado:
            messages.error(request, "Error de Procesamiento: La OC no tiene Empleado asignado.")
            return redirect('ordencompra_detalle', pk=pk)
            
        try:
            with transaction.atomic():
                # 1. Crear la Compra asociada 
                nueva_compra = Compra.objects.create(
                    proveedor=oc.proveedor,
                    empleado=oc.empleado,
                    total=oc.total,
                    estado='Recibida', # Se marca como Recibida al procesar la OC
                )
                
                # 2. Crear los DetalleCompra (Dispara la señal para actualizar stock)
                for detalle_oc in oc.ordendecompradetalle_set.all():
                    DetalleCompra.objects.create(
                        compra=nueva_compra,
                        producto=detalle_oc.producto,
                        cantidad=detalle_oc.cantidad,
                        precio_compra=detalle_oc.precio_unitario, 
                        subtotal=detalle_oc.subtotal
                    )
                    
                # 3. Crear la Cuenta por Pagar (CxP)
                CuentaAPagar.objects.create(
                    proveedor=oc.proveedor,
                    compra=nueva_compra,
                    monto_original=oc.total,
                    monto_pendiente=oc.total,
                    # Asumiendo que fecha_entrega_estimada es un buen proxy para fecha_vencimiento
                    fecha_vencimiento=oc.fecha_entrega_estimada, 
                    estado='Pendiente',
                )
                
                # 4. Actualizar el estado de la Orden de Compra
                oc.estado = 'Recibida'
                oc.save(update_fields=['estado'])
                
            messages.success(request, f"Orden de Compra N°{oc.pk} procesada. Se creó **Compra N°{nueva_compra.pk}** y Cuenta por Pagar.")
            
        except IntegrityError as e:
            messages.error(request, f"Error de integridad en la base de datos (Transacción cancelada): {e}")
        except Exception as e:
            messages.error(request, f"Error al procesar la Orden de Compra: {e}")
            
        return redirect('ordencompra_detalle', pk=pk)

class OrdenDeCompraDeleteView(BaseFinanzasView, DeleteView):
    model = OrdenDeCompra
    template_name = 'gestion/confirm_delete.html'
    success_url = reverse_lazy('ordencompra_lista')
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.estado == 'Recibida':
            messages.error(request, f"No se puede eliminar la OC N°{self.object.pk} porque ya está PROCESADA/RECIBIDA.")
            return redirect('ordencompra_detalle', pk=self.object.pk)
        messages.success(request, f"Orden de Compra N°{self.object.pk} eliminada.")
        return super().post(request, *args, **kwargs)


# ===================================================================
# B. CUENTAS POR PAGAR (CxP) 💸
# ===================================================================

class CuentaAPagarListView(BaseFinanzasView, ListView):
    model = CuentaAPagar
    template_name = 'gestion/finanzas/cuentapagar_lista.html'
    context_object_name = 'cuentas_pagar'
    ordering = ['estado', 'fecha_vencimiento']
    
    def get_queryset(self):
        # Muestra cuentas pendientes y vencidas
        return CuentaAPagar.objects.exclude(estado='Pagada').order_by('fecha_vencimiento') 

class CuentaAPagarDetailView(BaseFinanzasView, DetailView):
    model = CuentaAPagar
    template_name = 'gestion/finanzas/cuentapagar_detalle.html'
    context_object_name = 'cuenta_pagar'

class CuentaAPagarUpdateView(BaseFinanzasView, UpdateView):
    model = CuentaAPagar
    form_class = CuentaAPagarForm 
    template_name = 'gestion/finanzas/cuentapagar_form.html'
    
    def get_success_url(self):
        return reverse_lazy('cuentapagar_detalle', kwargs={'pk': self.object.pk})

# ===================================================================
# C. ORDEN DE PAGO (OP) 💵
# ===================================================================

class OrdenDePagoListView(BaseFinanzasView, ListView):
    model = OrdenDePago
    template_name = 'gestion/finanzas/ordenpago_list.html'
    context_object_name = 'ordenes_pago'
    ordering = ['-fecha_orden']

class OrdenDePagoDetailView(BaseFinanzasView, DetailView):
    model = OrdenDePago
    template_name = 'gestion/finanzas/ordenpago_detalle.html'
    context_object_name = 'orden_pago'

class OrdenDePagoCreateView(BaseFinanzasView, CreateView):
    model = OrdenDePago
    form_class = OrdenDePagoForm
    template_name = 'gestion/finanzas/ordenpago_form.html'
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['formset'] = DetalleOrdenDePagoFormset(self.request.POST)
        else:
            data['formset'] = DetalleOrdenDePagoFormset(queryset=OrdenDePagoDetalle.objects.none())
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if not formset.is_valid():
            messages.error(self.request, "Hay errores en los detalles de la Orden de Pago.")
            return self.form_invalid(form)
            
        # 🎯 Obtener Empleado y Validar
        empleado_instance = self.get_empleado_instance()
        if not empleado_instance:
            messages.error(self.request, "Error: Tu cuenta no está vinculada a un Empleado. No puedes crear Órdenes de Pago.")
            return self.form_invalid(form)
            
        try:
            with transaction.atomic():
                self.object = form.save(commit=False)
                self.object.empleado = empleado_instance 
                self.object.save()
                
                total_pago = Decimal('0.00')
                formset.instance = self.object
                detalles_guardados = formset.save(commit=False)
                
                for detalle in detalles_guardados:
                    if not detalle.pk: 
                         detalle.orden_pago = self.object
                    
                    #  Validación de saldo
                    cxp = detalle.cuenta_a_pagar
                    if detalle.monto_aplicado > cxp.monto_pendiente:
                         raise IntegrityError(f"Monto ({detalle.monto_aplicado}) excede el saldo pendiente en CxP #{cxp.pk} ({cxp.monto_pendiente}).")
                        
                    detalle.save()
                    total_pago += detalle.monto_aplicado
                
                # Manejo de eliminaciones
                formset.save_m2m()
                for deleted_form in formset.deleted_forms:
                    deleted_form.instance.delete()

                self.object.monto_total = total_pago 
                self.object.save(update_fields=['monto_total'])
                
                messages.success(self.request, f"Orden de Pago N°{self.object.pk} creada exitosamente.")
                return redirect('ordenpago_detalle', pk=self.object.pk)
        
        except IntegrityError as e:
            # Captura el error de saldo específicamente
            messages.error(self.request, f"Error de Saldo: {e}")
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f"Error al guardar la OP: {e}")
            return self.form_invalid(form)

class OrdenDePagoUpdateView(BaseFinanzasView, UpdateView):
    model = OrdenDePago
    form_class = OrdenDePagoForm
    template_name = 'gestion/finanzas/ordenpago_form.html'
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        op = self.get_object()
        if self.request.POST:
            data['formset'] = DetalleOrdenDePagoFormset(self.request.POST, instance=op)
        else:
            data['formset'] = DetalleOrdenDePagoFormset(instance=op)
        return data

    def form_valid(self, form):
        op = self.get_object()
        if op.estado != 'Pendiente': 
            messages.error(self.request, "Solo se pueden editar Órdenes de Pago con estado **PENDIENTE**.")
            return redirect('ordenpago_detalle', pk=op.pk)
            
        context = self.get_context_data()
        formset = context['formset']
        
        if not formset.is_valid():
            messages.error(self.request, "Hay errores en los detalles de la Orden de Pago.")
            return self.form_invalid(form)
            
        try:
            with transaction.atomic():
                self.object = form.save()
                
                formset.instance = self.object
                detalles_guardados = formset.save(commit=False)
                
                total_pago = Decimal('0.00')
                for detalle in detalles_guardados:
                    # ⚠️ Validación de saldo al actualizar
                    cxp = detalle.cuenta_a_pagar
                    if detalle.monto_aplicado > cxp.monto_pendiente: # Simplificación: si ya se aplicó pago, el monto pendiente es menor. Se necesitaría lógica más compleja para edición. Aquí solo valido que no exceda el pendiente.
                        raise IntegrityError(f"Monto ({detalle.monto_aplicado}) excede el saldo pendiente en CxP #{cxp.pk} ({cxp.monto_pendiente}).")
                        
                    detalle.save()
                    total_pago += detalle.monto_aplicado
                    
                formset.save_m2m()

                self.object.monto_total = total_pago
                self.object.save(update_fields=['monto_total'])
                
                messages.success(self.request, f"Orden de Pago N°{self.object.pk} actualizada exitosamente.")
                return redirect('ordenpago_detalle', pk=self.object.pk)
        
        except IntegrityError as e:
            messages.error(self.request, f"Error de Saldo al actualizar: {e}")
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f"Error al actualizar la OP: {e}")
            return self.form_invalid(form)
            
# --- Lógica de Procesamiento de OP (Aplica pagos a CxP) ---
class OrdenDePagoProcesarView(BaseFinanzasView, View):
    
    def post(self, request, pk):
        op = get_object_or_404(OrdenDePago, pk=pk)
        
        if op.estado != 'Pendiente':
            messages.warning(request, f"La Orden de Pago N°{op.pk} ya fue procesada o cancelada.")
            return redirect('ordenpago_detalle', pk=pk)
        
        if op.monto_total <= 0:
            messages.error(request, "La Orden de Pago no tiene monto total para aplicar.")
            return redirect('ordenpago_detalle', pk=pk)
        
        try:
            with transaction.atomic():
                for detalle_op in op.ordendepagodetalle_set.all():
                    cxp = detalle_op.cuenta_a_pagar
                    monto_aplicado = detalle_op.monto_aplicado
                    
                    # Validación de saldo (doble chequeo)
                    if monto_aplicado > cxp.monto_pendiente:
                         raise IntegrityError(f"El monto a aplicar ({monto_aplicado}) excede el pendiente ({cxp.monto_pendiente}) para la CxP N°{cxp.pk}.")
                    
                    # 1. Aplicar el pago a la Cuenta por Pagar (uso de F() atómico)
                    CuentaAPagar.objects.filter(pk=cxp.pk).update(
                        monto_pendiente=F('monto_pendiente') - monto_aplicado
                    )
                    cxp.refresh_from_db() # Recargar el objeto para tener el valor actualizado

                    # 2. Actualizar el estado de la Cuenta por Pagar
                    if cxp.monto_pendiente <= 0:
                        cxp.estado = 'Pagada'
                    else:
                        # Se mantiene en Pendiente o Parcial (si tu modelo tuviera ese estado)
                        cxp.estado = 'Pendiente' 
                        
                    cxp.save(update_fields=['estado'])
                    
                # 3. Actualizar el estado de la Orden de Pago
                op.estado = 'Pagada'
                op.save(update_fields=['estado'])
                
            messages.success(request, f"Orden de Pago N°{op.pk} procesada exitosamente. Pagos aplicados.")
            
        except IntegrityError as e:
            messages.error(request, f"ERROR DE PAGO (Transacción revertida): {e}")
        except Exception as e:
            messages.error(request, f"Error al procesar la Orden de Pago: {e}")
            
        return redirect('ordenpago_detalle', pk=pk)
        
class OrdenDePagoDeleteView(BaseFinanzasView, DeleteView):
    model = OrdenDePago
    template_name = 'gestion/confirm_delete.html'
    success_url = reverse_lazy('ordenpago_lista')
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.estado == 'Pagada':
            messages.error(request, f"No se puede eliminar la OP N°{self.object.pk} porque ya está PROCESADA/PAGADA.")
            return redirect('ordenpago_detalle', pk=self.object.pk)
        messages.success(request, f"Orden de Pago N°{self.object.pk} eliminada.")
        return super().post(request, *args, **kwargs)


# gestion/views_finanzas.py

from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import F, Sum
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction, IntegrityError
from decimal import Decimal 

# Mixins y Views genéricas de Django
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.views import View
from django.views.generic import DetailView, UpdateView, CreateView, ListView, DeleteView
from django.forms import inlineformset_factory 

# Importación de modelos (¡TODO CORREGIDO Y VERIFICADO!)
from .models import (
    Empleado, PerfilUsuario, 
    Producto, Compra, CuentaAPagar, Proveedor,
    OrdenDeCompra, OrdenDeCompraDetalle, DetalleCompra, 
    OrdenDePago, OrdenDePagoDetalle,
    DevolucionAProveedor, DevolucionAProveedorDetalle,
    InventarioMovimiento 
)

# Importación de formularios y formsets (de gestion/forms.py)
from .forms import (
    OrdenDeCompraForm, DetalleOrdenDeCompraForm,
    CuentaAPagarForm, 
    OrdenDePagoForm, DetalleOrdenDePagoForm,
    DevolucionAProveedorForm, DetalleDevolucionAProveedorForm
)

# ===================================================================
#  CONFIGURACIÓN DE FORMSETS
# ===================================================================

DetalleOrdenDeCompraFormset = inlineformset_factory(
    OrdenDeCompra, OrdenDeCompraDetalle, form=DetalleOrdenDeCompraForm, extra=1, can_delete=True
)
DetalleOrdenDePagoFormset = inlineformset_factory(
    OrdenDePago, OrdenDePagoDetalle, form=DetalleOrdenDePagoForm, extra=1, can_delete=True
)
DetalleDevolucionAProveedorFormset = inlineformset_factory(
    DevolucionAProveedor, DevolucionAProveedorDetalle, form=DetalleDevolucionAProveedorForm, extra=1, can_delete=True
)

# ===================================================================
#  CLASE BASE DE VISTA PARA MÓDULO DE FINANZAS
# ===================================================================

class BaseFinanzasView(LoginRequiredMixin, PermissionRequiredMixin):
    """Clase base que asegura que el usuario esté logueado y tenga permisos de staff."""
    # Requiere que el usuario sea staff para acceder al módulo de finanzas
    permission_required = 'is_staff' 
    
    def get_empleado_instance(self):
        """Intenta obtener la instancia de Empleado vinculada al usuario logueado."""
        try:
            perfil_usuario = PerfilUsuario.objects.get(user=self.request.user)
            # Retorna el empleado o None si el perfil no está vinculado a un empleado
            return perfil_usuario.empleado if hasattr(perfil_usuario, 'empleado') else None
        except PerfilUsuario.DoesNotExist:
            return None 
        except AttributeError:
            return None


# ===================================================================
# A. ORDEN DE COMPRA (OC) 
# ===================================================================

class OrdenDeCompraListView(BaseFinanzasView, ListView):
    model = OrdenDeCompra
    template_name = 'gestion/finanzas/ordencompra_lista.html'
    context_object_name = 'ordenes_compra'
    
    def get_queryset(self):
        # Muestra TODAS las órdenes
        return self.model.objects.all().order_by('-fecha_orden')

class OrdenDeCompraDetailView(BaseFinanzasView, DetailView):
    model = OrdenDeCompra
    template_name = 'gestion/finanzas/ordencompra_detalle.html'
    context_object_name = 'orden_compra'

class OrdenDeCompraCreateView(BaseFinanzasView, CreateView):
    model = OrdenDeCompra
    form_class = OrdenDeCompraForm
    template_name = 'gestion/finanzas/ordencompra_form.html'
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['formset'] = DetalleOrdenDeCompraFormset(self.request.POST)
        else:
            data['formset'] = DetalleOrdenDeCompraFormset(queryset=OrdenDeCompraDetalle.objects.none())
        data['titulo_pagina'] = 'Crear Nueva Orden de Compra'
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        # 1. Validar Formset
        if not formset.is_valid():
            messages.error(self.request, "Hay errores en los detalles de la Orden de Compra.")
            return self.form_invalid(form)

        # 2.  Obtener Empleado y Validar
        empleado_instance = self.get_empleado_instance()
        if not empleado_instance:
            messages.error(self.request, "Error: Tu cuenta no está vinculada a un Empleado. No puedes crear Órdenes de Compra.")
            return self.form_invalid(form)

        # 3. Guardar en Transacción
        try:
            with transaction.atomic():
                self.object = form.save(commit=False)
                self.object.empleado = empleado_instance 
                self.object.save()
                
                total = Decimal('0.00')
                formset.instance = self.object
                
                # Guarda los detalles (creación y edición)
                detalles_guardados = formset.save(commit=False)
                
                # Recalcular Subtotal y Total
                for detalle in detalles_guardados:
                    detalle.orden = self.object 
                    # Usamos precio_unitario, asumiendo que es el costo pactado
                    detalle.subtotal = detalle.cantidad * detalle.precio_unitario
                    detalle.save()
                    total += detalle.subtotal
                    
                # Manejo de eliminaciones
                formset.save_m2m() 
                for deleted_object in formset.deleted_objects:
                    deleted_object.delete()

                self.object.total = total
                self.object.save(update_fields=['total'])
                
                messages.success(self.request, f"Orden de Compra N°{self.object.pk} creada. Total: ${total}")
                return redirect('ordencompra_detalle', pk=self.object.pk)
        except Exception as e:
            messages.error(self.request, f"Error al guardar la OC: {e}")
            return self.form_invalid(form)


class OrdenDeCompraUpdateView(BaseFinanzasView, UpdateView):
    model = OrdenDeCompra
    form_class = OrdenDeCompraForm
    template_name = 'gestion/finanzas/ordencompra_form.html'
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        oc = self.get_object()
        if self.request.POST:
            data['formset'] = DetalleOrdenDeCompraFormset(self.request.POST, instance=oc)
        else:
            data['formset'] = DetalleOrdenDeCompraFormset(instance=oc)
        data['titulo_pagina'] = f'Editar Orden de Compra N°{oc.pk}'
        return data

    def form_valid(self, form):
        oc = self.get_object()
        if oc.estado != 'Pendiente': 
            messages.error(self.request, "Solo se pueden editar Órdenes de Compra con estado **PENDIENTE**.")
            return redirect('ordencompra_detalle', pk=oc.pk)
            
        context = self.get_context_data()
        formset = context['formset']
        
        if not formset.is_valid():
            messages.error(self.request, "Hay errores en los detalles de la Orden de Compra.")
            return self.form_invalid(form)
            
        try:
            with transaction.atomic():
                self.object = form.save()
                
                formset.instance = self.object
                formset.save() 
                
                # Recalcular el total basado en los detalles actuales
                total = Decimal('0.00')
                for detalle in self.object.ordendecompradetalle_set.all():
                    # Recalcular Subtotal y Total
                    detalle.subtotal = detalle.cantidad * detalle.precio_unitario
                    detalle.save(update_fields=['subtotal']) 
                    total += detalle.subtotal

                self.object.total = total
                self.object.save(update_fields=['total'])
                
                messages.success(self.request, f"Orden de Compra N°{self.object.pk} actualizada exitosamente.")
                return redirect('ordencompra_detalle', pk=self.object.pk)
        except Exception as e:
            messages.error(self.request, f"Error al actualizar la OC: {e}")
            return self.form_invalid(form)


# --- Lógica de Procesamiento de OC (Genera Compra y CxP) ---
class OrdenDeCompraProcesarView(BaseFinanzasView, View):
    
    def post(self, request, pk):
        oc = get_object_or_404(OrdenDeCompra, pk=pk)
        
        if oc.estado != 'Pendiente':
            messages.warning(request, f"La Orden de Compra N°{oc.pk} ya fue procesada o cancelada.")
            return redirect('ordencompra_detalle', pk=pk)
            
        if not oc.empleado:
            messages.error(request, "Error de Procesamiento: La OC no tiene Empleado asignado.")
            return redirect('ordencompra_detalle', pk=pk)
        
        detalles_oc = oc.ordendecompradetalle_set.all()
        if not detalles_oc.exists():
             messages.error(request, "Error de Procesamiento: La OC no tiene productos.")
             return redirect('ordencompra_detalle', pk=pk)
            
        try:
            with transaction.atomic():
                # 1. Crear la Compra asociada (Inventario)
                nueva_compra = Compra.objects.create(
                    proveedor=oc.proveedor,
                    empleado=oc.empleado,
                    total=oc.total,
                    estado='Recibida', # Se marca como Recibida al procesar la OC
                    # Aquí podrías asignar fecha_recepcion o usar la fecha actual
                )
                
                # 2. Crear los DetalleCompra (Actualiza stock via signals o aquí)
                for detalle_oc in detalles_oc:
                    DetalleCompra.objects.create(
                        compra=nueva_compra,
                        producto=detalle_oc.producto,
                        cantidad=detalle_oc.cantidad,
                        precio_compra=detalle_oc.precio_unitario, 
                        subtotal=detalle_oc.subtotal
                    )
                    #  Opcional: Registro de movimiento de inventario (si no usas signals)
                    InventarioMovimiento.objects.create(
                        producto=detalle_oc.producto,
                        tipo='ENTRADA',
                        cantidad=detalle_oc.cantidad,
                        descripcion=f'Recepción O.C. #{oc.pk} / Compra #{nueva_compra.pk}',
                    )
                    #  Opcional: Actualizar stock directamente (si no usas signals)
                    Producto.objects.filter(pk=detalle_oc.producto.pk).update(stock=F('stock') + detalle_oc.cantidad)

                # 3. Crear la Cuenta por Pagar (CxP)
                CuentaAPagar.objects.create(
                    proveedor=oc.proveedor,
                    compra=nueva_compra,
                    monto_original=oc.total,
                    monto_pendiente=oc.total,
                    fecha_vencimiento=oc.fecha_entrega_estimada, 
                    estado='Pendiente',
                )
                
                # 4. Actualizar el estado de la Orden de Compra
                oc.estado = 'Recibida'
                oc.compra_asociada = nueva_compra # Si tienes este campo FK
                oc.save(update_fields=['estado'])
                
            messages.success(request, f"Orden de Compra N°{oc.pk} procesada. Se creó **Compra N°{nueva_compra.pk}** y Cuenta por Pagar.")
            
        except IntegrityError as e:
            messages.error(request, f"Error de integridad en la base de datos (Transacción cancelada): {e}")
        except Exception as e:
            messages.error(request, f"Error al procesar la Orden de Compra: {e}")
            
        return redirect('ordencompra_detalle', pk=pk)

class OrdenDeCompraDeleteView(BaseFinanzasView, DeleteView):
    model = OrdenDeCompra
    template_name = 'gestion/confirm_delete.html'
    success_url = reverse_lazy('ordencompra_lista')
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.estado == 'Recibida':
            messages.error(request, f"No se puede eliminar la OC N°{self.object.pk} porque ya está PROCESADA/RECIBIDA.")
            return redirect('ordencompra_detalle', pk=self.object.pk)
        messages.success(request, f"Orden de Compra N°{self.object.pk} eliminada.")
        return super().post(request, *args, **kwargs)


# ===================================================================
# B. CUENTAS POR PAGAR (CxP) 
# ===================================================================

class CuentaAPagarListView(BaseFinanzasView, ListView):
    model = CuentaAPagar
    template_name = 'gestion/finanzas/cuentapagar_lista.html'
    context_object_name = 'cuentas_pagar'
    ordering = ['estado', 'fecha_vencimiento']
    
    def get_queryset(self):
        # Muestra cuentas pendientes, parciales y vencidas (excluye pagadas)
        return CuentaAPagar.objects.exclude(estado='Pagada').order_by('fecha_vencimiento') 

class CuentaAPagarDetailView(BaseFinanzasView, DetailView):
    model = CuentaAPagar
    template_name = 'gestion/finanzas/cuentapagar_detalle.html'
    context_object_name = 'cuenta_pagar'

class CuentaAPagarUpdateView(BaseFinanzasView, UpdateView):
    model = CuentaAPagar
    form_class = CuentaAPagarForm 
    template_name = 'gestion/finanzas/cuentapagar_form.html'
    
    def form_invalid(self, form):
        """Debug cuando el formulario no es válido"""
        print("=" * 50)
        print("DEBUG - FORMULARIO INVÁLIDO")
        print("=" * 50)
        
        # Imprimir todos los errores
        for field, errors in form.errors.items():
            print(f"Campo '{field}': {errors}")
        
        # Imprimir datos POST
        print("\nDatos POST recibidos:")
        for key, value in self.request.POST.items():
            print(f"  {key}: {value}")
        
        # Continuar con el comportamiento normal
        return super().form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('cuentapagar_detalle', kwargs={'pk': self.object.pk})

# ===================================================================
# C. ORDEN DE PAGO (OP) 💵
# ===================================================================

class OrdenDePagoListView(BaseFinanzasView, ListView):
    model = OrdenDePago
    template_name = 'gestion/finanzas/ordenpago_list.html'
    context_object_name = 'ordenes_pago'
    # Mostrar solo pendientes de pagar
    def get_queryset(self):
        return self.model.objects.filter(estado='Pendiente').order_by('-fecha_orden')

class OrdenDePagoDetailView(BaseFinanzasView, DetailView):
    model = OrdenDePago
    template_name = 'gestion/finanzas/ordenpago_detalle.html'
    context_object_name = 'orden_pago'

class OrdenDePagoCreateView(BaseFinanzasView, CreateView):
    model = OrdenDePago
    form_class = OrdenDePagoForm
    template_name = 'gestion/finanzas/ordenpago_form.html'
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['formset'] = DetalleOrdenDePagoFormset(self.request.POST)
        else:
            data['formset'] = DetalleOrdenDePagoFormset(queryset=OrdenDePagoDetalle.objects.none())
        data['titulo_pagina'] = 'Crear Nueva Orden de Pago'
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if not formset.is_valid():
            messages.error(self.request, "Hay errores en los detalles de la Orden de Pago.")
            return self.form_invalid(form)
            
        # 🎯 Obtener Empleado y Validar
        empleado_instance = self.get_empleado_instance()
        if not empleado_instance:
            messages.error(self.request, "Error: Tu cuenta no está vinculada a un Empleado. No puedes crear Órdenes de Pago.")
            return self.form_invalid(form)
            
        try:
            with transaction.atomic():
                self.object = form.save(commit=False)
                self.object.empleado = empleado_instance 
                self.object.save()
                
                total_pago = Decimal('0.00')
                formset.instance = self.object
                detalles_guardados = formset.save(commit=False)
                
                for detalle in detalles_guardados:
                    if not detalle.pk: 
                        detalle.orden_pago = self.object
                    
                    # ⚠️ Validación de saldo
                    cxp = detalle.cuenta_a_pagar
                    # Se usa get_object_or_404 para asegurar que la CxP existe antes de validar
                    cxp = get_object_or_404(CuentaAPagar, pk=cxp.pk)
                    
                    if detalle.monto_aplicado > cxp.monto_pendiente:
                        raise IntegrityError(f"Monto ({detalle.monto_aplicado}) excede el saldo pendiente en CxP #{cxp.pk} ({cxp.monto_pendiente}).")
                        
                    detalle.save()
                    total_pago += detalle.monto_aplicado
                
                # Manejo de eliminaciones
                formset.save_m2m()
                for deleted_object in formset.deleted_objects:
                    deleted_object.delete()

                self.object.monto_total = total_pago 
                self.object.save(update_fields=['monto_total'])
                
                messages.success(self.request, f"Orden de Pago N°{self.object.pk} creada exitosamente. Total a pagar: ${total_pago}")
                return redirect('ordenpago_detalle', pk=self.object.pk)
        
        except IntegrityError as e:
            # Captura el error de saldo específicamente
            messages.error(self.request, f"Error de Saldo: {e}")
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f"Error al guardar la OP: {e}")
            return self.form_invalid(form)

class OrdenDePagoUpdateView(BaseFinanzasView, UpdateView):
    model = OrdenDePago
    form_class = OrdenDePagoForm
    template_name = 'gestion/finanzas/ordenpago_form.html'
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        op = self.get_object()
        if self.request.POST:
            data['formset'] = DetalleOrdenDePagoFormset(self.request.POST, instance=op)
        else:
            data['formset'] = DetalleOrdenDePagoFormset(instance=op)
        data['titulo_pagina'] = f'Editar Orden de Pago N°{op.pk}'
        return data

    def form_valid(self, form):
        op = self.get_object()
        if op.estado != 'Pendiente': 
            messages.error(self.request, "Solo se pueden editar Órdenes de Pago con estado **PENDIENTE**.")
            return redirect('ordenpago_detalle', pk=op.pk)
            
        context = self.get_context_data()
        formset = context['formset']
        
        if not formset.is_valid():
            messages.error(self.request, "Hay errores en los detalles de la Orden de Pago.")
            return self.form_invalid(form)
            
        try:
            with transaction.atomic():
                self.object = form.save()
                
                formset.instance = self.object
                detalles_guardados = formset.save(commit=False) # Guardamos sin commit para validar

                total_pago = Decimal('0.00')
                for detalle in detalles_guardados:
                    # ⚠️ Validación de saldo al actualizar: Es más complejo, se asume que
                    # el formset de OP no permite seleccionar CxP ya pagadas y que el monto
                    # aplicado no puede exceder el pendiente restante.
                    cxp = detalle.cuenta_a_pagar
                    cxp = get_object_or_404(CuentaAPagar, pk=cxp.pk)
                    
                    # *Necesitarías lógica avanzada aquí para revertir pagos si se edita una OP ya procesada*
                    # Como la OP está en 'Pendiente' la validación simple es suficiente:
                    if detalle.monto_aplicado > cxp.monto_pendiente:
                        raise IntegrityError(f"Monto ({detalle.monto_aplicado}) excede el saldo pendiente en CxP #{cxp.pk} ({cxp.monto_pendiente}).")
                        
                    detalle.save()
                    total_pago += detalle.monto_aplicado
                    
                formset.save_m2m()
                for deleted_object in formset.deleted_objects:
                    deleted_object.delete()

                self.object.monto_total = total_pago
                self.object.save(update_fields=['monto_total'])
                
                messages.success(self.request, f"Orden de Pago N°{self.object.pk} actualizada exitosamente.")
                return redirect('ordenpago_detalle', pk=self.object.pk)
        
        except IntegrityError as e:
            messages.error(self.request, f"Error de Saldo al actualizar: {e}")
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f"Error al actualizar la OP: {e}")
            return self.form_invalid(form)
            
# --- Lógica de Procesamiento de OP (Aplica pagos a CxP) ---
class OrdenDePagoProcesarView(BaseFinanzasView, View):
    
    def post(self, request, pk):
        op = get_object_or_404(OrdenDePago, pk=pk)
        
        if op.estado != 'Pendiente':
            messages.warning(request, f"La Orden de Pago N°{op.pk} ya fue procesada o cancelada.")
            return redirect('ordenpago_detalle', pk=pk)
        
        detalles_op = op.ordendepagodetalle_set.all()
        if not detalles_op.exists() or op.monto_total <= 0:
            messages.error(request, "La Orden de Pago no tiene monto total o detalles para aplicar.")
            return redirect('ordenpago_detalle', pk=pk)
        
        try:
            with transaction.atomic():
                for detalle_op in detalles_op:
                    cxp = detalle_op.cuenta_a_pagar
                    monto_aplicado = detalle_op.monto_aplicado
                    
                    # Validación de saldo (doble chequeo)
                    cxp.refresh_from_db() 
                    if monto_aplicado > cxp.monto_pendiente:
                        raise IntegrityError(f"El monto a aplicar ({monto_aplicado}) excede el pendiente ({cxp.monto_pendiente}) para la CxP N°{cxp.pk}.")
                    
                    # 1. Aplicar el pago a la Cuenta por Pagar (uso de F() atómico)
                    CuentaAPagar.objects.filter(pk=cxp.pk).update(
                        monto_pendiente=F('monto_pendiente') - monto_aplicado
                    )
                    cxp.refresh_from_db() # Recargar el objeto para tener el valor actualizado

                    # 2. Actualizar el estado de la Cuenta por Pagar
                    if cxp.monto_pendiente <= 0:
                        cxp.estado = 'Pagada'
                    elif cxp.monto_pendiente < cxp.monto_original:
                        cxp.estado = 'Parcial' # Si tu modelo tiene Parcial
                    # Si no, se queda en 'Pendiente'

                    cxp.save(update_fields=['estado'])
                    
                # 3. Actualizar el estado de la Orden de Pago
                op.estado = 'Pagada'
                op.save(update_fields=['estado'])
                
            messages.success(request, f"Orden de Pago N°{op.pk} procesada exitosamente. Pagos aplicados (${op.monto_total}).")
            
        except IntegrityError as e:
            messages.error(request, f"ERROR DE PAGO (Transacción revertida): {e}")
        except Exception as e:
            messages.error(request, f"Error al procesar la Orden de Pago: {e}")
            
        return redirect('ordenpago_detalle', pk=pk)
        
class OrdenDePagoDeleteView(BaseFinanzasView, DeleteView):
    model = OrdenDePago
    template_name = 'gestion/confirm_delete.html'
    success_url = reverse_lazy('ordenpago_lista')
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.estado == 'Pagada':
            messages.error(request, f"No se puede eliminar la OP N°{self.object.pk} porque ya está PROCESADA/PAGADA. Se debe revertir el pago manualmente.")
            return redirect('ordenpago_detalle', pk=self.object.pk)
        messages.success(request, f"Orden de Pago N°{self.object.pk} eliminada.")
        return super().post(request, *args, **kwargs)
    

# ===================================================================
# D. DEVOLUCIÓN A PROVEEDOR (DAP) ↩️
# ===================================================================

class DevolucionAProveedorListView(BaseFinanzasView, ListView):
    model = DevolucionAProveedor
    template_name = 'gestion/devolucion_a_proveedor/devolucionaproveedor_list.html'
    context_object_name = 'object_list'
    ordering = ['-fecha']
    
    def get_template_names(self):
        return [self.template_name]

class DevolucionAProveedorDetailView(BaseFinanzasView, DetailView):
    model = DevolucionAProveedor
    template_name = 'gestion/devolucion_a_proveedor/devolucionaproveedor_detail.html'
    context_object_name = 'devolucion'

class DevolucionAProveedorCreateView(BaseFinanzasView, CreateView):
    model = DevolucionAProveedor
    form_class = DevolucionAProveedorForm
    template_name = 'gestion/devolucion_a_proveedor/devolucionaproveedor_form.html'
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['formset'] = DetalleDevolucionAProveedorFormset(self.request.POST)
        else:
            data['formset'] = DetalleDevolucionAProveedorFormset(queryset=DevolucionAProveedorDetalle.objects.none())
        data['titulo_pagina'] = 'Crear Devolución a Proveedor'
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if not formset.is_valid():
            messages.error(self.request, "Hay errores en los detalles de la Devolución.")
            return self.form_invalid(form)

        empleado_instance = self.get_empleado_instance()
        
        try:
            with transaction.atomic():
                self.object = form.save(commit=False)
                
                # ⚠️ SOLO si el modelo tiene campo 'empleado', descomenta:
                # self.object.empleado = empleado_instance
                
                # 🔥 CORREGIDO: Usar 'PENDIENTE' en mayúsculas (como en el modelo)
                self.object.estado = 'PENDIENTE'
                self.object.save()
                
                total_devolucion = Decimal('0.00')
                formset.instance = self.object
                detalles_guardados = formset.save(commit=False)
                
                for detalle in detalles_guardados:
                    if not detalle.pk: 
                        detalle.devolucion = self.object
                    # El save() del modelo ya calcula subtotal, pero por si acaso:
                    detalle.subtotal = Decimal(detalle.cantidad) * detalle.precio_devuelto 
                    detalle.save() 
                    total_devolucion += detalle.subtotal 
                
                formset.save_m2m()
                for deleted_object in formset.deleted_objects:
                    deleted_object.delete()
                
                # 🔥 CORREGIDO: Usar 'total' (NO 'total_devuelto')
                self.object.total = total_devolucion 
                self.object.save(update_fields=['total', 'estado'])
                
                messages.success(self.request, f"Devolución N°{self.object.pk} creada exitosamente.")
                return redirect('devolucionproveedor_detalle', pk=self.object.pk)
        except Exception as e:
            import traceback
            traceback.print_exc()  # Para debug
            messages.error(self.request, f"Error al guardar la Devolución: {str(e)}")
            return self.form_invalid(form)


class DevolucionAProveedorUpdateView(BaseFinanzasView, UpdateView):
    model = DevolucionAProveedor
    form_class = DevolucionAProveedorForm
    template_name = 'gestion/devolucion_a_proveedor/devolucionaproveedor_form.html'
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        dap = self.get_object()
        if self.request.POST:
            data['formset'] = DetalleDevolucionAProveedorFormset(self.request.POST, instance=dap)
        else:
            data['formset'] = DetalleDevolucionAProveedorFormset(instance=dap)
        data['titulo_pagina'] = f'Editar Devolución N°{dap.pk}'
        return data

    def form_valid(self, form):
        dap = self.get_object()
        # 🔥 CORREGIDO: Usar 'PENDIENTE' en mayúsculas
        if dap.estado != 'PENDIENTE': 
            messages.error(self.request, "Solo se pueden editar Devoluciones con estado **PENDIENTE**.")
            return redirect('devolucionproveedor_detalle', pk=dap.pk)
            
        context = self.get_context_data()
        formset = context['formset']
        
        if not formset.is_valid():
            messages.error(self.request, "Hay errores en los detalles de la Devolución.")
            return self.form_invalid(form)
            
        try:
            with transaction.atomic():
                self.object = form.save()
                formset.instance = self.object
                formset.save()
                
                total_devolucion = Decimal('0.00')
                # 🔥 CORREGIDO: Usar 'detalles' (related_name del modelo)
                for detalle in self.object.detalles.all():
                    detalle.subtotal = Decimal(detalle.cantidad) * detalle.precio_devuelto 
                    detalle.save(update_fields=['subtotal']) 
                    total_devolucion += detalle.subtotal 
                
                # 🔥 CORREGIDO: Usar 'total' (NO 'total_devuelto')
                self.object.total = total_devolucion 
                self.object.save(update_fields=['total'])
                
                messages.success(self.request, f"Devolución N°{self.object.pk} actualizada exitosamente.")
                return redirect('devolucionproveedor_detalle', pk=self.object.pk)
        except Exception as e:
            import traceback
            traceback.print_exc()  # Para debug
            messages.error(self.request, f"Error al actualizar la Devolución: {str(e)}")
            return self.form_invalid(form)

# --- Lógica de Procesamiento de DAP (Ajusta Stock y CxP) ---
class DevolucionAProveedorProcesarView(BaseFinanzasView, View):
    
    def post(self, request, pk):
        dap = get_object_or_404(DevolucionAProveedor, pk=pk)
        
        # 🔥 CORREGIDO: Usar 'PENDIENTE' en mayúsculas
        if dap.estado != 'PENDIENTE':
            messages.warning(request, f"La Devolución N°{dap.pk} ya fue procesada.")
            return redirect('devolucionproveedor_detalle', pk=pk)
            
        # 🔥 CORREGIDO: Usar 'detalles' (related_name)
        detalles_dap = dap.detalles.all()
        if not detalles_dap.exists():
            messages.error(request, "Error de Procesamiento: La Devolución no tiene productos.")
            return redirect('devolucionproveedor_detalle', pk=pk)
            
        try:
            with transaction.atomic():
                total_devolucion = Decimal('0.00')
                
                # 1. Ajuste de Stock (Salida)
                for detalle_dap in detalles_dap:
                    producto = detalle_dap.producto
                    cantidad = detalle_dap.cantidad
                    total_devolucion += detalle_dap.subtotal
                    
                    # Validación de Stock
                    producto.refresh_from_db() 
                    if producto.stock < cantidad:
                        raise IntegrityError(f"Stock insuficiente para Devolución del producto **{producto.nombre}**. Disponible: {producto.stock}, Solicitado: {cantidad}.")
                        
                    Producto.objects.filter(pk=producto.pk).update(stock=F('stock') - cantidad)
                    
                    # Registro de InventarioMovimiento 
                    InventarioMovimiento.objects.create(
                        producto=producto,
                        tipo='SALIDA',
                        cantidad=cantidad,
                        descripcion=f'Devolución a Proveedor #{dap.pk}',
                    )
                        
                # 2. Ajustar la Cuenta por Pagar asociada (Nota de Crédito)
                compra_original = dap.compra_original
                mensaje_cxp = "No hay Compra Original asociada. Solo se ajustó el stock."
                
                if compra_original: 
                    cxp_queryset = CuentaAPagar.objects.filter(compra=compra_original).exclude(estado='Pagada')
                    
                    if cxp_queryset.exists():
                        cxp = cxp_queryset.first()
                        monto_a_reducir = total_devolucion
                        
                        # Si el monto a devolver excede el saldo pendiente
                        if monto_a_reducir > cxp.monto_pendiente:
                            monto_a_reducir = cxp.monto_pendiente
                            messages.warning(request, "El monto a devolver excedía el saldo pendiente. Solo se redujo el saldo pendiente a cero.")
                            
                        # Reducir el saldo pendiente (uso de F() atómico)
                        CuentaAPagar.objects.filter(pk=cxp.pk).update(
                            monto_pendiente=F('monto_pendiente') - monto_a_reducir
                        )
                        cxp.refresh_from_db()
                        
                        # Actualizar estado de CxP
                        if cxp.monto_pendiente <= 0:
                            cxp.estado = 'Pagada'
                        elif cxp.monto_pendiente < cxp.monto_original:
                            cxp.estado = 'Parcial'
                        else:
                            cxp.estado = 'Pendiente'
                            
                        cxp.save(update_fields=['estado'])
                        mensaje_cxp = f"Saldo de Cuenta por Pagar N°{cxp.pk} ajustado en ${monto_a_reducir}."
                    else:
                        mensaje_cxp = f"ADVERTENCIA: No se encontró Cuenta por Pagar pendiente para la Compra N°{compra_original.pk}. Se debe generar Nota de Crédito."
                
                # 3. Finalizar la Devolución
                # 🔥 CORREGIDO: Usar 'total' (NO 'total_devuelto') y 'PROCESADA' en mayúsculas
                dap.total = total_devolucion
                dap.estado = 'PROCESADA'
                dap.save(update_fields=['total', 'estado'])
                
                messages.success(request, f"Devolución N°{dap.pk} procesada exitosamente. Stock ajustado. {mensaje_cxp}")
                
        except IntegrityError as e:
            messages.error(request, f"ERROR DE STOCK o SALDO (Transacción revertida): {e}")
        except Exception as e:
            import traceback
            traceback.print_exc()  # Para debug
            messages.error(request, f"Error al procesar la Devolución a Proveedor: {e}")
            
        return redirect('devolucionproveedor_detalle', pk=pk)

class DevolucionAProveedorDeleteView(BaseFinanzasView, DeleteView):
    model = DevolucionAProveedor
    template_name = 'gestion/confirm_delete.html'
    success_url = reverse_lazy('devolucionproveedor_lista')
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        # 🔥 CORREGIDO: Usar 'PROCESADA' en mayúsculas
        if self.object.estado == 'PROCESADA':
            messages.error(request, f"No se puede eliminar la Devolución N°{self.object.pk} porque ya fue PROCESADA. Se debe revertir la acción manualmente.")
            return redirect('devolucionproveedor_detalle', pk=self.object.pk)
        messages.success(request, f"Devolución N°{self.object.pk} eliminada.")
        return super().post(request, *args, **kwargs)
    
# ===================================================================
# E. CUENTAS POR COBRAR (CxC) 💰
# ===================================================================

class CuentaACobrarListView(BaseFinanzasView, ListView):
    """Listado de cuentas por cobrar a clientes."""
    model = CuentaACobrar
    template_name = 'gestion/finanzas/cuentacobrar_lista.html'
    context_object_name = 'cuentas_cobrar'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = CuentaACobrar.objects.select_related('cliente', 'venta').all()
        
        # Filtros
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        cliente_id = self.request.GET.get('cliente')
        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)
        
        # Filtrar vencidas
        if self.request.GET.get('vencidas') == 'true':
            queryset = queryset.filter(
                estado='Pendiente',
                fecha_vencimiento__lt=timezone.now().date()
            )
        
        return queryset.order_by('-fecha_vencimiento')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas
        queryset = self.get_queryset()
        
        # Totales
        context['total_pendiente'] = queryset.filter(
            estado='Pendiente'
        ).aggregate(total=Sum('monto_pendiente'))['total'] or Decimal('0.00')
        
        context['total_vencido'] = queryset.filter(
            Q(estado='Pendiente') & Q(fecha_vencimiento__lt=timezone.now().date())
        ).aggregate(total=Sum('monto_pendiente'))['total'] or Decimal('0.00')
        
        # Contadores
        context['pendientes_count'] = queryset.filter(estado='Pendiente').count()
        context['pagadas_count'] = queryset.filter(estado='Pagada').count()
        context['vencidas_count'] = queryset.filter(
            Q(estado='Pendiente') & Q(fecha_vencimiento__lt=timezone.now().date())
        ).count()
        
        # Para filtros
        context['clientes'] = Cliente.objects.all()
        
        context['titulo_pagina'] = 'Cuentas por Cobrar'
        return context


class CuentaACobrarDetailView(BaseFinanzasView, DetailView):
    """Detalle de una cuenta por cobrar."""
    model = CuentaACobrar
    template_name = 'gestion/finanzas/cuentacobrar_detalle.html'
    context_object_name = 'cuenta_cobrar'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener cobros relacionados
        cobros_detalle = CobroDetalle.objects.filter(
            cuenta_a_cobrar=self.object
        ).select_related('cobro')
        
        context['cobros_detalle'] = cobros_detalle
        context['total_cobrado'] = cobros_detalle.aggregate(
            total=Sum('monto_aplicado')
        )['total'] or Decimal('0.00')
        
        # Calcular días vencidos
        if self.object.estado == 'Pendiente' and self.object.fecha_vencimiento < timezone.now().date():
            context['dias_vencidos'] = (timezone.now().date() - self.object.fecha_vencimiento).days
        else:
            context['dias_vencidos'] = 0
            
        context['titulo_pagina'] = f'Cuenta por Cobrar #{self.object.id}'
        return context


class CuentaACobrarCreateView(BaseFinanzasView, CreateView):
    """Crear nueva cuenta por cobrar."""
    model = CuentaACobrar
    form_class = CuentaACobrarForm
    template_name = 'gestion/finanzas/cuentacobrar_form.html'
    
    def get_success_url(self):
        return reverse_lazy('cuentacobrar_lista')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filtrar ventas pendientes de pago
        form.fields['venta'].queryset = Venta.objects.filter(
            estado='FINALIZADA'  # Ajusta según tus estados
        ).exclude(
            id__in=CuentaACobrar.objects.values_list('venta_id', flat=True)
        )
        return form
    
    def form_valid(self, form):
        # Establecer monto_pendiente igual a monto_original si no se especifica
        if not form.instance.monto_pendiente:
            form.instance.monto_pendiente = form.instance.monto_original
        
        return super().form_valid(form)
    
class CuentaACobrarUpdateView(BaseFinanzasView, UpdateView):
    """Editar una cuenta por cobrar existente."""
    model = CuentaACobrar
    form_class = CuentaACobrarForm
    template_name = 'gestion/finanzas/cuentacobrar_form.html'
    
    def get_success_url(self):
        return reverse_lazy('cuentacobrar_detalle', kwargs={'pk': self.object.id})
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Para edición, permitir cualquier venta (incluso las que ya tienen cuenta)
        form.fields['venta'].queryset = Venta.objects.filter(
            estado='FINALIZADA'
        )
        return form

# ===================================================================
# F. GESTIÓN DE CAJAS 🏦
# ===================================================================

class CajaListView(BaseFinanzasView, ListView):
    """Listado de cajas/arqueos."""
    model = Caja
    template_name = 'gestion/finanzas/caja_lista.html'
    context_object_name = 'cajas'
    paginate_by = 20
    
    def get_queryset(self):
        # Ordenar por fecha de apertura descendente
        return Caja.objects.select_related('empleado_responsable').order_by('-fecha_apertura')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Verificar si hay cajas abiertas
        cajas_abiertas = Caja.objects.filter(estado='Abierta')
        
        # Contexto para el template
        context['caja_abierta'] = cajas_abiertas.first() if cajas_abiertas.exists() else None
        context['cajas_abiertas'] = cajas_abiertas  # ¡ESTA ES LA QUE FALTABA!
        context['cajas_abiertas_count'] = cajas_abiertas.count()
        
        # Estadísticas
        cajas_cerradas = Caja.objects.filter(estado='Cerrada')
        context['total_cajas'] = Caja.objects.count()
        context['cajas_cerradas_count'] = cajas_cerradas.count()
        
        # Suma de montos iniciales
        context['total_monto_inicial'] = Caja.objects.aggregate(
            total=Sum('monto_inicial')
        )['total'] or Decimal('0.00')
        
        # Para mostrar mensaje de advertencia en la creación
        if cajas_abiertas.exists():
            context['ya_existe_caja_abierta'] = True
            context['caja_abierta_actual'] = cajas_abiertas.first()
        else:
            context['ya_existe_caja_abierta'] = False
            
        context['titulo_pagina'] = 'Gestión de Cajas'
        return context



class CajaDetailView(BaseFinanzasView, DetailView):
    """Detalle de una caja."""
    model = Caja
    template_name = 'gestion/finanzas/caja_detalle.html'
    context_object_name = 'caja'
    
    def get_object(self, queryset=None):
        """Obtener el objeto y debuguear."""
        obj = super().get_object(queryset)
        
        # DEBUG: Imprimir en consola
        print(f"DEBUG CajaDetailView - ID: {obj.id}")
        print(f"DEBUG CajaDetailView - Nombre: {obj.nombre}")
        print(f"DEBUG CajaDetailView - Responsable: {obj.empleado_responsable}")
        
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # DEBUG
        print(f"DEBUG - Contexto caja: {self.object}")
        
        # Obtener arqueos relacionados
        arqueos = Arqueo.objects.filter(caja=self.object).select_related('empleado').order_by('-fecha_arqueo')
        print(f"DEBUG - Arqueos encontrados: {arqueos.count()}")
        
        # Obtener cobros relacionados (si existen)
        cobros = Cobro.objects.filter(caja=self.object).select_related('cliente', 'moneda').order_by('-fecha_cobro')
        print(f"DEBUG - Cobros encontrados: {cobros.count()}")
        
        context['arqueos'] = arqueos
        context['cobros'] = cobros
        context['ultimo_arqueo'] = arqueos.first() if arqueos.exists() else None
        
        # Calcular total cobrado en esta caja
        if cobros.exists():
            context['total_cobrado'] = cobros.aggregate(
                total=Sum('monto_total')
            )['total'] or Decimal('0.00')
        else:
            context['total_cobrado'] = Decimal('0.00')
            
        context['titulo_pagina'] = f'Caja {self.object.nombre}'
        
        # DEBUG final
        print(f"DEBUG - Contexto completo: {context.keys()}")
        
        return context

class CajaCreateView(BaseFinanzasView, CreateView):
    """Crear nueva caja."""
    model = Caja
    form_class = CajaForm
    template_name = 'gestion/finanzas/caja_form.html'
    
    def get_success_url(self):
        return reverse_lazy('caja_detalle', kwargs={'pk': self.object.pk})
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        
        # CORRECCIÓN: Solo muestra todos los empleados (sin filtrar por estado)
        form.fields['empleado_responsable'].queryset = Empleado.objects.all()
        
        # Si quieres ordenarlos alfabéticamente:
        form.fields['empleado_responsable'].queryset = Empleado.objects.all().order_by('nombre', 'apellido')
        
        # Opción: Si luego agregas un campo 'activo' booleano
        # form.fields['empleado_responsable'].queryset = Empleado.objects.filter(activo=True)
        
        # Comenta esta parte si no tienes relación User-Empleado
        # if self.request.user.is_authenticated:
        #     try:
        #         # Si no existe self.request.user.empleado, esto fallará
        #         empleado = self.request.user.empleado
        #         form.initial['empleado_responsable'] = empleado
        #     except AttributeError:
        #         # Si no hay relación, no hagas nada
        #         pass
        
        return form
    
    def form_valid(self, form):
        # Verificar si ya hay cajas abiertas
        cajas_abiertas = Caja.objects.filter(estado='Abierta')
        
        if cajas_abiertas.exists():
            form.add_error(None, 'Ya existe una caja abierta. Debe cerrarla antes de abrir una nueva.')
            return self.form_invalid(form)
        
        # Establecer estado inicial
        form.instance.estado = 'Abierta'
        
        # Guardar
        response = super().form_valid(form)
        
        # Mensaje de éxito
        messages.success(self.request, f'Caja "{form.instance.nombre}" abierta exitosamente.')
        
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Abrir Nueva Caja'
        
        # Verificar si ya hay caja abierta
        cajas_abiertas = Caja.objects.filter(estado='Abierta')
        context['ya_existe_caja_abierta'] = cajas_abiertas.exists()
        if cajas_abiertas.exists():
            context['caja_abierta_actual'] = cajas_abiertas.first()
            
        return context


class CajaUpdateView(BaseFinanzasView, UpdateView):
    """Actualizar caja (por ejemplo, para cerrarla)."""
    model = Caja
    form_class = CajaForm
    template_name = 'gestion/finanzas/caja_form.html'
    
    def get_success_url(self):
        return reverse_lazy('caja_detalle', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        # Lógica adicional al actualizar
        if form.instance.estado == 'Cerrada' and not form.instance.fecha_cierre:
            form.instance.fecha_cierre = timezone.now()
        
        return super().form_valid(form)
    
class CajaCerrarView(BaseFinanzasView, UpdateView):
    """Cerrar una caja."""
    model = Caja
    template_name = 'gestion/finanzas/caja_cerrar.html'
    fields = []  # No necesitamos campos del formulario
    
    def get_success_url(self):
        return reverse_lazy('caja_lista')
    
    def form_valid(self, form):
        # Solo permitir cerrar cajas abiertas
        if self.object.estado == 'Abierta':
            self.object.estado = 'Cerrada'
            self.object.fecha_cierre = timezone.now()
            messages.success(self.request, f'Caja "{self.object.nombre}" cerrada exitosamente.')
        else:
            messages.error(self.request, 'Esta caja ya está cerrada.')
        
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = f'Cerrar Caja: {self.object.nombre}'
        return context
    
    # ===================================================================
# G. COBROS 💵
# ===================================================================

class CobroCreateView(BaseFinanzasView, CreateView):
    """Registrar un nuevo cobro."""
    model = Cobro
    form_class = CobroForm
    template_name = 'gestion/finanzas/cobro_form.html'
    
    def get_success_url(self):
        return reverse_lazy('caja_detalle', kwargs={'pk': self.object.caja.pk})
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        
        # Filtrar cajas abiertas
        form.fields['caja'].queryset = Caja.objects.filter(estado='Abierta')
        
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Agregar el formset para detalles de cobro
        if self.request.POST:
            context['detalle_formset'] = CobroDetalleFormset(
                self.request.POST, 
                instance=self.object if self.object.pk else None
            )
        else:
            context['detalle_formset'] = CobroDetalleFormset(
                instance=self.object if self.object.pk else None
            )
        
        # Obtener cuentas por cobrar pendientes
        context['cuentas_pendientes'] = CuentaACobrar.objects.filter(
            estado='Pendiente'
        ).select_related('cliente')
        
        context['titulo_pagina'] = 'Registrar Cobro'
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        detalle_formset = context['detalle_formset']
        
        with transaction.atomic():
            self.object = form.save()
            
            if detalle_formset.is_valid():
                detalle_formset.instance = self.object
                detalle_formset.save()
                
                # Actualizar total del cobro
                total_cobrado = self.object.cobrodetalle_set.aggregate(
                    total=Sum('monto_aplicado')
                )['total'] or Decimal('0.00')
                
                self.object.monto_total = total_cobrado
                self.object.save()
                
                # Actualizar cuentas por cobrar
                for detalle in self.object.cobrodetalle_set.all():
                    cuenta = detalle.cuenta_a_cobrar
                    cuenta.monto_pendiente -= detalle.monto_aplicado
                    
                    if cuenta.monto_pendiente <= 0:
                        cuenta.estado = 'Pagada'
                        cuenta.monto_pendiente = Decimal('0.00')
                    
                    cuenta.save()
            else:
                return self.form_invalid(form)
        
        messages.success(self.request, f'Cobro registrado exitosamente por ${self.object.monto_total:.2f}')
        return super().form_valid(form)

# ===================================================================
# H. ARQUEO DE CAJA 📊
# ===================================================================

class ArqueoCreateView(BaseFinanzasView, CreateView):
    """Realizar arqueo de caja."""
    model = Arqueo
    form_class = ArqueoForm
    template_name = 'gestion/finanzas/arqueo_form.html'
    
    def get_success_url(self):
        return reverse_lazy('caja_detalle', kwargs={'pk': self.object.caja.pk})
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        
        # Filtrar cajas abiertas
        form.fields['caja'].queryset = Caja.objects.filter(estado='Abierta')
        
        # Establecer empleado actual
        if self.request.user.is_authenticated:
            try:
                empleado = self.request.user.empleado
                form.initial['empleado'] = empleado
            except:
                pass
        
        # Calcular monto del sistema
        caja_id = self.request.GET.get('caja')
        if caja_id:
            try:
                caja = Caja.objects.get(id=caja_id)
                cobros = Cobro.objects.filter(caja=caja)
                total_cobrado = cobros.aggregate(total=Sum('monto_total'))['total'] or Decimal('0.00')
                monto_sistema = caja.monto_inicial + total_cobrado
                form.initial['monto_sistema'] = monto_sistema
                form.initial['caja'] = caja
            except (Caja.DoesNotExist, ValueError):
                pass
        
        return form
    
    def form_valid(self, form):
        """Procesar el formulario válido"""
        from decimal import Decimal
        from django.db import transaction
        from django.utils import timezone
        
        # DEBUG: Verificar valores
        monto_contado = form.cleaned_data['monto_contado']
        monto_sistema = form.cleaned_data['monto_sistema']
        
        print("=" * 50)
        print("DEBUG - ArqueoCreateView.form_valid()")
        print("=" * 50)
        print(f"monto_contado: {monto_contado}")
        print(f"monto_sistema: {monto_sistema}")
        print(f"tipo monto_contado: {type(monto_contado)}")
        print(f"tipo monto_sistema: {type(monto_sistema)}")
        
        # Asegurar que sean Decimal
        if not isinstance(monto_contado, Decimal):
            monto_contado = Decimal(str(monto_contado))
        if not isinstance(monto_sistema, Decimal):
            monto_sistema = Decimal(str(monto_sistema))
        
        # Calcular diferencia
        diferencia = monto_contado - monto_sistema
        print(f"diferencia calculada: {diferencia}")
        
        form.instance.diferencia = diferencia
        print(f"diferencia asignada: {form.instance.diferencia}")
        print("=" * 50)
        
        # Verificar si la caja se va a cerrar después del arqueo
        cerrar_caja = self.request.POST.get('cerrar_caja') == 'true'
        
        with transaction.atomic():
            # Guardar el arqueo
            response = super().form_valid(form)
            
            if cerrar_caja:
                # Cerrar la caja
                caja = form.instance.caja
                caja.estado = 'Cerrada'
                caja.fecha_cierre = timezone.now()
                caja.save()
                
                messages.success(
                    self.request, 
                    f'Arqueo realizado y caja "{caja.nombre}" cerrada exitosamente. '
                    f'Diferencia: ${diferencia}'
                )
            else:
                messages.success(
                    self.request, 
                    f'Arqueo realizado exitosamente. Diferencia: ${diferencia}'
                )
        
        return response
    # ===================================================================
# I. INFORMES FINANCIEROS 📈
# ===================================================================

class EstadoCuentasView(BaseFinanzasView, TemplateView):
    """Dashboard de estado de cuentas"""
    template_name = 'gestion/finanzas/estado_cuentas.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Debug
        print("DEBUG - EstadoCuentasView ejecutándose")
        print("DEBUG - Cuentas por cobrar:", CuentaACobrar.objects.count())
        print("DEBUG - Cuentas por pagar:", CuentaAPagar.objects.count())

        # Filtros desde URL
        filtro_cliente = self.request.GET.get('cliente', '')
        filtro_proveedor = self.request.GET.get('proveedor', '')
        filtro_estado = self.request.GET.get('estado', '')
        filtro_vencimiento = self.request.GET.get('vencimiento', '')
        
        # ===== CUENTAS POR COBRAR =====
        cuentas_cobrar = CuentaACobrar.objects.select_related('cliente', 'venta')
        
        # Aplicar filtros
        if filtro_cliente:
            cuentas_cobrar = cuentas_cobrar.filter(
                Q(cliente__nombre__icontains=filtro_cliente) |
                Q(cliente__apellido__icontains=filtro_cliente)
            )
        
        if filtro_estado:
            cuentas_cobrar = cuentas_cobrar.filter(estado=filtro_estado)
        
        if filtro_vencimiento == 'vencidas':
            cuentas_cobrar = cuentas_cobrar.filter(fecha_vencimiento__lt=date.today())
        elif filtro_vencimiento == 'por_vencer':
            cuentas_cobrar = cuentas_cobrar.filter(fecha_vencimiento__gte=date.today())
        
        # Totales
        total_por_cobrar = cuentas_cobrar.aggregate(
            total=Sum('monto_pendiente')
        )['total'] or Decimal('0.00')
        
        vencidas_por_cobrar = cuentas_cobrar.filter(
            fecha_vencimiento__lt=date.today(),
            estado='Pendiente'
        ).aggregate(total=Sum('monto_pendiente'))['total'] or Decimal('0.00')
        
        # ===== CUENTAS POR PAGAR =====
        
        cuentas_pagar = CuentaAPagar.objects.exclude(estado='Pagada').select_related('proveedor', 'compra')
        if filtro_proveedor:
            cuentas_pagar = cuentas_pagar.filter(
                proveedor__nombre__icontains=filtro_proveedor
            )
        
        if filtro_estado:
            cuentas_pagar = cuentas_pagar.filter(estado=filtro_estado)
        
        if filtro_vencimiento == 'vencidas':
            cuentas_pagar = cuentas_pagar.filter(fecha_vencimiento__lt=date.today())
        elif filtro_vencimiento == 'por_vencer':
            cuentas_pagar = cuentas_pagar.filter(fecha_vencimiento__gte=date.today())
        
        # Totales
        total_por_pagar = cuentas_pagar.aggregate(
            total=Sum('monto_pendiente')
        )['total'] or Decimal('0.00')
        
        vencidas_por_pagar = cuentas_pagar.filter(
            fecha_vencimiento__lt=date.today(),
            estado='Pendiente'
        ).aggregate(total=Sum('monto_pendiente'))['total'] or Decimal('0.00')
        
        # ===== RESUMEN GENERAL =====
        clientes_con_deuda = cuentas_cobrar.values('cliente').distinct().count()
        proveedores_con_deuda = cuentas_pagar.values('proveedor').distinct().count()
        
        saldo_neto = total_por_cobrar - total_por_pagar
        
        context.update({
            'titulo_pagina': 'Estado de Cuentas',
            
            # Cuentas por Cobrar
            'cuentas_cobrar': cuentas_cobrar.order_by('fecha_vencimiento'),
            'total_por_cobrar': total_por_cobrar,
            'vencidas_por_cobrar': vencidas_por_cobrar,
            'clientes_con_deuda': clientes_con_deuda,
            
            # Cuentas por Pagar
            'cuentas_pagar': cuentas_pagar.order_by('fecha_vencimiento'),
            'total_por_pagar': total_por_pagar,
            'vencidas_por_pagar': vencidas_por_pagar,
            'proveedores_con_deuda': proveedores_con_deuda,
            
            # Resumen
            'saldo_neto': saldo_neto,
            
            # Filtros actuales
            'filtro_cliente': filtro_cliente,
            'filtro_proveedor': filtro_proveedor,
            'filtro_estado': filtro_estado,
            'filtro_vencimiento': filtro_vencimiento,
        })
        return context
class FlujoCajaView(BaseFinanzasView, TemplateView):
    """Reporte de flujo de caja"""
    template_name = 'gestion/finanzas/flujo_caja.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = 'Flujo de Caja'
        
        print("=" * 60)
        print("DEBUG DETALLADO - FlujoCajaView")
        print("=" * 60)
        
        # Parámetros de fecha
        fecha_desde = self.request.GET.get('fecha_desde')
        fecha_hasta = self.request.GET.get('fecha_hasta')
        
        # Fechas por defecto (últimos 30 días)
        hoy = date.today()
        hace_30_dias = hoy - timedelta(days=30)
        
        fecha_inicio = date.fromisoformat(fecha_desde) if fecha_desde else hace_30_dias
        fecha_fin = date.fromisoformat(fecha_hasta) if fecha_hasta else hoy
        
        print(f"Período: {fecha_inicio} a {fecha_fin}")
        
        # ===== 1. VERIFICAR TODOS LOS COBROS =====
        print("\n=== TODOS LOS COBROS ===")
        todos_cobros = Cobro.objects.all()
        print(f"Total cobros en sistema: {todos_cobros.count()}")
        
        for cobro in todos_cobros[:5]:  # Primeros 5
            print(f"  Cobro #{cobro.id}:")
            print(f"    Fecha: {cobro.fecha_cobro if hasattr(cobro, 'fecha_cobro') else cobro.fecha}")
            print(f"    Cliente: {cobro.cliente}")
            print(f"    Monto: {cobro.monto_total}")
            print(f"    Estado: {cobro.estado if hasattr(cobro, 'estado') else 'N/A'}")
        
        # Cobros en el período
        try:
            cobros = Cobro.objects.filter(
                fecha_cobro__date__range=[fecha_inicio, fecha_fin]
            )
        except FieldError:
            cobros = Cobro.objects.filter(
                fecha__date__range=[fecha_inicio, fecha_fin]
            )
        
        print(f"\nCobros en período: {cobros.count()}")
        
        # ===== 2. VERIFICAR TODAS LAS ÓRDENES DE PAGO =====
        print("\n=== TODAS LAS ÓRDENES DE PAGO ===")
        todas_ordenes = OrdenDePago.objects.all()
        print(f"Total órdenes en sistema: {todas_ordenes.count()}")
        
        for orden in todas_ordenes:
            print(f"\n  Orden #{orden.id}:")
            print(f"    Fecha: {orden.fecha_orden if hasattr(orden, 'fecha_orden') else orden.fecha}")
            print(f"    Proveedor: {orden.proveedor}")
            print(f"    Monto Total: {orden.monto_total}")
            print(f"    Estado: {orden.estado}")
            print(f"    Detalles: {orden.ordendepagodetalle_set.count()}")
            
            # Ver detalles si existen
            if hasattr(orden, 'detalles') and orden.detalles.exists():
                for det in orden.detalles.all()[:3]:
                    print(f"      - {det.cuenta_pagar}: ${det.monto_pagado}")
        
        # Órdenes en el período
        try:
            ordenes_pago = OrdenDePago.objects.filter(
                fecha_orden__date__range=[fecha_inicio, fecha_fin]
            )
        except FieldError:
            ordenes_pago = OrdenDePago.objects.filter(
                fecha__date__range=[fecha_inicio, fecha_fin]
            )
        
        print(f"\nÓrdenes en período: {ordenes_pago.count()}")
        print(f"Órdenes Pagadas en período: {ordenes_pago.filter(estado='Pagada').count()}")
        
        # ===== 3. CALCULAR TOTALES CORRECTAMENTE =====
        # INGRESOS: Sumar todos los cobros (no solo los del período si están vacíos)
        total_cobros = cobros.aggregate(total=Sum('monto_total'))['total'] or Decimal('0.00')
        
        # Si no hay cobros en período, mostrar total general para debug
        if total_cobros == 0 and todos_cobros.exists():
            total_general_cobros = todos_cobros.aggregate(total=Sum('monto_total'))['total'] or Decimal('0.00')
            print(f"\n¡ATENCIÓN! Cobros en período: $0, pero total general: ${total_general_cobros}")
        
        # EGRESOS: Solo órdenes PAGADAS
        ordenes_pagadas = ordenes_pago.filter(estado='Pagada')
        total_pagos = ordenes_pagadas.aggregate(total=Sum('monto_total'))['total'] or Decimal('0.00')
        
        # Si no hay pagos en período, ver si hay órdenes pero no están como Pagadas
        if total_pagos == 0 and ordenes_pago.exists():
            print(f"\n¡ATENCIÓN! Hay {ordenes_pago.count()} órdenes en período pero ninguna está como 'Pagada'")
            for orden in ordenes_pago:
                print(f"  Orden #{orden.id}: Estado='{orden.estado}', Monto=${orden.monto_total}")
        
        # ===== 4. PREPARAR MOVIMIENTOS =====
        movimientos = []
        
        # Cobros como INGRESOS
        for cobro in cobros:
            movimientos.append({
                'fecha': cobro.fecha_cobro if hasattr(cobro, 'fecha_cobro') else cobro.fecha,
                'tipo': 'INGRESO',
                'get_tipo_display': 'Ingreso',
                'descripcion': f'Cobro #{cobro.id} - {cobro.cliente}',
                'metodo_pago': getattr(cobro.moneda, 'nombre', 'Efectivo') if hasattr(cobro, 'moneda') else 'Efectivo',
                'monto': cobro.monto_total,
                'saldo_acumulado': 0
            })
        
        # Órdenes PAGADAS como EGRESOS
        for orden in ordenes_pagadas:
            movimientos.append({
                'fecha': orden.fecha_orden if hasattr(orden, 'fecha_orden') else orden.fecha,
                'tipo': 'EGRESO',
                'get_tipo_display': 'Egreso',
                'descripcion': f'Pago #{orden.id} - {orden.proveedor}',
                'metodo_pago': getattr(orden.moneda, 'nombre', 'Transferencia') if hasattr(orden, 'moneda') else 'Transferencia',
                'monto': orden.monto_total,
                'saldo_acumulado': 0
            })
        
        # Ordenar y calcular saldo acumulado
        movimientos.sort(key=lambda x: x['fecha'])
        saldo_acumulado = Decimal('0.00')
        
        for i, mov in enumerate(movimientos):
            if mov['tipo'] == 'INGRESO':
                saldo_acumulado += mov['monto']
            else:  # EGRESO
                saldo_acumulado -= mov['monto']
            mov['saldo_acumulado'] = saldo_acumulado
        
        # ===== 5. CONTEXT FINAL =====
        ingresos_totales = total_cobros
        egresos_totales = total_pagos
        saldo_neto = ingresos_totales - egresos_totales
        
        context.update({
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'filtro_fecha_desde': fecha_desde,
            'filtro_fecha_hasta': fecha_hasta,
            
            'ingresos_totales': ingresos_totales,
            'egresos_totales': egresos_totales,
            'saldo_neto': saldo_neto,
            
            'total_transacciones': len(movimientos),
            'transacciones_hoy': Cobro.objects.filter(
                fecha_cobro__date=hoy
            ).count() + OrdenDePago.objects.filter(
                fecha_orden__date=hoy, estado='Pagada'
            ).count(),
            
            'ingresos_ventas': Venta.objects.filter(
                fecha__date__range=[fecha_inicio, fecha_fin]
            ).aggregate(total=Sum('total'))['total'] or Decimal('0.00'),
            
            'egresos_compras': Compra.objects.filter(
                fecha__date__range=[fecha_inicio, fecha_fin]
            ).aggregate(total=Sum('total'))['total'] or Decimal('0.00'),
            
            'movimientos': movimientos,
        })
        
        print(f"\n=== RESUMEN ===")
        print(f"Ingresos: ${ingresos_totales}")
        print(f"Egresos: ${egresos_totales}")
        print(f"Saldo Neto: ${saldo_neto}")
        print(f"Movimientos: {len(movimientos)}")
        print("=" * 60)
        
        return context