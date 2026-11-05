from django.db import migrations

NOMBRES = {
    'tema-1': 'Medianoche',
    'tema-2': 'Violeta el\u00e9ctrico',
    'tema-3': 'Cielo tech',
    'tema-4': 'Lavanda',
}


def renombrar(apps, schema_editor):
    Tema = apps.get_model('temas', 'Tema')
    for identificador, nombre in NOMBRES.items():
        Tema.objects.filter(identificador=identificador).update(nombre=nombre)


def revertir(apps, schema_editor):
    Tema = apps.get_model('temas', 'Tema')
    for identificador in NOMBRES:
        numero = identificador.split('-')[1]
        Tema.objects.filter(identificador=identificador).update(nombre=f'Tema {numero}')


class Migration(migrations.Migration):

    dependencies = [
        ('temas', '0002_cargar_temas_iniciales'),
    ]

    operations = [
        migrations.RunPython(renombrar, revertir),
    ]