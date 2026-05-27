# gestion/signals.py
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from .models import (
    # Necesarios para Compras/Ventas
    DetalleCompra, DetalleVenta, Compra, Venta,
    # Necesarios para Ajustes
    Ajuste, AjusteDetalle, AjusteTipo,
    # Comunes
    Producto, InventarioMovimiento
)

# ====================================================================
# LÓGICA DE COMPRA (DetalleCompra)
# Se dispara al crear la línea de compra (asumiendo que la compra ya fue recibida)
# ====================================================================

@receiver(post_save, sender=DetalleCompra)
def actualizar_inventario_por_compra(sender, instance, created, **kwargs):
    """
    Registra la entrada de stock y el movimiento de inventario al crear una línea de compra.
    Nota: Solo se aplica en la CREACIÓN para evitar doble impacto en ediciones.
    """
    if created:
        try:
            with transaction.atomic():
                producto = instance.producto
                cantidad_recibida = instance.cantidad
                compra = instance.compra
                
                # 1. Actualizar el Stock del Producto (Entrada)
                Producto.objects.filter(pk=producto.pk).update(
                    stock=F('stock') + cantidad_recibida
                )
                
                # 2. Registrar el Movimiento de Inventario
                InventarioMovimiento.objects.create(
                    producto=producto,
                    tipo='ENTRADA',
                    cantidad=cantidad_recibida,
                    descripcion=f"Compra N°{compra.pk}",
                    # Usamos el empleado que procesó la Compra
                    # Asegúrate de que tu modelo Compra tiene el campo 'empleado'
                    # empleado=compra.empleado 
                )
                
                # 3. Actualizar el Total de la Compra
                compra.total = sum(d.subtotal for d in compra.detallecompra_set.all())
                compra.save(update_fields=['total'])
        
        except Exception as e:
            print(f"Error crítico al actualizar inventario para DetalleCompra {instance.pk}: {e}")

@receiver(post_delete, sender=DetalleCompra)
def devolver_stock_por_eliminacion_compra(sender, instance, **kwargs):
    """Devuelve el stock y ajusta el total de la compra al eliminar un detalle."""
    try:
        with transaction.atomic():
            producto = instance.producto
            compra = instance.compra
            
            # 1. Devolver Stock (Salida)
            Producto.objects.filter(pk=producto.pk).update(
                stock=F('stock') - instance.cantidad
            )
            
            # 2. Registrar el Movimiento (Contrario)
            InventarioMovimiento.objects.create(
                producto=producto,
                tipo='SALIDA',
                cantidad=instance.cantidad,
                descripcion=f"Anulación de línea Compra N°{compra.pk}"
            )
            
            # 3. Actualizar el Total de la Compra
            compra.total = sum(d.subtotal for d in compra.detallecompra_set.all())
            compra.save(update_fields=['total'])
            
    except Exception as e:
        print(f"Error al eliminar DetalleCompra {instance.pk}: {e}")


# ====================================================================
# LÓGICA DE VENTA (DetalleVenta)
# ====================================================================

@receiver(post_save, sender=DetalleVenta)
def actualizar_inventario_por_venta(sender, instance, created, **kwargs):
    """Registra la salida de stock y el movimiento de inventario al crear una línea de venta."""
    if created:
        try:
            with transaction.atomic():
                producto = instance.producto
                cantidad_vendida = instance.cantidad
                venta = instance.venta
                
                # 1. Actualizar el Stock del Producto (Salida)
                Producto.objects.filter(pk=producto.pk).update(
                    stock=F('stock') - cantidad_vendida
                )
                
                # 2. Registrar el Movimiento de Inventario
                InventarioMovimiento.objects.create(
                    producto=producto,
                    tipo='SALIDA',
                    cantidad=cantidad_vendida,
                    descripcion=f"Venta N°{venta.pk}",
                    # Asegúrate de que tu modelo Venta tiene el campo 'empleado'
                    # empleado=venta.empleado 
                )
                
                # 3. Actualizar el Total de la Venta
                venta.total = sum(d.subtotal for d in venta.detalleventa_set.all())
                venta.save(update_fields=['total'])
        
        except Exception as e:
            print(f"Error crítico al actualizar inventario para DetalleVenta {instance.pk}: {e}")


@receiver(post_delete, sender=DetalleVenta)
def devolver_stock_por_eliminacion_venta(sender, instance, **kwargs):
    """Devuelve el stock y ajusta el total de la venta al eliminar un detalle."""
    try:
        with transaction.atomic():
            producto = instance.producto
            venta = instance.venta
            
            # 1. Devolver Stock (Entrada)
            Producto.objects.filter(pk=producto.pk).update(
                stock=F('stock') + instance.cantidad
            )
            
            # 2. Registrar el Movimiento (Contrario)
            InventarioMovimiento.objects.create(
                producto=producto,
                tipo='ENTRADA',
                cantidad=instance.cantidad,
                descripcion=f"Anulación de línea Venta N°{venta.pk}"
            )
            
            # 3. Actualizar el Total de la Venta
            venta.total = sum(d.subtotal for d in venta.detalleventa_set.all())
            venta.save(update_fields=['total'])
            
    except Exception as e:
        print(f"Error al eliminar DetalleVenta {instance.pk}: {e}")


# ====================================================================
# LÓGICA DE AJUSTES DE INVENTARIO (Ajuste)
# Se dispara SOLO al pasar el estado de PENDIENTE a PROCESADO
# ====================================================================

@receiver(pre_save, sender=Ajuste)
def guardar_estado_original(sender, instance, **kwargs):
    """Guarda el estado actual del Ajuste antes de que se guarde el nuevo."""
    if instance.pk:
        try:
            original = sender.objects.get(pk=instance.pk)
            instance._estado_original = original.estado
        except sender.DoesNotExist:
            instance._estado_original = None

@receiver(post_save, sender=Ajuste)
def aplicar_ajuste_a_inventario(sender, instance, **kwargs):
    """
    Aplica el impacto del ajuste al inventario y crea los movimientos,
    solo si el estado cambia de 'Pendiente' a 'PROCESADO'.
    """
    estado_original = getattr(instance, '_estado_original', 'Pendiente')
    
    #  Condición CLAVE: Ejecutar solo si el estado es PROCESADO y el original era Pendiente
    if estado_original == 'Pendiente' and instance.estado == 'PROCESADO':
        try:
            with transaction.atomic():
                # 1. Recuperamos si es Entrada o Salida
                es_entrada = instance.tipo_ajuste.es_entrada
                
                # 2. Iteramos sobre todos los detalles del ajuste
                for detalle in instance.ajustedetalle_set.all():
                    producto = detalle.producto
                    cantidad_ajuste = detalle.cantidad
                    
                    tipo_movimiento = 'ENTRADA' if es_entrada else 'SALIDA'
                    
                    # 3. Actualizar el Stock del Producto
                    if es_entrada:
                        Producto.objects.filter(pk=producto.pk).update(
                            stock=F('stock') + cantidad_ajuste
                        )
                    else:
                        Producto.objects.filter(pk=producto.pk).update(
                            stock=F('stock') - cantidad_ajuste
                        )
                    
                    # 4. Crear el registro de InventarioMovimiento
                    InventarioMovimiento.objects.create(
                        producto=producto,
                        tipo=tipo_movimiento,
                        cantidad=cantidad_ajuste,
                        descripcion=f'Ajuste #{instance.id} - Tipo: {instance.tipo_ajuste.nombre}',
                        # empleado=instance.empleado # Usamos el empleado de la cabecera
                    )
        except Exception as e:
            print(f"Error al procesar el Ajuste N°{instance.pk}: {e}")

