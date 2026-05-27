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
# Asegúrate de que estos nombres coincidan con los de tu forms.py
from .forms import (
    OrdenDeCompraForm, DetalleOrdenDeCompraForm,
    CuentaAPagarForm, 
    OrdenDePagoForm, DetalleOrdenDePagoForm,
    DevolucionAProveedorForm, DetalleDevolucionAProveedorForm
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


# ===================================================================
# A. ORDEN DE COMPRA (OC) 🛒
# ===================================================================

class OrdenDeCompraListView(BaseFinanzasView, ListView):
    model = OrdenDeCompra
    template_name = 'gestion/finanzas/ordencompra_lista.html'
    context_object_name = 'ordenes_compra'
    ordering = ['-fecha_orden']

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
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        # 1. Validar Formset
        if not formset.is_valid():
            messages.error(self.request, "Hay errores en los detalles de la Orden de Compra.")
            return self.form_invalid(form)

        # 2. 🎯 Obtener Empleado y Validar
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
                
                # Recalcular Subtotal y Total (asegurando el vínculo y el cálculo)
                for detalle in detalles_guardados:
                    detalle.orden = self.object # Asegurar la FK, aunque formset ya debería hacerlo
                    detalle.subtotal = detalle.cantidad * detalle.precio_unitario
                    detalle.save()
                    total += detalle.subtotal
                    
                # Guardar los eliminados
                formset.save_m2m() # Necesario si hubiera campos ManyToMany
                for deleted_object in formset.deleted_objects:
                    deleted_object.delete()

                self.object.total = total
                self.object.save(update_fields=['total'])
                
                messages.success(self.request, f"Orden de Compra N°{self.object.pk} creada exitosamente.")
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
                formset.save() # Guarda creación, edición y eliminación (por defecto)
                
                # Recalcular el total basado en los detalles actuales (necesario después del save del formset)
                total = Decimal('0.00')
                for detalle in self.object.ordendecompradetalle_set.all():
                    # Recalcular Subtotal por si se modificó cantidad o precio
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
                    
                    # ⚠️ Validación de saldo
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

# ===================================================================
# D. DEVOLUCIÓN A PROVEEDOR (DAP) ↩️
# ===================================================================

class DevolucionAProveedorListView(BaseFinanzasView, ListView):
    model = DevolucionAProveedor
    template_name = 'gestion/finanzas/devolucionproveedor_lista.html'
    context_object_name = 'devoluciones'
    ordering = ['-fecha'] 

class DevolucionAProveedorDetailView(BaseFinanzasView, DetailView):
    model = DevolucionAProveedor
    template_name = 'gestion/finanzas/devolucionproveedor_detalle.html'
    context_object_name = 'devolucion'

class DevolucionAProveedorCreateView(BaseFinanzasView, CreateView):
    model = DevolucionAProveedor
    form_class = DevolucionAProveedorForm
    template_name = 'gestion/finanzas/devolucionproveedor_form.html'
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['formset'] = DetalleDevolucionAProveedorFormset(self.request.POST)
        else:
            data['formset'] = DetalleDevolucionAProveedorFormset(queryset=DevolucionAProveedorDetalle.objects.none())
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if not formset.is_valid():
            messages.error(self.request, "Hay errores en los detalles de la Devolución.")
            return self.form_invalid(form)

        # 🎯 Obtener Empleado (solo para permisos/auditoría)
        empleado_instance = self.get_empleado_instance()
        if not empleado_instance:
             messages.warning(self.request, "Advertencia: Tu cuenta no está vinculada a un Empleado.")
        
        try:
            with transaction.atomic():
                self.object = form.save(commit=False)
                # Si el modelo DAP tuviera FK a Empleado: self.object.empleado = empleado_instance 
                self.object.save()
                
                total_devolucion = Decimal('0.00')
                formset.instance = self.object
                detalles_guardados = formset.save(commit=False)
                
                for detalle in detalles_guardados:
                    if not detalle.pk: 
                         detalle.devolucion = self.object
                    detalle.subtotal = detalle.cantidad * detalle.precio_devuelto 
                    detalle.save() 
                    total_devolucion += detalle.subtotal 
                
                # Manejo de eliminaciones
                formset.save_m2m()
                for deleted_form in formset.deleted_forms:
                    deleted_form.instance.delete()
                
                self.object.total_devuelto = total_devolucion 
                self.object.save(update_fields=['total_devuelto'])
                
                messages.success(self.request, f"Devolución N°{self.object.pk} creada exitosamente.")
                return redirect('devolucionproveedor_detalle', pk=self.object.pk)
        except Exception as e:
            messages.error(self.request, f"Error al guardar la Devolución: {e}")
            return self.form_invalid(form)


class DevolucionAProveedorUpdateView(BaseFinanzasView, UpdateView):
    model = DevolucionAProveedor
    form_class = DevolucionAProveedorForm
    template_name = 'gestion/finanzas/devolucionproveedor_form.html'
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        dap = self.get_object()
        if self.request.POST:
            data['formset'] = DetalleDevolucionAProveedorFormset(self.request.POST, instance=dap)
        else:
            data['formset'] = DetalleDevolucionAProveedorFormset(instance=dap)
        return data

    def form_valid(self, form):
        # ⚠️ Agregar aquí validación de estado si el modelo DevolucionAProveedor tiene un campo 'estado'
        
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
                for detalle in self.object.devolucionaproveedordetalle_set.all():
                    detalle.subtotal = detalle.cantidad * detalle.precio_devuelto 
                    detalle.save(update_fields=['subtotal']) 
                    total_devolucion += detalle.subtotal 
                
                self.object.total_devuelto = total_devolucion 
                self.object.save(update_fields=['total_devuelto'])
                
                messages.success(self.request, f"Devolución N°{self.object.pk} actualizada exitosamente.")
                return redirect('devolucionproveedor_detalle', pk=self.object.pk)
        except Exception as e:
            messages.error(self.request, f"Error al actualizar la Devolución: {e}")
            return self.form_invalid(form)

# --- Lógica de Procesamiento de DAP (Ajusta Stock y CxP) ---
class DevolucionAProveedorProcesarView(BaseFinanzasView, View):
    
    def post(self, request, pk):
        dap = get_object_or_404(DevolucionAProveedor, pk=pk)
        
        # ⚠️ Aquí deberías verificar el estado si has añadido un campo de estado al modelo DAP
        
        try:
            with transaction.atomic():
                total_devolucion = Decimal('0.00')
                
                # 1. Ajuste de Stock (Salida)
                for detalle_dap in dap.devolucionaproveedordetalle_set.all():
                    producto = detalle_dap.producto
                    cantidad = detalle_dap.cantidad
                    total_devolucion += detalle_dap.subtotal
                    
                    # Validación de Stock
                    producto.refresh_from_db() # Obtener el stock actual en caso de que haya habido cambios
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
                    
                # 2. Ajustar la Cuenta por Pagar asociada 
                compra_original = dap.compra_original
                
                if compra_original: 
                    cxp_queryset = CuentaAPagar.objects.filter(compra=compra_original).exclude(estado='Pagada')
                    
                    if cxp_queryset.exists():
                        cxp = cxp_queryset.first()
                        monto_a_reducir = total_devolucion
                        
                        if monto_a_reducir > cxp.monto_pendiente:
                            monto_a_reducir = cxp.monto_pendiente
                            
                        # Reducir el saldo pendiente (uso de F() atómico)
                        CuentaAPagar.objects.filter(pk=cxp.pk).update(
                            monto_pendiente=F('monto_pendiente') - monto_a_reducir
                        )
                        cxp.refresh_from_db()
                        
                        # Actualizar estado de CxP
                        if cxp.monto_pendiente <= 0:
                            cxp.estado = 'Pagada'
                        else:
                            cxp.estado = 'Pendiente'
                            
                        cxp.save(update_fields=['estado'])
                        messages.info(request, f"Saldo de Cuenta por Pagar N°{cxp.pk} ajustado en ${monto_a_reducir}.")
                    else:
                        messages.warning(request, f"No se encontró Cuenta por Pagar pendiente para la Compra N°{compra_original.pk}. El stock fue ajustado, pero no se modificó el saldo financiero.")
                else:
                    messages.warning(request, "No hay Compra Original asociada a esta Devolución. Solo se ajustó el stock.")
                
                messages.success(request, f"Devolución N°{dap.pk} procesada exitosamente. Stock ajustado.")
                
                # Si DAP tiene campo de estado:
                # dap.estado = 'Procesada'
                # dap.save(update_fields=['estado'])
                
        except IntegrityError as e:
            messages.error(request, f"ERROR DE STOCK o SALDO (Transacción revertida): {e}")
        except Exception as e:
            messages.error(request, f"Error al procesar la Devolución a Proveedor: {e}")
            
        return redirect('devolucionproveedor_detalle', pk=pk)

class DevolucionAProveedorDeleteView(BaseFinanzasView, DeleteView):
    model = DevolucionAProveedor
    template_name = 'gestion/confirm_delete.html'
    success_url = reverse_lazy('devolucionproveedor_lista')
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        # ⚠️ Si tu modelo DAP tiene un campo de estado, verifica que no esté 'Procesada'
        messages.success(request, f"Devolución a Proveedor N°{self.object.pk} eliminada.")
        return super().post(request, *args, **kwargs)