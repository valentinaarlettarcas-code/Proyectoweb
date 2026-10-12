from django.contrib import admin
from .models import Order, OrderItem

class LineaDeOrdenInline(admin.TabularInline):
    """
    Permite ver los productos comprados directamente dentro de la vista de la orden.
    """
    model = OrderItem
    extra = 0
    # Estos campos solo se muestran como solo lectura
    readonly_fields = ('producto_id', 'historical_product_name', 'historical_price', 'moneda', 'quantity', 'subtotal')


@admin.register(Order)
class AdministradorDeOrdenes(admin.ModelAdmin):
    """
    Configuración del panel de administración para las Órdenes.
    """
    # Columnas que se verán en la lista principal 
    list_display = ('id', 'cliente_id', 'status', 'total_amount', 'moneda', 'created_at')
    
    # Filtros para buscar por estado o fecha
    list_filter = ('status', 'created_at')
    
    # Barra de búsqueda para buscar por cliente o checkout
    search_fields = ('cliente_id', 'checkout_id')
    
    # Campos que no deben poder modificar por seguridad
    readonly_fields = ('cliente_id', 'checkout_id', 'total_amount', 'moneda', 'created_at', 'updated_at')
    
    # Agrega la lista de productos dentro de la vista de la orden
    inlines = [LineaDeOrdenInline]