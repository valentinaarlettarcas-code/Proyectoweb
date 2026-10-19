from django.contrib import admin

from .models import IntentoPago, Orden


@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ("id", "cliente_id", "estado", "moneda", "total", "creado_en")
    list_filter = ("estado",)
    search_fields = ("id", "cliente_id", "reserva_id")
    readonly_fields = ("id", "creado_en", "actualizado_en")


@admin.register(IntentoPago)
class IntentoPagoAdmin(admin.ModelAdmin):
    list_display = ("buy_order", "orden", "estado", "amount", "currency", "creado_en")
    list_filter = ("estado", "currency")
    search_fields = ("buy_order", "token_ws", "orden__id")
    readonly_fields = ("id", "creado_en", "actualizado_en")
