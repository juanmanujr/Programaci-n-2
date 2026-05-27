# ====================================================================
# gestion/forms.py
# CÓDIGO FINAL Y COMPLETO CON TODOS LOS MÓDULOS DE GESTIÓN Y FINANZAS
# ====================================================================

from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from django.forms import inlineformset_factory 
from .models import (
    Cliente, Producto, Venta, Compra, Proveedor,
    DetalleVenta, DetalleCompra,
    # === MODELOS DE FLUJO PRINCIPAL ===
    PedidoCliente, 
    PedidoClienteDetalle, 
    Ajuste, 
    AjusteDetalle, 
    AjusteTipo, 
    Moneda, CategoriaProducto, Marca,
    
    # === MODELOS DE FINANZAS Y PROVEEDORES AÑADIDOS/FALTANTES ===
    OrdenDeCompra, 
    OrdenDeCompraDetalle, # Para el formset de OC
    CuentaAPagar,         # Para el formulario de Cuenta por Pagar
    OrdenDePago, 
    OrdenDePagoDetalle,   # Para el formset de OP
    DevolucionAProveedor, 
    DevolucionAProveedorDetalle, # Para el formset de Devolución
)

# ====================================================================
# A. CLASE BASE: Aplica estilos de Bootstrap
# ====================================================================

class BaseForm(forms.ModelForm):
    """Clase base que aplica la clase 'form-control' de Bootstrap."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Excluir CheckboxInput, RadioSelect, ClearableFileInput
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect, forms.ClearableFileInput)):
                current_classes = field.widget.attrs.get('class', '')
                # Limpiar los caracteres invisibles (\xa0)
                current_classes = current_classes.replace('\xa0', ' ').strip() 
                
                if 'form-control' not in current_classes:
                    field.widget.attrs['class'] = (current_classes + ' form-control').strip()

# ====================================================================
# B. Formularios Base (Clientes, Proveedores, Productos y Catálogos)
# ====================================================================

class ClienteForm(BaseForm): 
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'direccion', 'telefono', 'email']
        exclude = ('fecha_registro',)
        labels = {
            'nombre': 'Nombre del Cliente', 'apellido': 'Apellido del Cliente', 'email': 'Correo Electrónico',
        }

class ProveedorForm(BaseForm): 
    class Meta:
        model = Proveedor
        fields = ['nombre', 'contacto', 'telefono', 'email']
        labels = {
            'nombre': 'Razón Social / Nombre del Proveedor', 'contacto': 'Persona de Contacto', 'telefono': 'Teléfono', 'email': 'Correo Electrónico',
        }
    
class ProductoForm(BaseForm): 
    class Meta:
        model = Producto
        # Aseguramos que 'stock_minimo' esté incluido
        fields = ['nombre', 'descripcion', 'precio', 'proveedor', 'categoria', 'marca', 'stock_minimo'] 
        exclude = ('stock',)
        labels = {
            'precio': 'Precio Unitario de Venta',
            'stock_minimo': 'Stock Mínimo de Alerta', 
        }
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

class CategoriaProductoForm(BaseForm):
    class Meta:
        model = CategoriaProducto
        fields = '__all__'
        labels = {'nombre': 'Nombre de la Categoría'}

class MarcaForm(BaseForm):
    class Meta:
        model = Marca
        fields = '__all__'
        labels = {'nombre': 'Nombre de la Marca'}


# ====================================================================
# C. Formularios para Transacciones (Venta, Compra, Pedido, Ajuste)
# ====================================================================

# --- VENTA ---
class VentaForm(BaseForm):
    moneda = forms.ModelChoiceField(queryset=Moneda.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    class Meta:
        model = Venta
        exclude = ('total', 'fecha',) 
        fields = '__all__'
        labels = {
            'cliente': 'Cliente (*)', 'empleado': 'Empleado (*)', 'estado': 'Estado de Venta',
        }

class DetalleVentaForm(BaseForm):
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(stock__gt=-1).order_by('nombre'), 
        empty_label="--- Seleccione Producto ---",
        label="Producto a Vender",
        required=False 
    )
    cantidad = forms.IntegerField(required=False)
    precio_unitario = forms.DecimalField(required=False)

    class Meta:
        model = DetalleVenta
        fields = ['producto', 'cantidad', 'precio_unitario'] 
        exclude = ('venta', 'subtotal',) 
        labels = {
            'producto': 'Producto (*)', 'cantidad': 'Cantidad (*)', 'precio_unitario': 'Precio Unitario de Venta',
        }
    def clean(self):
        # Lógica de limpieza y validación existente (OK)
        # ... (código de clean omitido para brevedad en la revisión, se asume correcto)
        if 'cantidad' in self.data and isinstance(self.data['cantidad'], str):
            self.data['cantidad'] = self.data['cantidad'].strip()
        
        if 'precio_unitario' in self.data and isinstance(self.data['precio_unitario'], str):
            precio_limpio = self.data['precio_unitario'].strip()
            precio_limpio = precio_limpio.replace(',', '.') 
            self.data['precio_unitario'] = precio_limpio
            
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad')
        precio = cleaned_data.get('precio_unitario')
        is_delete = cleaned_data.get('DELETE')
        if not producto and not is_delete and (cantidad is None or cantidad == 0) and (precio is None or precio == 0):
            return {} 
        if producto:
            if cantidad is None or cantidad <= 0:
                self.add_error('cantidad', "La cantidad es obligatoria y debe ser mayor que cero para el producto seleccionado.")
            if precio is None or precio <= 0:
                self.add_error('precio_unitario', "El precio unitario es obligatorio y debe ser mayor que cero.")
        if not producto and (cantidad is not None and cantidad > 0 or precio is not None and precio > 0):
            self.add_error('producto', "Debe seleccionar un producto para ingresar una cantidad o precio.")
        return cleaned_data


# --- COMPRA ---
class CompraForm(BaseForm):
    moneda = forms.ModelChoiceField(queryset=Moneda.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    class Meta:
        model = Compra
        exclude = ('total', 'fecha',)
        fields = '__all__'
        labels = {
            'proveedor': 'Proveedor (*)', 'empleado': 'Empleado (*)', 'estado': 'Estado de Compra',
        }

class DetalleCompraForm(BaseForm):
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.all().order_by('nombre'), 
        empty_label="--- Seleccione Producto ---",
        label="Producto a Comprar",
        required=False
    )
    cantidad = forms.IntegerField(required=False)
    precio_compra = forms.DecimalField(
        required=False,
        label="Precio Unitario de Compra"
    )

    class Meta:
        model = DetalleCompra
        fields = ['producto', 'cantidad', 'precio_compra'] 
        exclude = ('compra', 'subtotal',) 

    def clean(self):
        # Lógica de limpieza y validación existente (OK)
        # ... (código de clean omitido para brevedad en la revisión, se asume correcto)
        if 'cantidad' in self.data and isinstance(self.data['cantidad'], str):
            self.data['cantidad'] = self.data['cantidad'].strip()
        
        if 'precio_compra' in self.data and isinstance(self.data['precio_compra'], str):
            precio_limpio = self.data['precio_compra'].strip()
            precio_limpio = precio_limpio.replace(',', '.') 
            self.data['precio_compra'] = precio_limpio
            
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad')
        precio_compra = cleaned_data.get('precio_compra')
        is_delete = cleaned_data.get('DELETE')
        if not producto and not is_delete and (cantidad is None or cantidad == 0) and (precio_compra is None or precio_compra == 0):
            return {}
        if producto:
            if cantidad is None or cantidad <= 0:
                self.add_error('cantidad', "La cantidad es obligatoria y debe ser mayor que cero para el producto seleccionado.")
            if precio_compra is None or precio_compra <= 0:
                self.add_error('precio_compra', "El precio de compra es obligatorio y debe ser mayor que cero.")
        if not producto and (cantidad is not None and cantidad > 0 or precio_compra is not None and precio_compra > 0):
            self.add_error('producto', "Debe seleccionar un producto para ingresar una cantidad o precio.")
        return cleaned_data

# --- PEDIDO DE CLIENTE ---
class PedidoClienteForm(BaseForm):
    fecha_entrega_estimada = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False,
        label="Fecha de Entrega Estimada"
    )

    class Meta:
        model = PedidoCliente
        fields = ['cliente', 'empleado', 'fecha_entrega_estimada', 'estado']
        labels = {
            'cliente': 'Cliente (*)', 
            'empleado': 'Empleado (Opcional)', 
            'fecha_entrega_estimada': 'Entrega Estimada',
            'estado': 'Estado del Pedido',
        }

class PedidoClienteDetalleForm(BaseForm):
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.all().order_by('nombre'), 
        empty_label="--- Seleccione Producto ---",
        label="Producto",
        required=False 
    )
    cantidad = forms.IntegerField(required=False)
    precio_acordado = forms.DecimalField( 
        required=False, 
        label="Precio Acordado"
    )

    class Meta:
        model = PedidoClienteDetalle
        fields = ['producto', 'cantidad', 'precio_acordado'] 
        exclude = ('pedido', 'subtotal',) 

    def clean(self):
        # Lógica de limpieza y validación existente (OK)
        # ... (código de clean omitido para brevedad en la revisión, se asume correcto)
        if 'cantidad' in self.data and isinstance(self.data['cantidad'], str):
            self.data['cantidad'] = self.data['cantidad'].strip()
        
        if 'precio_acordado' in self.data and isinstance(self.data['precio_acordado'], str):
            precio_limpio = self.data['precio_acordado'].strip().replace(',', '.') 
            self.data['precio_acordado'] = precio_limpio
            
        cleaned_data = super().clean()

        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad')
        precio = cleaned_data.get('precio_acordado') 
        
        is_delete = cleaned_data.get('DELETE')
        if not producto and not is_delete and (cantidad is None or cantidad == 0) and (precio is None or precio == 0):
            return {}

        if producto:
            if cantidad is None or cantidad <= 0:
                self.add_error('cantidad', "La cantidad es obligatoria y debe ser mayor que cero.")
            if precio is None or precio <= 0:
                self.add_error('precio_acordado', "El precio acordado es obligatorio y debe ser mayor que cero.") 

        if not producto and (cantidad is not None and cantidad > 0 or precio is not None and precio > 0):
            self.add_error('producto', "Debe seleccionar un producto para ingresar una cantidad o precio.")
        
        return cleaned_data

# --- AJUSTES DE INVENTARIO ---

class AjusteInventarioForm(BaseForm):
    tipo_ajuste = forms.ModelChoiceField(
        queryset=AjusteTipo.objects.all().order_by('nombre'),
        label="Tipo de Ajuste (*)",
    )
    class Meta:
        model = Ajuste 
        fields = ['tipo_ajuste', 'empleado', 'motivo', 'estado']
        labels = {
            'empleado': 'Empleado (*)', 
            'motivo': 'Motivo del Ajuste',
            'estado': 'Estado',
        }
        widgets = {
            'motivo': forms.Textarea(attrs={'rows': 2}),
        }
        exclude = ('fecha',)

class DetalleAjusteForm(BaseForm):
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.all().order_by('nombre'), 
        empty_label="--- Seleccione Producto ---",
        label="Producto",
        required=False
    )
    cantidad = forms.IntegerField(
        required=False,
        label="Cantidad a Ajustar" 
    )

    class Meta:
        model = AjusteDetalle 
        fields = ['producto', 'cantidad'] 
        exclude = ('ajuste',) 

    def clean(self):
        # Lógica de limpieza y validación existente (OK)
        # ... (código de clean omitido para brevedad en la revisión, se asume correcto)
        if 'cantidad' in self.data and isinstance(self.data['cantidad'], str):
            self.data['cantidad'] = self.data['cantidad'].strip()
            
        cleaned_data = super().clean()

        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad')
        
        is_delete = cleaned_data.get('DELETE')
        
        if not producto and not is_delete and (cantidad is None or cantidad == 0):
            return {}

        if producto:
            if cantidad is None or cantidad == 0:
                self.add_error('cantidad', "La cantidad de ajuste es obligatoria y no puede ser cero.")

        if not producto and (cantidad is not None and cantidad != 0):
            self.add_error('producto', "Debe seleccionar un producto si ingresa una cantidad de ajuste.")
        
        return cleaned_data

# ====================================================================
# D. Formularios para ÓRDENES DE COMPRA Y FINANZAS (AÑADIDOS Y CORREGIDOS)
# ====================================================================

# --- 1. ORDEN DE COMPRA (OC) ---
class OrdenDeCompraForm(BaseForm):
    fecha_entrega_estimada = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False,
        label="Fecha de Entrega Estimada"
    )
    class Meta:
        model = OrdenDeCompra
        fields = ['proveedor', 'empleado', 'fecha_entrega_estimada', 'estado'] 
        labels = {
            'proveedor': 'Proveedor (*)', 
            'empleado': 'Empleado a Cargo (Opcional)', 
        }

# === CORRECCIÓN: CLASE BASE PARA EL DETALLE DE OC (Para importación) ===
class DetalleOrdenDeCompraForm(BaseForm): 
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.all().order_by('nombre'), 
        empty_label="--- Seleccione Producto ---",
        label="Producto Solicitado",
        required=False
    )
    class Meta:
        model = OrdenDeCompraDetalle
        fields = ['producto', 'cantidad', 'precio_unitario']

# --- 2. CUENTA POR PAGAR (CxP) ---
class CuentaAPagarForm(BaseForm):
    class Meta:
        model = CuentaAPagar
        # Incluyo monto_pendiente para poder modificar saldos si es necesario, aunque el monto original no cambia.
        fields = ['proveedor', 'compra', 'fecha_vencimiento', 'monto_original', 'monto_pendiente', 'estado']
        widgets = {
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
        }
        
# --- 3. ORDEN DE PAGO (OP) ---
class OrdenDePagoForm(BaseForm):
    class Meta:
        model = OrdenDePago
        fields = ['proveedor', 'empleado', 'moneda', 'estado']

# === CORRECCIÓN: CLASE BASE PARA EL DETALLE DE OP (Para importación) ===
class DetalleOrdenDePagoForm(BaseForm):
    cuenta_a_pagar = forms.ModelChoiceField(
        queryset=CuentaAPagar.objects.filter(estado='PENDIENTE'), 
        empty_label="--- Seleccione Cuenta por Pagar ---",
        label="Cuenta a Pagar",
        required=False
    )
    monto_aplicado = forms.DecimalField(required=False)
    class Meta:
        model = OrdenDePagoDetalle
        fields = ['cuenta_a_pagar', 'monto_aplicado']


# --- 4. DEVOLUCIÓN A PROVEEDOR ---
class DevolucionAProveedorForm(BaseForm):
    class Meta:
        model = DevolucionAProveedor
        fields = ['proveedor', 'compra_original'] 

# === CORRECCIÓN: CLASE BASE PARA EL DETALLE DE DEVOLUCIÓN (Para importación) ===
class DetalleDevolucionAProveedorForm(BaseForm):
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.all().order_by('nombre'), 
        empty_label="--- Seleccione Producto ---",
        label="Producto a Devolver",
        required=False
    )
    class Meta:
        model = DevolucionAProveedorDetalle
        fields = ['producto', 'cantidad', 'precio_devuelto']


# ====================================================================
# E. Formset Base
# ====================================================================

class BaseDetalleFormSet(BaseInlineFormSet):
    pass

# E.1. Clases de formset base (solo alias)
BaseDetalleVentaFormSet = BaseDetalleFormSet
BaseDetalleCompraFormSet = BaseDetalleFormSet 
BasePedidoClienteDetalleFormSet = BaseDetalleFormSet 
BaseDetalleAjusteFormSet = BaseDetalleFormSet 


# ====================================================================
# F. Creación de Formsets (TODOS COMPLETOS Y CORREGIDOS)
# ====================================================================

DetalleCompraFormset = inlineformset_factory(
    Compra, 
    DetalleCompra, 
    form=DetalleCompraForm,
    formset=BaseDetalleCompraFormSet, 
    extra=1, 
    can_delete=True
)

DetalleVentaFormset = inlineformset_factory(
    Venta, 
    DetalleVenta, 
    form=DetalleVentaForm, 
    formset=BaseDetalleVentaFormSet,
    extra=1, 
    can_delete=True
)

# --- PEDIDO DE CLIENTE FORMSET ---
PedidoClienteDetalleFormset = inlineformset_factory(
    PedidoCliente, 
    PedidoClienteDetalle, 
    form=PedidoClienteDetalleForm,
    formset=BasePedidoClienteDetalleFormSet, 
    extra=1, 
    can_delete=True
)

# --- AJUSTE DE INVENTARIO FORMSET ---
DetalleAjusteFormset = inlineformset_factory(
    Ajuste, 
    AjusteDetalle, 
    form=DetalleAjusteForm,
    formset=BaseDetalleAjusteFormSet, 
    extra=1, 
    can_delete=True
) 

# --- ORDEN DE COMPRA FORMSET (CORREGIDO USANDO LA CLASE BASE DetalleOrdenDeCompraForm) ---
DetalleOrdenDeCompraFormset = inlineformset_factory(
    OrdenDeCompra, 
    OrdenDeCompraDetalle, 
    form=DetalleOrdenDeCompraForm, # <-- CORRECCIÓN APLICADA
    extra=1, 
    can_delete=True
)

# --- ORDEN DE PAGO FORMSET (CORREGIDO USANDO LA CLASE BASE DetalleOrdenDePagoForm) ---
DetalleOrdenDePagoFormset = inlineformset_factory(
    OrdenDePago, 
    OrdenDePagoDetalle, 
    form=DetalleOrdenDePagoForm, # <-- CORRECCIÓN APLICADA
    extra=1, 
    can_delete=True
)

# --- DEVOLUCIÓN A PROVEEDOR FORMSET (CORREGIDO USANDO LA CLASE BASE DetalleDevolucionAProveedorForm) ---
DetalleDevolucionAProveedorFormset = inlineformset_factory(
    DevolucionAProveedor, 
    DevolucionAProveedorDetalle, 
    form=DetalleDevolucionAProveedorForm, # <-- CORRECCIÓN APLICADA
    extra=1, 
    can_delete=True
)