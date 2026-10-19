from django.contrib import admin

from .models import IntentoPago


@admin.register(IntentoPago)
class IntentoPagoAdmin(admin.ModelAdmin):
    list_display = ("buy_order", "order", "status", "amount", "currency", "created_at")
    list_filter = ("status", "currency")
    search_fields = ("buy_order", "token_ws", "order__id")
    readonly_fields = ("id", "created_at", "updated_at")