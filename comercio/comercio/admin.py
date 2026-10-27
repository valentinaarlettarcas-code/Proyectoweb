
from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "producto_id",
        "historical_product_name",
        "historical_price",
        "moneda",
        "quantity",
        "subtotal",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cliente_id",
        "status",
        "total_amount",
        "moneda",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("checkout_id",)
    readonly_fields = (
        "cliente_id",
        "checkout_id",
        "total_amount",
        "moneda",
<<<<<<< HEAD
        "created_at",
=======
        "created_at"
>>>>>>> origin/main
    )
    inlines = [OrderItemInline]

