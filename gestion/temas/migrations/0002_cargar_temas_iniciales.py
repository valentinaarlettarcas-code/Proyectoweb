from django.db import migrations

TEMAS = [
    ('tema-1', 'Tema 1'),
    ('tema-2', 'Tema 2'),
    ('tema-3', 'Tema 3'),
    ('tema-4', 'Tema 4'),
]


def cargar_temas(apps, schema_editor):
    Tema = apps.get_model('temas', 'Tema')
    for identificador, nombre in TEMAS:
        Tema.objects.get_or_create(
            identificador=identificador,
            defaults={'nombre': nombre},
        )


class Migration(migrations.Migration):

    dependencies = [
        ('temas', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(cargar_temas, migrations.RunPython.noop),
    ]