
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name="ID",
                )),
                ("cliente_id", models.PositiveIntegerField(
                    help_text="ID del cliente en el servicio de Gestión"
                )),
                ("checkout_id", models.CharField(max_length=255, unique=True)),
                ("status", models.CharField(
                    choices=[
                        ("PENDIENTE_PAGO", "Pendiente de pago"),
                        ("CONFIRMACION_PENDIENTE", "Confirmación pendiente"),
                        ("CONFIRMADA", "Confirmada"),
                        ("RECHAZADA", "Rechazada"),
                        ("CANCELADA", "Cancelada"),
                        ("VENCIDA", "Vencida"),
                        ("REVISION_REQUERIDA", "Revisión requerida"),
                    ],
                    default="PENDIENTE_PAGO",
                    max_length=30,
                )),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("moneda", models.CharField(default="CLP", max_length=3)),
                ("total_amount", models.DecimalField(
                    decimal_places=0, default=0, max_digits=12
                )),
            ],
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                ("id", models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name="ID",
                )),
                ("producto_id", models.CharField(max_length=255)),
                ("historical_product_name", models.CharField(max_length=255)),
                ("historical_price", models.DecimalField(
                    decimal_places=0, max_digits=12
                )),
                ("moneda", models.CharField(default="CLP", max_length=3)),
                ("quantity", models.PositiveIntegerField(default=1)),
                ("subtotal", models.DecimalField(
                    decimal_places=0, max_digits=12
                )),
                ("order", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="items",
                    to="comercio.order",
                )),
            ],
        ),
    ]
