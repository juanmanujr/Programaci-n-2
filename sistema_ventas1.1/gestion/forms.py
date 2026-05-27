# ====================================================================
# gestion/forms.py
# CÓDIGO FINAL CON DEBUG DE FORMSET APLICADO EN EL MÉTODO clean()
# ====================================================================

from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from django.forms import inlineformset_factory 
from .models import (
    Cliente, Producto, Venta, Compra, Proveedor,
    DetalleVenta, DetalleCompra,
    # Asegúrate de que estos modelos existan e impórten correctamente:
    Moneda 
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
# B. Formularios Base (Clientes, Proveedores, Productos)
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
        fields = ['nombre', 'descripcion', 'precio', 'proveedor', 'categoria', 'marca']
        exclude = ('stock',)
        labels = {
            'precio': 'Precio Unitario de Venta',
        }
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }


# ====================================================================
# C. Formularios para Transacciones (Venta y Compra) - **CONTENEDOR DEL DEBUG**
# ====================================================================

class VentaForm(BaseForm):
    moneda = forms.ModelChoiceField(queryset=Moneda.objects.all(), required=False)
    class Meta:
        model = Venta
        exclude = ('total', 'fecha',) 
        fields = '__all__'
        labels = {
            'cliente': 'Cliente (*)', 'empleado': 'Empleado (*)', 'estado': 'Estado de Venta',
        }

class DetalleVentaForm(BaseForm):
    """
    Formulario para DetalleVenta, con validación de filas vacías.
    """
    producto = forms.ModelChoiceField(
        # Filtro de stock: asumiendo que el stock -1 es para productos inactivos
        queryset=Producto.objects.filter(stock__gt=-1).order_by('nombre'), 
        empty_label="--- Seleccione Producto ---",
        label="Producto a Vender",
        required=False # 🔑 CLAVE: El Formset necesita que no sea requerido a nivel de campo
    )
    cantidad = forms.IntegerField(
        required=False, # 🔑 CLAVE
    )
    precio_unitario = forms.DecimalField(
        required=False, # 🔑 CLAVE
    )

    class Meta:
        model = DetalleVenta
        fields = ['producto', 'cantidad', 'precio_unitario'] 
        exclude = ('venta', 'subtotal',) 

        labels = {
            'producto': 'Producto (*)', 'cantidad': 'Cantidad (*)', 'precio_unitario': 'Precio Unitario de Venta',
        }

    def clean(self):
        # --- 1. LIMPIEZA AGRESIVA DE ESPACIOS/CARACTERES RAROS (MANTENER) ---
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
        
        # --- 2. 🚨 DEBUG CRÍTICO: DESCARTE DE FILA VACÍA 🚨
        is_delete = cleaned_data.get('DELETE')
        # La forma más robusta de chequear si la fila está vacía/incompleta
        if not producto and not is_delete and (cantidad is None or cantidad == 0) and (precio is None or precio == 0):
             # 🔑 CLAVE DEL DEBUG: Devolver un diccionario vacío anula este formulario
             # y previene que el Formset intente validar campos requeridos.
            return {} 
        
        # --- 3. VALIDACIÓN CONDICIONAL DE CAMPOS OBLIGATORIOS (SÓLO SI HAY PRODUCTO) ---
        if producto:
            if cantidad is None or cantidad <= 0:
                   self.add_error('cantidad', "La cantidad es obligatoria y debe ser mayor que cero para el producto seleccionado.")
            if precio is None or precio <= 0:
                   self.add_error('precio_unitario', "El precio unitario es obligatorio y debe ser mayor que cero.")

        if not producto and (cantidad is not None and cantidad > 0 or precio is not None and precio > 0):
            self.add_error('producto', "Debe seleccionar un producto para ingresar una cantidad o precio.")
        
        return cleaned_data


class CompraForm(BaseForm):
    moneda = forms.ModelChoiceField(queryset=Moneda.objects.all(), required=False)
    class Meta:
        model = Compra
        exclude = ('total', 'fecha',)
        fields = '__all__'
        labels = {
            'proveedor': 'Proveedor (*)', 'empleado': 'Empleado (*)', 'estado': 'Estado de Compra',
        }

class DetalleCompraForm(BaseForm):
    """
    Formulario para DetalleCompra. Implementa la lógica de debug en clean()
    para manejar la fila extra del formset.
    """
    # 🔑 CLAVE 1: HACER LOS CAMPOS NO OBLIGATORIOS A NIVEL DE CAMPO
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.all().order_by('nombre'), 
        empty_label="--- Seleccione Producto ---",
        label="Producto a Comprar",
        required=False
    )
    cantidad = forms.IntegerField(
        required=False,
    )
    precio_compra = forms.DecimalField(
        required=False,
        label="Precio Unitario de Compra"
    )

    class Meta:
        model = DetalleCompra
        fields = ['producto', 'cantidad', 'precio_compra'] 
        exclude = ('compra', 'subtotal', 'precio_unitario',) 

    def clean(self):
        # --- 1. LIMPIEZA DE DATOS (Decimales y espacios) ---
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
        
        # --- 2. 🚨 DEBUG CRÍTICO: DESCARTE DE FILA VACÍA 🚨
        is_delete = cleaned_data.get('DELETE')
        # Si no hay producto Y no está marcado para borrado Y los campos numéricos están vacíos o en cero (dato residual)
        if not producto and not is_delete and (cantidad is None or cantidad == 0) and (precio_compra is None or precio_compra == 0):
             # 🔑 CLAVE DEL DEBUG: Devolver un diccionario vacío anula este formulario
            return {}
        
        # --- 3. VALIDACIÓN CONDICIONAL DE CAMPOS OBLIGATORIOS (SÓLO SI HAY PRODUCTO) ---
        if producto:
            if cantidad is None or cantidad <= 0:
                   self.add_error('cantidad', "La cantidad es obligatoria y debe ser mayor que cero para el producto seleccionado.")
            if precio_compra is None or precio_compra <= 0:
                   self.add_error('precio_compra', "El precio de compra es obligatorio y debe ser mayor que cero.")

        if not producto and (cantidad is not None and cantidad > 0 or precio_compra is not None and precio_compra > 0):
            self.add_error('producto', "Debe seleccionar un producto para ingresar una cantidad o precio.")
        
        return cleaned_data


# ====================================================================
# D. Formset Base (Para uso general, ya no necesita lógica extra)
# ====================================================================

class BaseDetalleFormSet(BaseInlineFormSet):
    """
    Clase base estándar para formsets, ya que la lógica de descarte
    ahora está en el clean() de los formularios individuales.
    """
    # Si el formulario individual devuelve {}, Django lo ignora automáticamente.
    pass

BaseDetalleVentaFormSet = BaseDetalleFormSet
BaseDetalleCompraFormSet = BaseDetalleFormSet 


# ====================================================================
# E. Creación de Formsets
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