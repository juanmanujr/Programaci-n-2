# ====================================================================
# gestion/forms.py
# 
# ====================================================================

from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from django.forms import inlineformset_factory
from decimal import Decimal
from .models import (
    Cliente, Producto, Venta, Compra, Proveedor,
    DetalleVenta, DetalleCompra,
    PedidoCliente,
    PedidoClienteDetalle,
    Ajuste,
    AjusteDetalle,
    AjusteTipo,
    Moneda, CategoriaProducto, Marca,
    OrdenDeCompra,
    OrdenDeCompraDetalle,
    CuentaAPagar,
    OrdenDePago,
    OrdenDePagoDetalle,
    DevolucionAProveedor,
    DevolucionAProveedorDetalle,
    # AGREGAR ESTOS MODELOS:
    CuentaACobrar,  # ← Agregar
    Caja,           # ← Agregar
    Empleado,       # ← Agregar (si no está ya)
    Cobro,          # ← Agregar
    CobroDetalle,   # ← Agregar
    Arqueo,         # ← Agregar
)

# ====================================================================
# === PARTE 1: CLASE BASE Y FORMULARIOS PRINCIPALES (Clientes, Prod.)
# ====================================================================

class BaseForm(forms.ModelForm):
    """Clase base que aplica la clase 'form-control' de Bootstrap."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Evitar errores si no hay campos
        for field_name, field in getattr(self, 'fields', {}).items():
            # Excluir CheckboxInput, RadioSelect, ClearableFileInput
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect, forms.ClearableFileInput)):
                current_classes = field.widget.attrs.get('class', '')
                # Limpiar caracteres invisibles (\xa0)
                current_classes = current_classes.replace('\xa0', ' ').strip()
                if 'form-control' not in current_classes:
                    field.widget.attrs['class'] = (current_classes + ' form-control').strip()

# -------------------- B. Formularios Base --------------------

class ClienteForm(BaseForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'direccion', 'telefono', 'email']
        labels = {
            'nombre': 'Nombre del Cliente',
            'apellido': 'Apellido del Cliente',
            'email': 'Correo Electrónico',
        }

class ProveedorForm(BaseForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'contacto', 'telefono', 'email']
        labels = {
            'nombre': 'Razón Social / Nombre del Proveedor',
            'contacto': 'Persona de Contacto',
            'telefono': 'Teléfono',
            'email': 'Correo Electrónico',
        }

class ProductoForm(BaseForm):
    class Meta:
        model = Producto
        # Incluimos explícitamente campos importantes; stock se gestiona internamente
        fields = ['nombre', 'descripcion', 'precio', 'proveedor', 'categoria', 'marca', 'stock_minimo']
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
# === PARTE 1 (continuación): Formularios de Transacción (Venta/Compra)
# ====================================================================

# --- VENTA ---
class VentaForm(BaseForm):
    moneda = forms.ModelChoiceField(queryset=Moneda.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    class Meta:
        model = Venta
        # Excluir total y fecha porque se calculan/gestionan automáticamente
        exclude = ('total', 'fecha',)

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
        exclude = ('venta', 'subtotal',)
        fields = ['producto', 'cantidad', 'precio_unitario']
        labels = {
            'producto': 'Producto (*)',
            'cantidad': 'Cantidad (*)',
            'precio_unitario': 'Precio Unitario de Venta',
        }

    def clean(self):
        # Normalizar entradas de cadena y validar lógicas de integridad
        if 'cantidad' in self.data and isinstance(self.data['cantidad'], str):
            self.data['cantidad'] = self.data['cantidad'].strip()

        if 'precio_unitario' in self.data and isinstance(self.data['precio_unitario'], str):
            precio_limpio = self.data['precio_unitario'].strip().replace(',', '.')
            self.data['precio_unitario'] = precio_limpio

        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad')
        precio = cleaned_data.get('precio_unitario')
        is_delete = cleaned_data.get('DELETE')

        # Fila vacía nueva -> ignorar
        if not producto and not is_delete and (cantidad in (None, 0)) and (precio in (None, 0)):
            return {}

        if producto:
            if cantidad is None or cantidad <= 0:
                self.add_error('cantidad', "La cantidad es obligatoria y debe ser mayor que cero para el producto seleccionado.")
            if precio is None or precio <= 0:
                self.add_error('precio_unitario', "El precio unitario es obligatorio y debe ser mayor que cero.")

        if not producto and (cantidad not in (None, 0) or precio not in (None, 0)):
            self.add_error('producto', "Debe seleccionar un producto para ingresar una cantidad o precio.")

        return cleaned_data


# --- COMPRA ---
class CompraForm(BaseForm):
    moneda = forms.ModelChoiceField(queryset=Moneda.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    class Meta:
        model = Compra
        exclude = ('total', 'fecha',)

class DetalleCompraForm(BaseForm):
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.all().order_by('nombre'),
        empty_label="--- Seleccione Producto ---",
        label="Producto a Comprar",
        required=False
    )
    cantidad = forms.IntegerField(required=False)
    precio_compra = forms.DecimalField(required=False, label="Precio Unitario de Compra")

    class Meta:
        model = DetalleCompra
        exclude = ('compra', 'subtotal',)
        fields = ['producto', 'cantidad', 'precio_compra']

    def clean(self):
        if 'cantidad' in self.data and isinstance(self.data['cantidad'], str):
            self.data['cantidad'] = self.data['cantidad'].strip()

        if 'precio_compra' in self.data and isinstance(self.data['precio_compra'], str):
            precio_limpio = self.data['precio_compra'].strip().replace(',', '.')
            self.data['precio_compra'] = precio_limpio

        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad')
        precio_compra = cleaned_data.get('precio_compra')
        is_delete = cleaned_data.get('DELETE')

        if not producto and not is_delete and (cantidad in (None, 0)) and (precio_compra in (None, 0)):
            return {}

        if producto:
            if cantidad is None or cantidad <= 0:
                self.add_error('cantidad', "La cantidad es obligatoria y debe ser mayor que cero para el producto seleccionado.")
            if precio_compra is None or precio_compra <= 0:
                self.add_error('precio_compra', "El precio de compra es obligatorio y debe ser mayor que cero.")

        if not producto and (cantidad not in (None, 0) or precio_compra not in (None, 0)):
            self.add_error('producto', "Debe seleccionar un producto para ingresar una cantidad o precio.")

        return cleaned_data


# ====================================================================
# === PARTE 2: Pedidos, Ajustes, Órdenes, CxP, OP, Devoluciones
# ====================================================================

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

# --- Pedido Cliente Detalle (parte 2 que enviaste) ---
class PedidoClienteDetalleForm(BaseForm):
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.all().order_by('nombre'),
        empty_label="--- Seleccione Producto ---",
        label="Producto",
        required=False
    )
    cantidad = forms.IntegerField(required=False)
    precio_acordado = forms.DecimalField(required=False, label="Precio Acordado")

    class Meta:
        model = PedidoClienteDetalle
        exclude = ('pedido', 'subtotal',)
        fields = ['producto', 'cantidad', 'precio_acordado']

    def clean(self):
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

        if not producto and not is_delete and (cantidad in (None, 0)) and (precio in (None, 0)):
            return {}

        if producto:
            if cantidad is None or cantidad <= 0:
                self.add_error('cantidad', "La cantidad es obligatoria y debe ser mayor que cero.")
            if precio is None or precio <= 0:
                self.add_error('precio_acordado', "El precio acordado es obligatorio y debe ser mayor que cero.")

        if not producto and (cantidad not in (None, 0) or precio not in (None, 0)):
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
        widgets = {
            'motivo': forms.Textarea(attrs={'rows': 2}),
        }

class DetalleAjusteForm(BaseForm):
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.all().order_by('nombre'),
        empty_label="--- Seleccione Producto ---",
        label="Producto",
        required=False
    )
    cantidad = forms.IntegerField(required=False, label="Cantidad a Ajustar")

    class Meta:
        model = AjusteDetalle
        exclude = ('ajuste',)
        fields = ['producto', 'cantidad', 'observaciones']

    def clean(self):
        if 'cantidad' in self.data and isinstance(self.data['cantidad'], str):
            self.data['cantidad'] = self.data['cantidad'].strip()

        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad')
        is_delete = cleaned_data.get('DELETE')

        es_fila_nueva_vacia = (
            not getattr(self.instance, 'pk', None) and
            not producto and
            not is_delete and
            (cantidad in (None, 0))
        )

        if es_fila_nueva_vacia:
            return {}

        if producto:
            if cantidad is None or cantidad == 0:
                self.add_error('cantidad', "La cantidad de ajuste es obligatoria y no puede ser cero.")

        if not producto and (cantidad not in (None, 0)):
            self.add_error('producto', "Debe seleccionar un producto si ingresa una cantidad de ajuste.")

        return cleaned_data


# ====================================================================
# D. Formularios para ÓRDENES DE COMPRA Y FINANZAS
# ====================================================================

class OrdenDeCompraForm(BaseForm):
    fecha_entrega_estimada = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False,
        label="Fecha de Entrega Estimada"
    )

    class Meta:
        model = OrdenDeCompra
        fields = ['proveedor', 'empleado', 'fecha_entrega_estimada', 'estado']

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


class CuentaAPagarForm(BaseForm):
    class Meta:
        model = CuentaAPagar
        fields = ['proveedor', 'compra', 'fecha_vencimiento', 'monto_original', 'monto_pendiente', 'estado']
        widgets = {
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
        }

class OrdenDePagoForm(BaseForm):
    class Meta:
        model = OrdenDePago
        fields = ['proveedor', 'empleado', 'moneda', 'estado']

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


# --- DEVOLUCIÓN A PROVEEDOR ---
class DevolucionAProveedorForm(BaseForm):
    class Meta:
        model = DevolucionAProveedor
        fields = ['proveedor', 'compra_original']

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
# E. FORMULARIOS PARA CUENTAS POR COBRAR Y CAJAS (NUEVOS)
# ====================================================================

class CuentaACobrarForm(BaseForm):
    class Meta:
        model = CuentaACobrar
        fields = ['cliente', 'venta', 'fecha_vencimiento', 'monto_original', 'monto_pendiente', 'estado']
        widgets = {
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        labels = {
            'cliente': 'Cliente',
            'venta': 'Venta relacionada',
            'fecha_vencimiento': 'Fecha de vencimiento',
            'monto_original': 'Monto original',
            'monto_pendiente': 'Monto pendiente',
            'estado': 'Estado',
        }


class CajaForm(BaseForm):
    class Meta:
        model = Caja
        fields = ['nombre', 'empleado_responsable', 'monto_inicial']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Caja Principal - Turno Mañana'
            }),
            'monto_inicial': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
        }
        labels = {
            'nombre': 'Nombre de la caja',
            'empleado_responsable': 'Empleado responsable',
            'monto_inicial': 'Monto inicial en efectivo',
        }


class CobroForm(BaseForm):
    class Meta:
        model = Cobro
        fields = ['cliente', 'moneda', 'caja']
        labels = {
            'cliente': 'Cliente',
            'moneda': 'Moneda',
            'caja': 'Caja donde se registra',
        }


class CobroDetalleForm(BaseForm):
    class Meta:
        model = CobroDetalle
        fields = ['cuenta_a_cobrar', 'monto_aplicado']
        labels = {
            'cuenta_a_cobrar': 'Cuenta por cobrar',
            'monto_aplicado': 'Monto aplicado',
        }


class ArqueoForm(BaseForm):
    class Meta:
        model = Arqueo
        fields = ['caja', 'empleado', 'monto_contado', 'monto_sistema', 'observaciones']
        widgets = {
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'caja': 'Caja a arquear',
            'empleado': 'Empleado que realiza el arqueo',
            'monto_contado': 'Monto contado físicamente',
            'monto_sistema': 'Monto según sistema',
            'observaciones': 'Observaciones',
        }


# ====================================================================
# F. Formset Base y G. Creación de Formsets
# ====================================================================

class BaseDetalleFormSet(BaseInlineFormSet):
    pass

BaseDetalleVentaFormSet = BaseDetalleFormSet
BaseDetalleCompraFormSet = BaseDetalleFormSet
BasePedidoClienteDetalleFormSet = BaseDetalleFormSet
BaseDetalleAjusteFormSet = BaseDetalleFormSet

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

PedidoClienteDetalleFormset = inlineformset_factory(
    PedidoCliente,
    PedidoClienteDetalle,
    form=PedidoClienteDetalleForm,
    formset=BasePedidoClienteDetalleFormSet,
    extra=1,
    can_delete=True
)

DetalleAjusteFormset = inlineformset_factory(
    Ajuste,
    AjusteDetalle,
    form=DetalleAjusteForm,
    extra=1,
    can_delete=True
)

DetalleOrdenDeCompraFormset = inlineformset_factory(
    OrdenDeCompra,
    OrdenDeCompraDetalle,
    form=DetalleOrdenDeCompraForm,
    extra=1,
    can_delete=True
)

DetalleOrdenDePagoFormset = inlineformset_factory(
    OrdenDePago,
    OrdenDePagoDetalle,
    form=DetalleOrdenDePagoForm,
    extra=1,
    can_delete=True
)

DetalleDevolucionAProveedorFormset = inlineformset_factory(
    DevolucionAProveedor,
    DevolucionAProveedorDetalle,
    form=DetalleDevolucionAProveedorForm,
    extra=1,
    can_delete=True
)

# NUEVOS FORMSETS PARA COBROS
CobroDetalleFormset = inlineformset_factory(
    Cobro,
    CobroDetalle,
    form=CobroDetalleForm,
    extra=1,
    can_delete=True,
    fields=['cuenta_a_cobrar', 'monto_aplicado']
)


# ====================================================================
# FIN de forms.py
# ====================================================================