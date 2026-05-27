import logging
from decimal import Decimal
import json 
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db import transaction
from django.db.models import F, Sum
from django.forms.models import model_to_dict
from django.utils import timezone
from .middleware import get_current_user 
from .models import (
    DetalleCompra, DetalleVenta, Compra, Venta,
    Ajuste, AjusteDetalle, AjusteTipo,
    Producto, InventarioMovimiento,
    Auditoria, Cliente, Proveedor, Empleado,
    DevolucionAProveedor, DevolucionAProveedorDetalle,
    CuentaACobrar, Cobro, CobroDetalle  # NUEVOS MODELOS AÑADIDOS
)
from django.core.exceptions import ObjectDoesNotExist

# Configurar el logger
logger = logging.getLogger(__name__)

# Definición de acciones de auditoría (para estandarización)
ACCION_CREACION = 'CREACIÓN'
ACCION_MODIFICACION = 'MODIFICACIÓN'
ACCION_ELIMINACION = 'ELIMINACIÓN'
ACCION_PROCESADO = 'PROCESADO'
ACCION_COMPLETADO = 'COMPLETADO'


# ====================================================================
# -------------------- UTILIDADES Y AUDITORÍA --------------------
# ====================================================================

class DecimalEncoder(json.JSONEncoder):
    """Serializa objetos Decimal a str() para mantener la precisión total."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)

def get_current_user_or_none():
    """Devuelve el usuario actual o None."""
    user = get_current_user()
    return user if user and getattr(user, 'is_authenticated', False) else None

def obtener_diferencias(original_dict, nuevo_dict):
    """Calcula las diferencias entre dos diccionarios (antes/despues)."""
    diffs = {}
    for k, v in nuevo_dict.items():
        if original_dict.get(k) != v:
            diffs[k] = {'antes': original_dict.get(k), 'despues': v}
    return diffs

def auditar(instancia, accion, datos_anteriores=None, datos_nuevos=None):
    """
    Registra una acción de auditoría. 
    Aísla la operación para que un fallo en la auditoría no interrumpa la transacción principal.
    """
    try:
        usuario = get_current_user_or_none()
        registro_id = getattr(instancia, 'pk', None) or getattr(instancia, '_original_pk', None)

        # Serializar los datos
        datos_anteriores_json = json.dumps(datos_anteriores, cls=DecimalEncoder) if datos_anteriores else None
        
        # En lugar de usar datos_nuevos como campo separado, lo guardamos como texto o
        # combinamos con datos_anteriores en el JSON si es necesario
        datos_completos = None
        
        if datos_anteriores_json or datos_nuevos:
            datos_completos = {
                'anteriores': datos_anteriores,
                'nuevos': datos_nuevos
            }
            datos_completos_json = json.dumps(datos_completos, cls=DecimalEncoder)
        else:
            datos_completos_json = None
            
        if accion == ACCION_CREACION and not datos_completos_json:
            datos_completos = {'nuevos': model_to_dict(instancia)}
            datos_completos_json = json.dumps(datos_completos, cls=DecimalEncoder)
        elif accion == ACCION_ELIMINACION and not datos_completos_json:
            datos_completos = {'anteriores': model_to_dict(instancia)}
            datos_completos_json = json.dumps(datos_completos, cls=DecimalEncoder)

        Auditoria.objects.create(
            usuario=usuario,
            accion=accion,
            modelo_afectado=instancia.__class__.__name__,
            registro_id=registro_id,
            datos_anteriores=datos_completos_json  # Guardamos ambos en el mismo campo
        )
        
    except Exception as e:
        registro_id = getattr(instancia, 'pk', 'N/A')
        logger.error(f"Fallo al registrar auditoría para {instancia.__class__.__name__} (ID: {registro_id}, Acción: {accion}): {e}", exc_info=True)

def actualizar_estado_cuenta_cobrar(cuenta):
    """
    Actualiza el estado de una cuenta por cobrar automáticamente.
    Se llama desde signals de CuentaACobrar y CobroDetalle.
    """
    hoy = timezone.now().date()
    
    # Si no hay monto pendiente o es negativo (por si acaso), está pagada
    if cuenta.monto_pendiente <= 0:
        nuevo_estado = 'Pagada'
    # Si tiene monto pendiente y fecha pasada, está vencida
    elif cuenta.fecha_vencimiento < hoy:
        nuevo_estado = 'Vencida'
    else:
        nuevo_estado = 'Pendiente'
    
    # Solo actualizar si cambió el estado
    if cuenta.estado != nuevo_estado:
        cuenta.estado = nuevo_estado
        cuenta.save(update_fields=['estado'])


def registrar_movimiento(producto, tipo, cantidad, descripcion):
    """
    Crea un movimiento de inventario y actualiza stock en BD.
    Usa select_for_update() para prevenir race conditions en SALIDA.
    """
    
    cantidad_op = Decimal(cantidad) 

    if tipo == 'ENTRADA':
        Producto.objects.filter(pk=producto.pk).update(stock=F('stock') + cantidad_op)
    elif tipo == 'SALIDA':
        # Bloquear y obtener el stock actual (select_for_update)
        try:
            producto_db = Producto.objects.select_for_update().get(pk=producto.pk)
        except ObjectDoesNotExist:
             raise ValueError(f"Producto con ID {producto.pk} no encontrado para la operación.")
        
        current_stock = producto_db.stock

        if current_stock < cantidad_op:
            logger.error(f"Stock negativo fallido. Producto: {producto.pk}, Stock: {current_stock}, Salida: {cantidad_op}. Desc: {descripcion}. Usr: {get_current_user_or_none()}")
            raise ValueError(f"Stock insuficiente para el producto {producto_db.nombre}. Disponible: {current_stock}, Requerido: {cantidad_op}")

        # Si hay suficiente stock, se actualiza
        Producto.objects.filter(pk=producto.pk).update(stock=F('stock') - cantidad_op)
    else:
        logger.error(f"Tipo de movimiento desconocido: {tipo} para producto {producto.pk}")
        raise ValueError(f"Tipo de movimiento desconocido: {tipo}")

    InventarioMovimiento.objects.create(
        producto=producto,
        tipo=tipo,
        cantidad=cantidad,
        descripcion=descripcion
    )

def actualizar_total(obj, detalle_set_name):
    """
    Calcula y actualiza el campo total de la cabecera usando aggregate(Sum).
    """
    
    manager = getattr(obj, detalle_set_name)
    
    if detalle_set_name == 'devolucionaproveedordetalle_set':
        sum_field = 'monto_devuelto'
    else:
        sum_field = 'subtotal'

    # Calcular la suma en la DB
    total_sum = manager.aggregate(total=Sum(sum_field))['total'] or Decimal('0.00')

    # Actualizar la cabecera (update() para evitar signals)
    obj.__class__.objects.filter(pk=obj.pk).update(total=total_sum)


def actualizar_detalle_stock(instance, original=None, es_compra=True):
    """Gestiona el stock y el total de cabecera para detalles de Compra/Venta."""
    producto = instance.producto

    MOV_MAP = {
        True: {'NEW': 'ENTRADA', 'DEL': 'SALIDA', 'ADJ_POS': 'ENTRADA', 'ADJ_NEG': 'SALIDA'}, 
        False: {'NEW': 'SALIDA', 'DEL': 'ENTRADA', 'ADJ_POS': 'SALIDA', 'ADJ_NEG': 'ENTRADA'}
    }

    if original:
        diferencia = instance.cantidad - original.cantidad
        if diferencia == 0:
            obj = instance.compra if es_compra else instance.venta
            actualizar_total(obj, 'detallecompra_set' if es_compra else 'detalleventa_set')
            return

        tipo_mov_key = 'ADJ_POS' if diferencia > 0 else 'ADJ_NEG'
        tipo_mov = MOV_MAP[es_compra][tipo_mov_key]
        cantidad_cambio = abs(diferencia)
        descripcion = f"{'Compra' if es_compra else 'Venta'} N°{instance.compra.pk if es_compra else instance.venta.pk} - Modificación de línea (Ajuste stock)"
    else:
        cantidad_cambio = instance.cantidad
        tipo_mov = MOV_MAP[es_compra]['NEW']
        descripcion = f"{'Compra' if es_compra else 'Venta'} N°{instance.compra.pk if es_compra else instance.venta.pk} - Nueva línea (Ajuste stock)"

    registrar_movimiento(producto, tipo_mov, cantidad_cambio, descripcion)
    
    obj = instance.compra if es_compra else instance.venta
    actualizar_total(obj, 'detallecompra_set' if es_compra else 'detalleventa_set')


# ====================================================================
# -------------------- PRE_SAVE: CAPTURA DE ESTADO --------------------
# ====================================================================

AUDITED_MODELS_SIMPLE = [Cliente, Proveedor, Producto, Empleado]
AUDITED_MODELS_CABECERA = [Ajuste, Compra, Venta, DevolucionAProveedor, CuentaACobrar]  # AÑADIDO CuentaACobrar

def make_original_simple_signal(modelo):
    """Función fábrica para prevenir el problema de late binding."""
    @receiver(pre_save, sender=modelo, dispatch_uid=f"pre_save_{modelo.__name__}_simple")
    def guardar_original_simple(sender, instance, **kwargs):
        if instance.pk:
            try:
                instance._original_dict = model_to_dict(sender.objects.get(pk=instance.pk)) 
            except sender.DoesNotExist:
                instance._original_dict = None
        else:
            instance._original_dict = None
    return guardar_original_simple

# Conexión de señales para modelos simples
for modelo in AUDITED_MODELS_SIMPLE + AUDITED_MODELS_CABECERA:
    make_original_simple_signal(modelo)

@receiver(pre_save, sender=DetalleCompra)
@receiver(pre_save, sender=DetalleVenta)
@receiver(pre_save, sender=DevolucionAProveedorDetalle)
@receiver(pre_save, sender=CobroDetalle)  # NUEVA SEÑAL
def guardar_original_detalle(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._original = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._original = None
    else:
        instance._original = None

# Solo guardamos el estado original para la lógica de stock en post_save
@receiver(pre_save, sender=Ajuste)
@receiver(pre_save, sender=DevolucionAProveedor) 
@receiver(pre_save, sender=Compra)
@receiver(pre_save, sender=Venta)
def guardar_estado_original_cabecera(sender, instance, **kwargs):
    if instance.pk:
        try:
            original = sender.objects.get(pk=instance.pk)
            instance._estado_original = original.estado
            instance._original_pk = original.pk
        except sender.DoesNotExist:
            instance._estado_original = None
            instance._original_pk = None
    else:
        instance._estado_original = None
        instance._original_pk = None

# ====================================================================
# -------------------- CUENTAS POR COBRAR: SEÑALES ESPECÍFICAS --------------------
# ====================================================================

@receiver(pre_save, sender=CuentaACobrar)
def pre_save_cuenta_cobrar(sender, instance, **kwargs):
    """
    Pre-save para CuentaACobrar.
    - Captura estado original
    - Auto-calcula monto_pendiente si no se especifica
    """
    if instance.pk:
        try:
            instance._original = sender.objects.get(pk=instance.pk)
            instance._estado_original = instance._original.estado
            instance._original_pk = instance.pk
        except sender.DoesNotExist:
            instance._original = None
            instance._estado_original = None
            instance._original_pk = None
    else:
        instance._original = None
        instance._estado_original = None
        instance._original_pk = None
    
    # Auto-calcular monto_pendiente si está vacío al crear
    if not instance.pk and (not instance.monto_pendiente or instance.monto_pendiente == 0):
        instance.monto_pendiente = instance.monto_original

@receiver(post_save, sender=CuentaACobrar)
def post_save_cuenta_cobrar(sender, instance, created, **kwargs):
    """
    Post-save para CuentaACobrar.
    - Actualiza estado automáticamente
    - Registra auditoría
    """
    try:
        with transaction.atomic():
            # Auditoría
            if created:
                auditar(instance, ACCION_CREACION)
            else:
                # Solo auditar si hubo cambios (excluyendo actualizaciones automáticas de estado)
                original = getattr(instance, '_original', None)
                if original:
                    cambios = obtener_diferencias(
                        model_to_dict(original), 
                        model_to_dict(instance)
                    )
                    # Excluir cambios automáticos de estado
                    if 'estado' in cambios:
                        del cambios['estado']
                    
                    if cambios:
                        auditar(instance, ACCION_MODIFICACION, 
                               datos_anteriores=model_to_dict(original), 
                               datos_nuevos=model_to_dict(instance))
            
            # Auto-actualizar estado si se creó o se modificaron campos relevantes
            if created or (instance._estado_original != instance.estado):
                actualizar_estado_cuenta_cobrar(instance)
                
    except Exception as e:
        logger.error(f"Error post_save CuentaACobrar {instance.pk}. Usr: {get_current_user_or_none()}", exc_info=True)

@receiver(post_delete, sender=CuentaACobrar)
def post_delete_cuenta_cobrar(sender, instance, **kwargs):
    """Audita la eliminación de una cuenta por cobrar."""
    auditar(instance, ACCION_ELIMINACION)

# ====================================================================
# -------------------- COBROS DETALLE: SEÑALES ESPECÍFICAS --------------------
# ====================================================================

@receiver(post_save, sender=CobroDetalle)
def post_save_cobro_detalle(sender, instance, created, **kwargs):
    """
    Maneja la lógica cuando se registra o modifica un pago.
    - Actualiza monto pendiente de la cuenta
    - Actualiza estado de la cuenta
    """
    try:
        with transaction.atomic():
            cuenta = instance.cuenta_a_cobrar
            original = getattr(instance, '_original', None)
            
            if created:
                # NUEVO PAGO: restar del monto pendiente
                CuentaACobrar.objects.filter(pk=cuenta.pk).update(
                    monto_pendiente=F('monto_pendiente') - instance.monto_aplicado
                )
                cuenta.refresh_from_db()
                
                # Actualizar estado de la cuenta
                actualizar_estado_cuenta_cobrar(cuenta)
                
                # Auditoría del pago
                auditar(instance, ACCION_CREACION)
                
            elif original:
                # PAGO MODIFICADO: ajustar diferencia
                diferencia = instance.monto_aplicado - original.monto_aplicado
                if diferencia != 0:
                    CuentaACobrar.objects.filter(pk=cuenta.pk).update(
                        monto_pendiente=F('monto_pendiente') - diferencia
                    )
                    cuenta.refresh_from_db()
                    
                    # Actualizar estado de la cuenta
                    actualizar_estado_cuenta_cobrar(cuenta)
                
                # Auditoría de modificación
                cambios = obtener_diferencias(
                    model_to_dict(original), 
                    model_to_dict(instance)
                )
                if cambios:
                    auditar(instance, ACCION_MODIFICACION,
                           datos_anteriores=model_to_dict(original),
                           datos_nuevos=model_to_dict(instance))
                
    except Exception as e:
        logger.error(f"Error post_save CobroDetalle {instance.pk}. Usr: {get_current_user_or_none()}", exc_info=True)

@receiver(post_delete, sender=CobroDetalle)
def post_delete_cobro_detalle(sender, instance, **kwargs):
    """
    Revierte un pago cuando se elimina.
    - Suma el monto al pendiente
    - Actualiza estado de la cuenta
    """
    try:
        with transaction.atomic():
            cuenta = instance.cuenta_a_cobrar
            
            # REVERTIR EL PAGO: sumar al monto pendiente
            CuentaACobrar.objects.filter(pk=cuenta.pk).update(
                monto_pendiente=F('monto_pendiente') + instance.monto_aplicado
            )
            cuenta.refresh_from_db()
            
            # Actualizar estado de la cuenta
            actualizar_estado_cuenta_cobrar(cuenta)
            
            # Auditoría
            auditar(instance, ACCION_ELIMINACION)
            
    except Exception as e:
        logger.error(f"Error post_delete CobroDetalle {instance.pk}. Usr: {get_current_user_or_none()}", exc_info=True)

# ====================================================================
# -------------------- CREACIÓN AUTOMÁTICA DE CUENTAS DESDE VENTAS --------------------
# ====================================================================

@receiver(post_save, sender=Venta)
def crear_cuenta_cobrar_desde_venta(sender, instance, created, **kwargs):
    """
    Crea automáticamente una cuenta por cobrar para ventas a crédito.
    Se ejecuta después de que una venta es creada o su estado cambia.
    """
    estado_original = getattr(instance, '_estado_original', 'PENDIENTE')
    
    # Condiciones para crear cuenta:
    # 1. Venta a crédito Y
    # 2. Estado es FINALIZADA/COMPLETADA Y
    # 3. No existe ya una cuenta para esta venta Y
    # 4. (Creación nueva O cambio de estado a completada)
    
    condiciones_credito = hasattr(instance, 'tipo_pago') and instance.tipo_pago == 'CREDITO'
    condiciones_estado = instance.estado in ['FINALIZADA', 'COMPLETADA']
    condiciones_creacion = created or (estado_original not in ['FINALIZADA', 'COMPLETADA'] and condiciones_estado)
    
    if condiciones_credito and condiciones_estado and condiciones_creacion:
        try:
            # Verificar si ya existe una cuenta para esta venta
            cuenta_existente = CuentaACobrar.objects.filter(venta=instance).exists()
            
            if not cuenta_existente:
                with transaction.atomic():
                    # Calcular fecha de vencimiento (30 días por defecto)
                    fecha_vencimiento = instance.fecha_venta + timezone.timedelta(days=30)
                    
                    cuenta = CuentaACobrar.objects.create(
                        cliente=instance.cliente,
                        venta=instance,
                        fecha_vencimiento=fecha_vencimiento,
                        monto_original=instance.total,
                        monto_pendiente=instance.total,
                        estado='Pendiente',
                        descripcion=f'Cuenta generada automáticamente desde Venta #{instance.id} - {instance.descripcion or "Sin descripción"}'
                    )
                    logger.info(f'Cuenta por cobrar #{cuenta.id} creada automáticamente desde Venta #{instance.id}')
        except Exception as e:
            logger.error(f"Error al crear cuenta desde venta #{instance.id}: {e}", exc_info=True)

# ====================================================================
# -------------------- POST_SAVE/DELETE: DETALLES --------------------
# ====================================================================

def handle_detalle_post_save(sender, instance, created, es_compra=False, es_devolucion=False):
    """Manejo común para DetalleCompra, DetalleVenta y DetalleDevolucion."""
    try:
        with transaction.atomic():
            original = getattr(instance, '_original', None)
            
            # Mapeo
            if es_compra:
                cabecera = instance.compra
                detalle_set_name = 'detallecompra_set'
            elif not es_devolucion:
                cabecera = instance.venta
                detalle_set_name = 'detalleventa_set'
            else:
                cabecera = instance.devolucionaproveedor
                detalle_set_name = 'devolucionaproveedordetalle_set'
            
            # Lógica de Stock/Total
            if not es_devolucion: 
                if cabecera.estado in [ACCION_COMPLETADO, ACCION_PROCESADO]:
                    actualizar_detalle_stock(instance, original, es_compra=es_compra)
                else:
                    actualizar_total(cabecera, detalle_set_name)
            else: 
                actualizar_total(cabecera, detalle_set_name)


            # Auditoría
            if created:
                auditar(instance, ACCION_CREACION)
            elif original:
                cambios = obtener_diferencias(model_to_dict(original), model_to_dict(instance))
                if cambios:
                    auditar(instance, ACCION_MODIFICACION, model_to_dict(original), model_to_dict(instance))
    except Exception as e:
        logger.error(f"Error post_save Detalle {getattr(instance, 'pk', 'new')} en {sender.__name__}. Usr: {get_current_user_or_none()}", exc_info=True)

@receiver(post_save, sender=DetalleCompra)
def post_save_detalle_compra(sender, instance, created, **kwargs):
    handle_detalle_post_save(sender, instance, created, es_compra=True, es_devolucion=False)

@receiver(post_save, sender=DetalleVenta)
def post_save_detalle_venta(sender, instance, created, **kwargs):
    handle_detalle_post_save(sender, instance, created, es_compra=False, es_devolucion=False)

@receiver(post_save, sender=DevolucionAProveedorDetalle)
def post_save_detalle_devolucion(sender, instance, created, **kwargs):
    handle_detalle_post_save(sender, instance, created, es_compra=False, es_devolucion=True) 

@receiver(post_delete, sender=DetalleCompra)
def post_delete_detalle_compra(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            registrar_movimiento(instance.producto, 'SALIDA', instance.cantidad, 
                                 descripcion=f"Anulación línea Compra N°{instance.compra.pk}")
            actualizar_total(instance.compra, 'detallecompra_set')
            auditar(instance, ACCION_ELIMINACION)
    except Exception as e:
        logger.error(f"Error post_delete DetalleCompra {instance.pk}. Usr: {get_current_user_or_none()}", exc_info=True)

@receiver(post_delete, sender=DetalleVenta)
def post_delete_detalle_venta(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            registrar_movimiento(instance.producto, 'ENTRADA', instance.cantidad, 
                                 descripcion=f"Anulación línea Venta N°{instance.venta.pk}")
            actualizar_total(instance.venta, 'detalleventa_set')
            auditar(instance, ACCION_ELIMINACION)
    except Exception as e:
        logger.error(f"Error post_delete DetalleVenta {instance.pk}. Usr: {get_current_user_or_none()}", exc_info=True)

@receiver(post_delete, sender=DevolucionAProveedorDetalle)
def post_delete_detalle_devolucion(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            actualizar_total(instance.devolucionaproveedor, 'devolucionaproveedordetalle_set')
            auditar(instance, ACCION_ELIMINACION)
    except Exception as e:
        logger.error(f"Error post_delete DetalleDevolucion {instance.pk}. Usr: {get_current_user_or_none()}", exc_info=True)


# ====================================================================
# -------------------- POST_SAVE: CABECERAS DE PROCESO --------------------
# ====================================================================

@receiver(post_save, sender=Ajuste)
def post_save_ajuste(sender, instance, **kwargs):
    estado_original = getattr(instance, '_estado_original', 'Pendiente')
    
    if estado_original != ACCION_PROCESADO and instance.estado == ACCION_PROCESADO:
        try:
            with transaction.atomic():
                es_entrada = instance.tipo_ajuste.es_entrada
                for detalle in instance.ajustedetalle_set.all():
                    producto = detalle.producto
                    cantidad = detalle.cantidad
                    tipo_mov = 'ENTRADA' if es_entrada else 'SALIDA'
                    registrar_movimiento(producto, tipo_mov, cantidad,
                                         descripcion=f"Ajuste #{instance.pk} - Tipo: {instance.tipo_ajuste.nombre}")
                auditar(instance, ACCION_PROCESADO, datos_nuevos={'estado': ACCION_PROCESADO}) 
        except Exception as e:
            logger.error(f"Error al procesar Ajuste N°{instance.pk}. Usr: {get_current_user_or_none()}", exc_info=True)


@receiver(post_save, sender=DevolucionAProveedor)
def post_save_devolucion_proveedor(sender, instance, **kwargs):
    estado_original = getattr(instance, '_estado_original', 'Pendiente')
    
    if estado_original != ACCION_COMPLETADO and instance.estado == ACCION_COMPLETADO:
        try:
            with transaction.atomic():
                for detalle in instance.devolucionaproveedordetalle_set.all():
                    registrar_movimiento(detalle.producto, 'SALIDA', detalle.cantidad,
                                         descripcion=f"Devolución Proveedor #{instance.pk} a {instance.proveedor.nombre}")

                actualizar_total(instance, 'devolucionaproveedordetalle_set')
                instance.refresh_from_db()
                auditar(instance, ACCION_COMPLETADO, datos_nuevos={'estado': ACCION_COMPLETADO, 'total_devuelto': instance.total_devuelto})
        except Exception as e:
            logger.error(f"Error al procesar Devolución Proveedor N°{instance.pk}. Usr: {get_current_user_or_none()}", exc_info=True)


@receiver(post_save, sender=Compra)
def post_save_compra(sender, instance, **kwargs):
    estado_original = getattr(instance, '_estado_original', 'PENDIENTE') 
    
    # 1. Lógica de Stock / Cambio de Estado
    if estado_original != ACCION_COMPLETADO and instance.estado == ACCION_COMPLETADO:
        try:
            with transaction.atomic():
                for detalle in instance.detallecompra_set.all():
                    producto = detalle.producto
                    registrar_movimiento(producto, 'ENTRADA', detalle.cantidad,
                                         descripcion=f"Compra #{instance.pk} a {instance.proveedor.nombre}")

                    # Actualiza el precio de compra del producto
                    Producto.objects.filter(pk=producto.pk).update(
                        precio_compra=detalle.precio_compra
                    )
                    
                actualizar_total(instance, 'detallecompra_set')
                instance.refresh_from_db()
                
                # CORRECCIÓN: Pasar ambos datos en datos_anteriores
                datos_cambio = {
                    'estado': ACCION_COMPLETADO,
                    'total': str(instance.total)
                }
                auditar(instance, ACCION_COMPLETADO, datos_anteriores=datos_cambio)
        except Exception as e:
            logger.error(f"Error al procesar Compra N°{instance.pk}. Usr: {get_current_user_or_none()}", exc_info=True)
    
    # 2. Auditoría de Modificación (Manejador Genérico) - Ver sección de Auditoría Genérica


@receiver(post_save, sender=Venta)
def post_save_venta(sender, instance, **kwargs):
    estado_original = getattr(instance, '_estado_original', 'PENDIENTE') 
    
    # 1. Lógica de Stock / Cambio de Estado
    if estado_original not in [ACCION_COMPLETADO, ACCION_PROCESADO] and instance.estado in [ACCION_COMPLETADO, ACCION_PROCESADO]:
        try:
            with transaction.atomic():
                detalles = instance.detalleventa_set.select_related('producto').all()
                
                for detalle in detalles:
                    registrar_movimiento(detalle.producto, 'SALIDA', detalle.cantidad,
                                         descripcion=f"Venta #{instance.pk} a {instance.cliente.nombre}")
                    
                actualizar_total(instance, 'detalleventa_set')
                instance.refresh_from_db()
                auditar(instance, instance.estado, datos_nuevos={'estado': instance.estado, 'total': instance.total})
        except ValueError as ve:
            logger.error(f"Fallo de stock al procesar Venta N°{instance.pk}: {ve}. Usr: {get_current_user_or_none()}")
            raise 
        except Exception as e:
            logger.error(f"Error al procesar Venta N°{instance.pk}. Usr: {get_current_user_or_none()}", exc_info=True)
            
    # 2. Auditoría de Modificación (Manejador Genérico) - Ver sección de Auditoría Genérica


# ====================================================================
# -------------------- POST_DELETE: CABECERAS (REVERSIÓN) --------------------
# ====================================================================

@receiver(post_delete, sender=Compra)
def post_delete_compra(sender, instance, **kwargs):
    """Revierte stock y movimientos al eliminar una Compra completada."""
    try:
        if instance.estado == ACCION_COMPLETADO:
            with transaction.atomic():
                for detalle in instance.detallecompra_set.select_related('producto').all():
                    registrar_movimiento(detalle.producto, 'SALIDA', detalle.cantidad,
                                         descripcion=f"ANULACIÓN COMPRA #{instance.pk} (Eliminación cabecera)")
        
        auditar(instance, ACCION_ELIMINACION)
    except Exception as e:
        logger.error(f"Error al eliminar Compra N°{instance.pk}. Usr: {get_current_user_or_none()}", exc_info=True)

@receiver(post_delete, sender=Venta)
def post_delete_venta(sender, instance, **kwargs):
    """Revierte stock y movimientos al eliminar una Venta completada."""
    try:
        if instance.estado in [ACCION_COMPLETADO, ACCION_PROCESADO]:
            with transaction.atomic():
                for detalle in instance.detalleventa_set.select_related('producto').all():
                    registrar_movimiento(detalle.producto, 'ENTRADA', detalle.cantidad,
                                         descripcion=f"ANULACIÓN VENTA #{instance.pk} (Eliminación cabecera)")
        
        auditar(instance, ACCION_ELIMINACION)
    except Exception as e:
        logger.error(f"Error al eliminar Venta N°{instance.pk}. Usr: {get_current_user_or_none()}", exc_info=True)


# ====================================================================
# -------------------- AUDITORÍA GENÉRICA (MODELOS SIMPLES Y CABECERAS) --------------------
# ====================================================================

AUDITED_MODELS_ALL = AUDITED_MODELS_SIMPLE + AUDITED_MODELS_CABECERA

@receiver(post_save, sender=Cliente)
@receiver(post_save, sender=Proveedor)
@receiver(post_save, sender=Producto)
@receiver(post_save, sender=Empleado)
@receiver(post_save, sender=Compra)
@receiver(post_save, sender=Venta)
@receiver(post_save, sender=Ajuste)
@receiver(post_save, sender=DevolucionAProveedor)
@receiver(post_save, sender=CuentaACobrar)  # NUEVO: Auditoría genérica para CuentaACobrar
def auditar_modelo_generico_post_save(sender, instance, created, **kwargs):
    """
    Función genérica para auditar Creación y Modificación de campos *simples* en todos los modelos auditados (evitando repetir el código de auditoría).
    """
    if created:
        auditar(instance, ACCION_CREACION)
    else:
        original_dict = getattr(instance, '_original_dict', None)
        # Excluimos la auditoría si el único cambio es el campo 'estado', 
        # que ya se audita por la lógica de proceso (ej: post_save_compra)
        
        if original_dict:
            # Omitimos el estado para que la auditoría genérica no se solape con la auditoría de cambio de estado
            original_dict_sin_estado = original_dict.copy()
            if 'estado' in original_dict_sin_estado:
                del original_dict_sin_estado['estado']
            
            nuevo_dict = model_to_dict(instance)
            if 'estado' in nuevo_dict:
                del nuevo_dict['estado']

            cambios = obtener_diferencias(original_dict_sin_estado, nuevo_dict)
            
            if cambios:
                auditar(instance, ACCION_MODIFICACION, datos_anteriores=original_dict, datos_nuevos=model_to_dict(instance))


@receiver(post_delete, sender=Cliente)
@receiver(post_delete, sender=Proveedor)
@receiver(post_delete, sender=Producto)
@receiver(post_delete, sender=Empleado)
@receiver(post_delete, sender=CuentaACobrar)  # NUEVO: Auditoría de eliminación para CuentaACobrar
def auditar_modelo_simple_post_delete(sender, instance, **kwargs):
    # Para cabeceras (Compra, Venta, etc.), el post_delete ya llama a auditar(ACCION_ELIMINACION)
    auditar(instance, ACCION_ELIMINACION)